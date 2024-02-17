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
    redirect_uri="http://localhost:8000/callback"
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

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


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

class Joke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joke_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)