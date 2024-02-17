# Chuck Norris Jokes Web Application

This web application allows users to generate and view Chuck Norris jokes. Users can generate random Chuck Norris jokes and view their own list of jokes.

## Features

- **Generate Joke**: Click the "Generate Joke" button to generate a random Chuck Norris joke.
- **View Your List of Jokes**: Click the "Show Your List of Jokes" button to view your list of generated jokes.
- **Last Generated Joke**: The last generated joke is displayed at the top of the page.
- **User Authentication**: Users can sign up, sign in, sign in using Google Authentication and log out. Each user has their own list of jokes.
- **Database Storage**: Jokes are stored in a SQLite database.
- **Responsive Design**: The web application is responsive and works well on different devices.

## Installation

1. Clone the repository:
git clone https://github.com/codewithdani/chuck-norris-jokes.git

2. Install dependencies:
pip install -r requirements.txt

3. Set up the database:

```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)

4. Run the application:
python app.py

5. Open your web browser and navigate to `http://localhost:8000`.

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- sqlite3
- HTML/CSS
- JavaScript
- Jinja2 templating engine

## Third-Party Services Used

- Chuck Norris API (https://api.chucknorris.io) for generating jokes.
- Google Hosted Authentication (https://console.cloud.google.com/)
- render.com for deployment

### Google Authentication

Users can log-in using their Google account for authentication. This allows for a seamless sign-in experience without the need to create an additional account.

### Logout

Users can log out of their account at any time. This clears their session and logs them out of the application.

To set up with Google Authentication:

- https://console.cloud.google.com/
- Register a service with Google > create a new project (give name).
- Within the new project, go to APIs + Services > Create credentials > Configure Consent Screen > External Users > name the project again (same name) > enter user support email > leave defaults > create test users if you'd like
- Go back to dashboard > Credentials > Create Creds > OAuth Client ID > web app > define your redirect url of your web app (http://localhost:8000/callback)
- Create the call back > download your creds as a json file
- Copy this client_secret.json locally to the project repo
- Write the GOOGLE_CLIENT_ID in app.py with what's present in the client_secret.json you got from Google.

## Project Structure
- `app.py`: Main Flask application file.
- `templates/`: HTML templates for rendering pages.
- `static/`: Contains static files (e.g., CSS, JavaScript, image).
- `client_secret.json`: Contains GOOGLE_CLIENT_ID and client_secret.
- `README.md`: Provided full information about the project.
- `requirements.txt`: Contains dependencies of the project.

## Contributors

- Daniel Giday (daneximpex@gmail.com)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
This README.md file provides information about the Chuck Norris Jokes web application, including features, installation instructions, technologies used, project structure, contributors, Google Authentication, and license details. Adjust the content as needed for your specific project.
