from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user
import os
import bleach
from database import db, EmergencyAlertUsers, EmergencyAlerts
from twilio.rest import Client
from app import limiter

# Blueprint for the website, so that app can have a designated file for the website routes
website_blueprint = Blueprint('website', __name__)

# Webpage – ONEPAGER
@website_blueprint.route('/onepager', methods=['GET', 'POST'])
# The onepager backend function is simple, it just renders the onepager.html template
# When the user visits the onepager webpage route
def onepager():
    return render_template('onepager.html')

# Webpage – ADMIN LOGIN
# Using the Flask-Login library, we can manage the user's login state
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# This function gets called every time the user accesses a route protected
# by the decorator @login_required
def load_user(user_id):
    # Codes fetches admin username from the environment variables
    admin_username = os.getenv('ADMIN_USERNAME')
    # If the user ID is the admin username, return the user object and exit the function, 
    # allowing the user to access the admin dashboard
    if user_id == admin_username:
        return User(user_id)
    return None
"""If load_user() returns None, it means that the user was not found 
or the user is not authorized. Any protected routes that require 
the user to be logged in (@login_required routes)"""

# The admin_login route is used to log in the admin user, from the admin_login.html template
@website_blueprint.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # This logic corresponds to the form submission from the admin_login.html template
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']
        # Codes fetches admin username and password from the environment variables
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')
        # If the username and password are correct, log the user in
        if username == admin_username and password == admin_password:
            # Create a User object with the username
            user = User(username)
            # Log the user in
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('website.admin_dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('admin_login.html')


# Webpage – ADMIN DASHBOARD
@website_blueprint.route('/admin_dashboard', methods=['GET', 'POST'])
# This route is protected by the @login_required decorator
# User must log in before accessing this route
@login_required
@limiter.limit("5 per minute")  # Limit the rate of requests to this route. 
# Limiter currently stored in-memory. When moved to production environment
# use Redis as a more robust solution for storing rate limit data.
def admin_dashboard():
    """
    Admin dashboard route. Handles both GET and POST requests.
    On a POST request, sends an alert message to all users and records the event.
    """
    if request.method == 'POST':
        # Get the message from the form
        alert_message = request.form.get('message')
        if alert_message is not None:
            # Append the automated message disclaimer
            alert_message = "**This is an automated alert**\n\n" + alert_message + "\n\n**End of alert**"
            # Sanitize the message to prevent XSS(security) attacks
            sanitized_message = bleach.clean(alert_message)
            # Query the database to get all users
            alert_users = EmergencyAlertUsers.query.all()
            # Twilio client setup (use your Twilio account SID and auth token)
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_ = os.getenv('TWILIO_FROM')
            client = Client(account_sid, auth_token)
            # For each user, send the message
            for user in alert_users:
                client.messages.create(
                    body=alert_message,
                    from_=from_,
                    to=user.phone_number
                )
                # Increment the total number of alerts sent for each user
                user.total_alerts += 1
            # Add the new alert data to the database
            number_of_users = len(alert_users)  # Count the number of users signed up for alerts
            # Create a new EmergencyAlerts object with the sanitized message and the number of users sent
            new_alert_event = EmergencyAlerts(message=sanitized_message, number_of_users_sent=number_of_users)
            db.session.add(new_alert_event)
            db.session.commit()  # Commit the changes to the database
    # Render the admin dashboard page
    return render_template('admin_dashboard.html')

# If this route is accessed, the user is logged out and redirected to the onepager
@website_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('website.onepager'))
