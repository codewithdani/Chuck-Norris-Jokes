import os
import pathlib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import requests
from flask import Flask, session, abort, render_template, request, jsonify, redirect, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = "codewithdani.com"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "1096270564503-1vn9qm6nob1ddqr35jevf7r96tea8bf3.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://chuck-norris-jokes-762t.onrender.com/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if "state" in session and "state" in request.args:
        if not session["state"] == request.args["state"]:
            abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    google_id = id_info.get("sub")  # Extract Google ID
    name = id_info.get("name")
    email = id_info.get("email")

    # Check if the user already exists in the database
    user = GoogleUser.query.filter_by(google_id=google_id).first()

    if not user:
        # Create a new user record using Google account information
        new_user = GoogleUser(google_id=google_id, name=name, email=email)  # Assuming no password is required for Google-authenticated users
        db.session.add(new_user)
        db.session.commit()

    # Set user information in the session
    session["google_id"] = google_id
    session["name"] = name
    
    return redirect("/joke")

'''
# GitHub OAuth settings
GITHUB_CLIENT_ID = 'b9efcd4bf38e74b93d74'
GITHUB_CLIENT_SECRET = 'be1930cda8c586ed95e792ec14b245358a5f70dc'
GITHUB_REDIRECT_URI = 'https://chuck-norris-jokes-762t.onrender.com/github_callback'

@app.route("/github_callback")
def github_callback():
    # Get the authorization code from the request query parameters
    code = request.args.get('code')

    # Exchange the authorization code for an access token
    client = WebApplicationClient(GITHUB_CLIENT_ID)
    token_endpoint = 'https://github.com/login/oauth/access_token'
    token_params = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI
    }
    token_response = requests.post(token_endpoint, data=token_params)
    token_data = token_response.json()
    access_token = token_data.get('access_token')

    # Fetch user information using the access token
    user_endpoint = 'https://api.github.com/user'
    headers = {'Authorization': f'token {access_token}'}
    user_response = requests.get(user_endpoint, headers=headers)
    user_data = user_response.json()

    # Extract user information
    github_id = user_data.get('id')
    name = user_data.get('name')
    email = user_data.get('email')

    # Check if the user already exists in the database
    user = User.query.filter_by(github_id=github_id).first()

    if not user:
        # Create a new user record using GitHub account information
        new_user = User(github_id=github_id, name=name, email=email)  # Assuming no password is required for GitHub-authenticated users
        db.session.add(new_user)
        db.session.commit()

    # Set user information in the session
    session["github_id"] = github_id
    session["name"] = name
    
    return redirect("/joke")  # Redirect to the desired page after authentication
'''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


# Define custom filter function
def jinja2_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)

# Register the custom filter with Jinja2
app.jinja_env.filters['enumerate'] = jinja2_enumerate

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class GoogleUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)  # Add Google ID field
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Joke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joke_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    google_id = db.Column(db.String(100), db.ForeignKey('google_user.google_id'), nullable=True)  # Corrected table name reference

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', error='Account already registered.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('jokes'))
        else:
            return render_template('signin.html', error='User not found. Please register.')
    return render_template('signin.html')


@app.route('/jokes')
def jokes():
    if 'username' in session:
        user_id = User.query.filter_by(username=session['username']).first().id
        jokes = Joke.query.filter_by(user_id=user_id).all()
        joke_texts = [joke.joke_text for joke in jokes]
        return render_template('jokes.html', jokes=joke_texts)
    return redirect(url_for('index'))

@app.route('/generate_joke')
def generate_joke():
    joke_response = requests.get('https://api.chucknorris.io/jokes/random')
    joke_text = joke_response.json()['value']
    if 'username' in session:
        user_id = User.query.filter_by(username=session['username']).first().id
        new_joke = Joke(joke_text=joke_text, user_id=user_id)
    else:
        new_joke = Joke(joke_text=joke_text)
    db.session.add(new_joke)
    db.session.commit()
    
    # Get the latest joke from the database
    latest_joke = Joke.query.order_by(Joke.timestamp.desc()).first()
    
    # Get all jokes from the database
    all_jokes = Joke.query.all()

    return render_template('jokes.html', latest_joke=latest_joke, jokes=all_jokes)

@app.route('/joke')
def joke():
    if 'google_id' in session:  # Check if Google ID is in session
        google_id = session['google_id']
        user = GoogleUser.query.filter_by(google_id=google_id).first()
        if user:
            jokes = Joke.query.filter_by(google_id=google_id).all()
            joke_texts = [joke.joke_text for joke in jokes]
            return render_template('jokes.html', jokes=joke_texts)
        else:
            # Handle the case where the user is not found in the database
            return render_template('error.html', message='User not found in the database.')
    else:
        # Redirect unauthenticated users to the index route
        return redirect(url_for('index'))
    

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        message = request.form['message']
        new_feedback = Feedback(message=message)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('feedback'))
    else:
        return render_template('feedback.html')

@app.route('/view_feedback')
def view_feedback():
    feedback_messages = Feedback.query.all()
    return render_template('view_feedback.html', feedback_messages=feedback_messages)

last_joke = None

# Endpoint to generate a new Chuck Norris joke
@app.route('/generate_joke_social', methods=['GET'])
def generate_joke_social():
    # Generate new Chuck Norris joke (replace this with your actual logic)
    new_joke = "Joke.query.order_by(Joke.timestamp.desc()).first()"
    # Store the new joke as the last generated joke
    global last_joke
    last_joke = new_joke
    return jsonify({'joke': new_joke})

# Endpoint to return the last generated Chuck Norris joke
@app.route('/last_joke', methods=['GET'])
def get_last_joke():
    last_joke = Joke.query.order_by(Joke.timestamp.desc()).first()
    
    if last_joke:
        return jsonify({'joke': last_joke.joke_text})
    else:
        return jsonify({'error': 'No joke available'}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=False)