from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from database import db, SMSUserSession
from chatbot_utils import check_create_user, is_session_expired, create_user_session, hash_phone_number
from event_handlers import event_sms_received
from state_handlers import (state_PRE_REGISTRATION, state_REGISTRATION, state_ASK_RACE_ETHNICITY,
                            state_ASK_MULTIRACIAL1, state_ASK_MULTIRACIAL2, state_ASK_GENDER, state_ASK_GENDER_OTHER,state_ASK_AGE_GROUP,
                            state_MAIN_MENU, state_RESOURCE_MENU, state_RESOURCE_VIEW, state_ZIPCODE_INPUT, state_HELPLINE_MENU, state_HELPLINE_VIEW,
                            state_NEW_ALERTS_USER, state_EXISTING_ALERTS_USER, state_RETURNING_USER)

chatbot_blueprint = Blueprint('chatbot', __name__)

@chatbot_blueprint.route("/sms", methods=['GET', 'POST'])
def sms_reply():
     # Extract phone number and message body from the request
    phone_number = request.values.get('From', None)
    hashed_phone_number = hash_phone_number(phone_number)
    body = request.values.get('Body', None)

    # Convert the body to lowercase to ensure consistent processing
    if body is not None:
        body = body.lower()

    # Check if the user exists in the database, and create a new user if they don't
    check_create_user(hashed_phone_number)

    # Get the user's session. If the session is expired the query will return None.
    user_session = SMSUserSession.query.filter_by(hashed_phone_number=hashed_phone_number).order_by(SMSUserSession.last_interaction.desc()).first()
    
    # If the session doesn't exist (None) or is expired, create a new session.
    if not user_session or is_session_expired(user_session):
        user_session = create_user_session(hashed_phone_number)

    # Log the SMS received event
    event_sms_received(hashed_phone_number, user_session.id)
    db.session.commit()

    # Use a dictionary to map states to their handler functions
    state_handlers = {
        "PRE-REGISTRATION": state_PRE_REGISTRATION,
        "REGISTRATION": state_REGISTRATION,
        "ASK_RACE_ETHNICITY": state_ASK_RACE_ETHNICITY,
        "ASK_MULTIRACIAL1": state_ASK_MULTIRACIAL1,
        "ASK_MULTIRACIAL2": state_ASK_MULTIRACIAL2,
        "ASK_GENDER": state_ASK_GENDER,
        "ASK_GENDER_OTHER": state_ASK_GENDER_OTHER,
        "ASK_AGE_GROUP": state_ASK_AGE_GROUP,
        "MAIN_MENU": state_MAIN_MENU,
        "RETURNING_USER": state_RETURNING_USER,
        "RESOURCE_MENU": state_RESOURCE_MENU,
        "ZIPCODE_INPUT": state_ZIPCODE_INPUT,
        "RESOURCE_VIEW": state_RESOURCE_VIEW,
        "HELPLINE_MENU": state_HELPLINE_MENU,
        "HELPLINE_VIEW": state_HELPLINE_VIEW,
        "NEW_ALERTS_USER": state_NEW_ALERTS_USER,
        "EXISTING_ALERTS_USER": state_EXISTING_ALERTS_USER,
    }
    # Call the appropriate state handler function
    if user_session.state in state_handlers:
        return state_handlers[user_session.state](user_session, hashed_phone_number, body)
        """In the above code, user_session.state is the current state of the conversation
        # This code uses the current state as the key to look up the corresponding function in the state_handlers dictionary
        # Then it calls that function with the user_session, hashed_phone_number, and body as arguments
        """
    else:
        # Handle unknown state. This shouldn't happen, but it's good to have a fallback.
        resp = MessagingResponse()
        resp.message("An error occurred. Please try again later.")
        return str(resp)