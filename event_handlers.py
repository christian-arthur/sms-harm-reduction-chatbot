# event_handlers.py

"""
This file contains functions that handle events that occur within the chatbot.
These events are logged in the database for analytics and reporting purposes.
"""

# Import the database and event models from the database.py file
from database import db, Event

# Create a new event in the database
def create_event(hashed_phone_number, type, resource_category=None, session_id=None, page_number=None, helpline_program=None, chatbot_service=None):
    event = Event(hashed_phone_number=hashed_phone_number, type=type, resource_category=resource_category, session_id=session_id, page_number=page_number, helpline_program=helpline_program, chatbot_service=chatbot_service)
    db.session.add(event)
    db.session.commit()

# This event is triggered when an SMS is received by the chatbot
def event_sms_received(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='sms_received', session_id=session_id)

# This event is triggered when an SMS is sent by the chatbot
def event_sms_sent(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number,type='sms_sent', session_id=session_id)

# This event is triggered when a user is created in the database
def event_create_user(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='create_user', session_id=session_id)

# This event is triggered when a session is created
def event_session_created(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='session_created', session_id=session_id)

# This event is triggered when a user opts in to the chatbot
def event_opt_in(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='opt-in', session_id=session_id)

# This event is triggered when a user opts out of the chatbot
def event_opt_out(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='opt-out', session_id=session_id)

# This event is triggered when a user's race is collected
def event_race_collected(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='race_collected', session_id=session_id)

# This event is triggered when a user's gender is collected
def event_gender_collected(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='gender_collected', session_id=session_id)

# This event is triggered when a user's age is collected
def event_age_collected(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='age_collected', session_id=session_id)

# This event is triggered when the user visits one of the three chatbot services, 
# which are the helpline, resource menu, or emergency alerts
def event_chatbot_service(hashed_phone_number, chatbot_service, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='chatbot_service', chatbot_service=chatbot_service, session_id=session_id)

# This event is triggered when the user selects a resource to view
def event_resource_view(hashed_phone_number, resource_category, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='resource_view', resource_category=resource_category, session_id=session_id)

# This event is triggered when the user changes page while in the resource view,
def event_page_change(hashed_phone_number, resource_category, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='page_change', resource_category=resource_category, session_id=session_id)

# This event is triggered when the user selects a helpline to view
def event_helpline_view(hashed_phone_number, helpline_program, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='helpline_view', helpline_program=helpline_program, session_id=session_id)

# This event is triggered when the user subscribes to the emergency alerts
def event_alerts_subscribe(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='alerts_subscribe', session_id=session_id)

# This event is triggered when the user unsubscribes from the emergency alerts
def event_alerts_unsubscribe(hashed_phone_number, session_id=None):
    create_event(hashed_phone_number=hashed_phone_number, type='alerts_unsubscribe', session_id=session_id)