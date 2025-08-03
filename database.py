from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy extension
db = SQLAlchemy()

# Define the database model for the SMS users
class SMSUser(db.Model):
    __tablename__ = 'users'
    # Define the columns for the SMSUser model
    hashed_phone_number = db.Column(db.String, primary_key=True)
    first_interaction = db.Column(db.DateTime, default=datetime.now())
    race_ethnicity = db.Column(db.String)
    multiracial1 = db.Column(db.String)
    multiracial2 = db.Column(db.String)
    gender = db.Column(db.String)
    age_group = db.Column(db.String)
    opt_in = db.Column(db.Boolean, default=False)
    opt_in_time = db.Column(db.DateTime, default=datetime.now())
    # Define the relationship to SMSUserSession, which is a one-to-many relationship, meaning that each 
    # SMSUser can have multiple SMSUserSessions, and each SMSUserSession belongs to one SMSUser.
    sessions = db.relationship('SMSUserSession', backref='user')

# Define the database model for the SMS user sessions
class SMSUserSession(db.Model):
    __tablename__ = 'sessions'
    # Define the columns for the SMSUserSession model
    id = db.Column(db.Integer, primary_key=True)
    # hashed_phone_number is a 'foreign key' linking a session to the corresponding SMSUser.
    # This means that every SMSUserSession must have a corresponding hashed_phone_number
    hashed_phone_number = db.Column(db.String, db.ForeignKey('users.hashed_phone_number'))
    state = db.Column(db.String)
    last_interaction = db.Column(db.DateTime, default=datetime.now())
    first_interaction = db.Column(db.Boolean, default=True)
    resource_category = db.Column(db.String)
    # page_number is used to track the page number within the resources view
    page_number = db.Column(db.Integer, default=0)
    helpline_program = db.Column(db.String)
    # 'events' defines a one-to-many relationship with the Event model.
    # Each SMSUserSession can have multiple associated Events, and each Event belongs to one SMSUserSession,
    # as defined by a foreign key in the Event table.
    events = db.relationship('Event', backref='session')

# Define the database model for the events
class Event(db.Model):
    __tablename__ = 'events'
    # Define the columns for the Event model
    id = db.Column(db.Integer, primary_key=True)
    # session_id is a 'foreign key' linking an event to the corresponding SMSUserSession.
    # This means that every Event must have a corresponding session_id
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    # hashed_phone_number is a 'foreign key' linking an event to the corresponding SMSUser.
    # This means that every Event must have a corresponding hashed_phone_number
    hashed_phone_number = db.Column(db.String, db.ForeignKey('users.hashed_phone_number')) 
    # type is used to track the type of event, such as 'opt_in', 'opt_out', 'resource_view'
    type = db.Column(db.String)
    # chatbot_service is used to track the chatbot service that the user is using, such as 'resource_menu or 'hotline_menu'
    chatbot_service = db.Column(db.String)
    # resource_category is used to track the resource category that the user is viewing, such as 'Syringe Service Program'
    resource_category = db.Column(db.String)
    # hotline_program is used to track the hotline program that the user is using, such as 'SafeSpot'
    helpline_program = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    page_number = db.Column(db.Integer)

# Define the database model for the emergency alert users
class EmergencyAlertUsers(db.Model):
    __tablename__ = 'alert_users'
    # Define the columns for the EmergencyAlertUsers model
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String)
    total_alerts = db.Column(db.Integer)
    timestamp_user_created = db.Column(db.DateTime, default=datetime.now())

# Define the database model for the emergency alerts
class EmergencyAlerts(db.Model):
    __tablename__ = 'emergency_alerts'
    # Define the columns for the EmergencyAlerts model
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    number_of_users_sent = db.Column(db.Integer)

"""The foreign keys confer a degree of integrity to the database. Although the code would 
work without them, the foreign keys ensure that the data is consistent across the tables.
"""