# Deployment Instructions

This document provides instructions on how to deploy the web application to various platforms:

## Deploying to Heroku

1. Create a Heroku account if you don't have one already.
2. Install the Heroku CLI from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
3. Login to Heroku using the command:
   ```
   heroku login
   ```
4. Navigate to your project directory and create a new Heroku app:
   ```
   heroku create your-app-name
   ```
5. Commit your changes to Git:
   ```
   git add .
   git commit -m "Prepare for deployment"
   ```
6. Deploy your app:
   ```
   git push heroku main
   ```
7. Visit your app at `https://your-app-name.herokuapp.com`.

## Deploying to PythonAnywhere

1. Create a PythonAnywhere account if you don't have one already.
2. Log in to your PythonAnywhere dashboard.
3. Click on the "Web" tab to create a new web app.
4. Choose a Python version that matches your project.
5. Set up your virtual environment and install dependencies via the Bash console:
   ```
   mkvirtualenv your-virtualenv-name
   pip install -r requirements.txt
   ```
6. Configure your web app settings to point to your WSGI file.
7. Reload your web app to see the changes.

## Local Setup Instructions

To run the web app locally, follow these steps:

1. Ensure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).
2. Clone the repository:
   ```
   git clone https://github.com/vishu555/VishuFirstproject.git
   cd VishuFirstproject
   ```
3. Create a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python app.py  # Replace app.py with your main file
   ```
6. Open your browser and go to `http://127.0.0.1:5000` (or the port your app is running on).
