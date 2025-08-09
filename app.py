# Import necessary libraries and modules
import os
from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database import db

# Create the Flask application
app = Flask(__name__)
# When testing locally uncomment the second line and comment out the first line. Do vice versa when deploying to Heroku
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('HR_DATABASE_URI')
# secret key
app.secret_key = os.environ.get('SECRET_KEY')

# Initialize the database
db.init_app(app)

# Load and cache the data at startup
resources_data = None
# Load and cache the data at startup
with app.app_context():
    # The db.drop_all() is commented out to prevent accidental database drops.
    # Uncomment it only when you need to drop and recreate the tables, during development.
    db.drop_all()  # Drop all tables
    # Create all tables if database does not exist
    db.create_all()  # Create all tables if database does not exist

# Set up rate limiting for the application
limiter = Limiter(key_func=get_remote_address, app=app)

# Set up the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'website.admin_login'

# Import these here to avoid circular import errors
from chatbot import chatbot_blueprint
from website import website_blueprint, load_user

# Register blueprints
app.register_blueprint(chatbot_blueprint)
app.register_blueprint(website_blueprint)

# Set the user loader
login_manager.user_loader(load_user)

# Entry point for running the Flask application
if __name__ == "__main__":
    app.run(debug=True)

    #test
