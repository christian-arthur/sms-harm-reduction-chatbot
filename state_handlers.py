# This file contains functions that handle the state of the chatbot.

from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from database import db, SMSUser, EmergencyAlertUsers, EmergencyAlerts
from response_content import (greeting, opt_in_question, beta_testing_boilerplate, you_opted_out,
                              race_ethnicity_dictionary, multiracial_dictionary, gender_dictionary, age_group_dictionary, main_menu_response,
                              resource_menu_response, zipcode_input_message, resource_view_boilerplate, helpline_menu_response, safespot_info, nine_1_1_info, helpline_view_boilerplate, added_to_alerts,
                              not_subscribed_to_alerts_boilerplate, already_subscribed_to_alerts_boilerplate,
                              ma_substance_use_helpline, suicide_and_crisis_lifeline_info, safe_link_info,)
from event_handlers import (event_opt_in, event_opt_out, event_race_collected, event_gender_collected,
                            event_age_collected, event_chatbot_service, event_resource_view, event_helpline_view,
                            event_alerts_subscribe, event_alerts_unsubscribe, event_sms_sent,
                            event_page_change)
from chatbot_utils import typos_check, geolocate_resources, emergency_alerts_checker
from datetime import datetime, timezone
from app import resources_data

# This function handles the PRE-REGISTRATION state, which is the first state a user will see when they start the chatbot.
def state_PRE_REGISTRATION(user_session, hashed_phone_number, body=None):
    resp = MessagingResponse()
    msg = resp.message(f"\nHello, {greeting}\n {opt_in_question} \n \n {beta_testing_boilerplate}")
    # This is the image that will be displayed to the user when they start the chatbot.
    msg.media("https://goldenrod-bulldog-3127.twil.io/assets/EatEyeg%20-%20Imgur.jpg")
    event_sms_sent(hashed_phone_number, user_session.id)
    user_session.state = "REGISTRATION"
    db.session.commit()
    return str(resp)

# This function handles the REGISTRATION state, assessing whether the user wants to opt-in to the chatbot.
# and either moving forward with collecting demographics or completing opting out.
def state_REGISTRATION(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    if typos_check(body,'yes'):
        # A boolean value to track if the user opts in to the chatbot.
        user.opt_in = True
        user.opt_in_time = datetime.now()
        event_opt_in(hashed_phone_number, user_session.id)
        # If the user opts in, the chatbot will set the state to ASK_RACE_ETHNICITY
        user_session.state = "ASK_RACE_ETHNICITY"
        # If the user opts in, the chatbot will send the user the race/ethnicity question. The items() method turns the race_ethnicity_dictionary
        # into a list of tuples. A For loop iterates through the list of tuples and joins them into a string.
        resp.message("Please enter your race/ethnicity. Reply with the number next to the category:\n" + 
                            "".join([f"{k}) {v}\n" for k, v in race_ethnicity_dictionary.items()]))
    elif typos_check(body,'no'):
        # A boolean value to track if the user opts out of the chatbot.
        user.opt_in = False
        event_opt_out(hashed_phone_number, user_session.id)
        # If the user opts out, the chatbot will set the state to OPT-OUT
        user_session.state = "OPT-OUT"
        # If the user opts out, the chatbot will send the user the opted out message.
        resp.message(you_opted_out)
    # If the user does not opt in or out, the chatbot will send the user the opt in/out question.
    else:
        resp.message("Please reply with 'Yes' to opt-in or 'No' to opt-out.")
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the ASK_RACE_ETHNICITY state, logging the race/ethnicity of the user based on the response.
# and moving on to the next state, the gender question. If the user selects multiracial, the chatbot will branch them to questions recording their identities. 
def state_ASK_RACE_ETHNICITY(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    # This logic triggers if the user selects multiracial
    if body == '7' or typos_check(body, "multiracial"):
        # The chatbot will log the user as multiracial
        user.race_ethnicity = 'Multiracial'
        # Event that acknowledges the race/ethnicity of a user got collected
        event_race_collected(hashed_phone_number, user_session.id)
        # The chatbot will set the state to ASK_MULTIRACIAL1, branching the user through questions recording their racial/ethnic identities.
        user_session.state = "ASK_MULTIRACIAL1"
        # The chatbot will send the user the multiracial question.
        resp.message("You selected Multiracial. Please select one of your racial/ethnic identities by replying with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in multiracial_dictionary.items() if k != '7']))
    elif body in race_ethnicity_dictionary or any(typos_check(body, option) for option in race_ethnicity_dictionary.values()):
        """Check if user's input matches other valid responses. Must either...1) Be a number response matching one of the keys in the race_ethnicity_dictionary.
        2) Using a generator expression with the any() method to loop through the race_ethnicity_dictionary values (race/ethnicity options),
        if the user's response passes a typos_check() against the race/ethnicity option then the response is valid. Will never trigger for '7) Multiracial'
        because that would have been caught in the first if statement."""
        # Records the race/ethnicity if their response matches one of the keys in the race_ethnicity_dictionary.
        if body in race_ethnicity_dictionary:
            user.race_ethnicity = race_ethnicity_dictionary[body]
        else:
            # The items() method generates a list of (key, value) tuples from race_ethnicity_dictionary. We iterate through these tuples using a for loop.
            # For each value, we check if the user's response resembles the value, using the typos_check() function. 
            for key, value in race_ethnicity_dictionary.items():
                # If the user's response resembles the value, we assign that value to user.race_ethnicity and break the loop.
                if typos_check(body, value):
                    user.race_ethnicity = value
                    break
        # Event that acknowledges the race/ethnicity of a user got collected
        event_race_collected(hashed_phone_number, user_session.id)
        # The chatbot will set the state to ASK_GENDER
        user_session.state = "ASK_GENDER"
        # The chatbot will send the user the gender question.
        resp.message("Please enter your gender. Reply with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in gender_dictionary.items()]))
    else:
        # Invalid input handling
        resp.message("Invalid response. Please enter your race/ethnicity. Reply with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in race_ethnicity_dictionary.items()]))
        # The state remains ASK_RACE_ETHNICITY
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the ASK_MULTIRACIAL1 state, logging the first racial/ethnic identity of the user based on their response.
def state_ASK_MULTIRACIAL1(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    # Logic that triggers if the user's response is a valid key or close match to a value in the multiracial_dictionary
    if body in multiracial_dictionary or any(typos_check(body, option) for option in multiracial_dictionary.values()):
        # Checks if the input is a valid key
        if body in multiracial_dictionary:
            user.multiracial1 = multiracial_dictionary[body]
        else:
            # The items() method generates a list of (key, value) tuples from multiracial_dictionary. We iterate through these tuples using a for loop.
            # For each value, we check if the user's response resembles the value, using the typos_check() function. 
            for key, value in multiracial_dictionary.items():
                if typos_check(body, value):
                    user.multiracial1 = value
                    break
        # Event that acknowledges the first racial/ethnic identity of a multiracial user got collected
        event_race_collected(hashed_phone_number, user_session.id)
        # The chatbot will set the state to ASK_MULTIRACIAL2, which will handle the second racial/ethnic identity of the user.
        user_session.state = "ASK_MULTIRACIAL2"
        # The chatbot will send the user the second multiracial question. The items() method turns the multiracial_dictionary into a list of tuples. 
        # A For loop iterates through the list of tuples and joins them into a string.
        resp.message("Please select your second racial/ethnic identity by replying with the number next to the category:\n" + 
                    "".join([f"{k}) {v}\n" for k, v in multiracial_dictionary.items()]))
    else:
        # Invalid input handling
        resp.message("Invalid response. Please select one of your racial/ethnic identities by replying with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in multiracial_dictionary.items()]))
        # The state remains ASK_MULTIRACIAL1
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the ASK_MULTIRACIAL2 state, logging the second racial/ethnic identity of the user based on their response.
# After this question the chatbot routes the used from the multiracial question branch back to the main path and asks the gender question.
def state_ASK_MULTIRACIAL2(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    # Logic that triggers if the user's response is a valid key or close match to a value in the multiracial_dictionary
    if body in multiracial_dictionary or any(typos_check(body, option) for option in multiracial_dictionary.values()):
        # Checks if the input is a valid key
        if body in multiracial_dictionary:
            user.multiracial1 = multiracial_dictionary[body]
        else:
            # The items() method generates a list of (key, value) tuples from multiracial_dictionary. We iterate through these tuples using a for loop.
            # For each value, we check if the user's response resembles the value, using the typos_check() function. 
            for key, value in multiracial_dictionary.items():
                if typos_check(body, value):
                    user.multiracial1 = value
                    break
        # Event that acknowledges the first racial/ethnic identity of a multiracial user got collected
        event_race_collected(hashed_phone_number, user_session.id)
        # The chatbot will set the state to ASK_GENDER
        user_session.state = "ASK_GENDER"
        # The chatbot will send the user the gender question. The items() method turns the gender_dictionary into a list of tuples. 
        # A Foor loop iterates through the list of tuples and joins them into a string.
        resp.message("Please enter your gender. Reply with the number next to the category:\n" + 
                    "".join([f"{k}) {v}\n" for k, v in gender_dictionary.items()]))
    else:
        # Invalid input handling
        resp.message("Invalid response. Please select another of your racial/ethnic identities by replying with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in multiracial_dictionary.items()]))
        # The state remains ASK_MULTIRACIAL2
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)


# This function handles the ASK_GENDER state, logging the gender of the user based on the response.
# and moving on to the next state, the age question.
def state_ASK_GENDER(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)    
    # Check if the input is valid (either a key in the dictionary or a close match to a value)
    if body in gender_dictionary or any(typos_check(body, option) for option in gender_dictionary.values()):
        # If the input is a valid key, use it directly
        if body in gender_dictionary:
            user.gender = gender_dictionary[body]
        else:
            # The items() method generates a list of (key, value) tuples from gender_dictionary. We iterate through these tuples using a for loop.
            # For each value, we check if the user's response resembles the value, using the typos_check() function. 
            for key, value in gender_dictionary.items():
                if typos_check(body, value):
                    user.gender = value
                    break
        if body == "6" or typos_check(body, "other"):
            # Route to intermediary state for free text entry
            user_session.state = "ASK_GENDER_OTHER"
            resp.message("Please type and send your gender identity:")
            event_gender_collected(hashed_phone_number, user_session.id)
        else:
            # Event that acknowledges the gender of a user got collected
            # The chatbot will set the state to ASK_AGE_GROUP
            user_session.state = "ASK_AGE_GROUP"
            # The chatbot will send the user the age question. The items() method turns the age_group_dictionary into a list of tuples. 
            # A For loop iterates through the list of tuples and joins them into a string.
            resp.message("Please enter your age group. Reply with the number next to the category:\n" + 
                         "".join([f"{k}) {v}\n" for k, v in age_group_dictionary.items()]))
            event_gender_collected(hashed_phone_number, user_session.id)
    else:
        # Invalid input handling
        resp.message("Invalid response. Please enter your gender. Reply with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in gender_dictionary.items()]))
        # The state remains ASK_GENDER
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)


# This function handles the ASK_GENDER_OTHER state, logging the gender of the user based on the response.
# and moving on to the next state, the age question.
def state_ASK_GENDER_OTHER(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    user.gender_other = body
    user_session.state = "ASK_AGE_GROUP"
    resp.message("Please enter your age group. Reply with the number next to the category:\n" + 
                         "".join([f"{k}) {v}\n" for k, v in age_group_dictionary.items()]))
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the ASK_AGE_GROUP state, logging the age group of the user based on the response.
# and moving on to the main menu.
def state_ASK_AGE_GROUP(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    user = SMSUser.query.get(hashed_phone_number)
    # Check if the input is valid (either a key in the dictionary or a close match to a value)
    if body in age_group_dictionary or any(typos_check(body, option) for option in age_group_dictionary.values()):
        # If the input is a valid key, use it directly
        if body in age_group_dictionary:
            user.age_group = age_group_dictionary[body]
        else:
            # The items() method generates a list of (key, value) tuples from age_group_dictionary. We iterate through these tuples using a for loop.
            # For each value, we check if the user's response resembles the value, using the typos_check() function. 
            for key, value in age_group_dictionary.items():
                if typos_check(body, value):
                    user.age_group = value
                    break
        # Event that acknowledges the age group of a user got collected
        event_age_collected(hashed_phone_number, user_session.id)
        # The chatbot will set the state to MAIN_MENU
        user_session.state = "MAIN_MENU"
        # The chatbot will send the user the main menu response.
        resp.message(main_menu_response)
    else:
        # Invalid input handling
        resp.message("Invalid response. Please enter your age group. Reply with the number next to the category:\n" + 
                     "".join([f"{k}) {v}\n" for k, v in age_group_dictionary.items()]))
        # The state remains ASK_AGE_GROUP
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the MAIN_MENU state, which is the main menu of the chatbot.
def state_MAIN_MENU(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user selects the "find harm reduction resources" option
    if body == '1' or typos_check(body, "find harm reduction resources"):
        # This event records a user was interested in the harm reduction resources
        event_chatbot_service(hashed_phone_number, 'resource_menu', user_session.id)
        # The chatbot will set the state to RESOURCE_MENU
        user_session.state = "RESOURCE_MENU"
        resp.message(resource_menu_response)
        # This logic triggers if the user selects the "talk with a helpline" option
    elif body == '2' or typos_check(body, "talk with a helpline"):
        # This event records a user was interested in the helpline services
        event_chatbot_service(hashed_phone_number, 'helpline_menu', user_session.id)
        # The chatbot will set the state to HELPLINE_MENU
        user_session.state = "HELPLINE_MENU"
        resp.message(helpline_menu_response)
    # This logic triggers if the user selects the "emergency alerts" option
    elif body == '3' or typos_check(body, "emergency alerts"):
        # This event records a user was interested in the emergency alerts
        event_chatbot_service(hashed_phone_number, 'emergency_alerts', user_session.id)
        # The chatbot will set the state to EMERGENCY_ALERTS
        user_session.state = "EMERGENCY_ALERTS"
        resp.message(emergency_alerts_checker(request.values.get('From', None), user_session))
    # This logic triggers if the user selects any other option
    else:
        resp.message("Invalid response.\n\n"+ main_menu_response)
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the RETURNING_USER state, and displays the main menu of the chatbot for returning users.
def state_RETURNING_USER(user_session, hashed_phone_number, body=None):
    resp = MessagingResponse()
    msg = resp.message(f"\nWelcome back, {greeting}\n {main_menu_response} \n \n {beta_testing_boilerplate}")
    msg.media("https://goldenrod-bulldog-3127.twil.io/assets/EatEyeg%20-%20Imgur.jpg")
    event_sms_sent(hashed_phone_number, user_session.id)
    # The chatbot will set the state to MAIN_MENU, so when the user sends a message, it will be handled by the state_MAIN_MENU function.
    user_session.state = "MAIN_MENU"
    db.session.commit()
    return str(resp)

# This function handles the RESOURCE_MENU state, routing the user to the resource view
# for the program they selected.
def state_RESOURCE_MENU(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user selects the "syringe service program" option
    if body == '1' or typos_check(body, "syringe service program"):
        # Code tracks the resource category in the user's current session
        user_session.resource_category = 'Syringe Service Program'
        # This event records a user was interested in the syringe service program
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        # The chatbot will set the state to ZIPCODE_INPUT
        user_session.state = 'ZIPCODE_INPUT'
        # The chatbot will send the user the zipcode input message
        resp.message(zipcode_input_message + "\n" + resource_view_boilerplate)
    # This logic triggers if the user selects the "0" or "menu" option
    elif body == '2' or typos_check(body, "medication for opioid use disorder"):
        user_session.resource_category = 'Medication for Opioid Use Disorder'
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        user_session.state = 'ZIPCODE_INPUT'
        resp.message(zipcode_input_message + "\n\n" + resource_view_boilerplate)
    elif body == '3' or typos_check(body, "naloxone and overdose training"):
        user_session.resource_category = 'Naloxone and Overdose Training'
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        user_session.state = 'ZIPCODE_INPUT'
        resp.message(zipcode_input_message + "\n\n" + resource_view_boilerplate)
    elif body == '4' or typos_check(body, "bridge clinic"):
        user_session.resource_category = 'Bridge Clinic'
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        user_session.state = 'ZIPCODE_INPUT'
        resp.message(zipcode_input_message + "\n\n" + resource_view_boilerplate)
    elif body == '5' or typos_check(body, "shelter"):
        user_session.resource_category = 'Shelter'
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        user_session.state = 'ZIPCODE_INPUT'
        resp.message(zipcode_input_message + "\n\n" + resource_view_boilerplate)
    elif body == '6' or typos_check(body, "detox"):
        user_session.resource_category = 'Detox'    
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
        user_session.state = 'ZIPCODE_INPUT'
        resp.message(zipcode_input_message + "\n\n" + resource_view_boilerplate)
    elif any(typos_check(body, option) for option in ['0', 'menu']):    
        # The chatbot will set the state to MAIN_MENU
        user_session.state = "MAIN_MENU"
        # The chatbot will send the user the main menu response
        resp.message(main_menu_response)
    # This logic triggers if the user sends any other response
    else:
        # The chatbot will send the user the resource menu response again
        resp.message(resource_menu_response)
        # The chatbot will set the state to RESOURCE_MENU
        user_session.state = 'RESOURCE_MENU'
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the ZIPCODE_INPUT state, which is the state where the user inputs their zipcode.
def state_ZIPCODE_INPUT(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    if any(typos_check(body, option) for option in ['*', 'resources']):
        user_session.state = 'RESOURCE_MENU'
        resp.message(resource_menu_response)
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        user_session.state = 'MAIN_MENU'
        resp.message(main_menu_response)
    elif body is not None and body.isdigit() and len(body) == 5:
        zipcode = body
        user_session.state = 'RESOURCE_VIEW'
        geolocate_result = geolocate_resources(user_session.resource_category, zipcode)
        resp.message(geolocate_result + "Enter another zipcode to try again.\n" + resource_view_boilerplate)
        user_session.state = 'ZIPCODE_INPUT'
        event_resource_view(hashed_phone_number, user_session.resource_category, user_session.id)
    else:
        resp.message("Invalid response. Please enter a valid zipcode.")
        user_session.state = 'ZIPCODE_INPUT'
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the RESOURCE_VIEW state, and exists to navigate the user
# through the pages of resources they are viewing.
def state_RESOURCE_VIEW(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    if body == '*' or typos_check(body, "resources"):
        user_session.state = 'RESOURCE_MENU'
        resp.message(resource_menu_response)
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        user_session.state = 'MAIN_MENU'
        resp.message(main_menu_response)
    else:
        resp.message("Invalid response.\n\n" + resource_view_boilerplate)
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the HELPLINE_MENU state, routing the user to the helpline program info
# for the program they selected.
def state_HELPLINE_MENU(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user selects the "substance use helpline" option
    if body == '1' or typos_check(body, "substance use help"):
        # Code tracks the helpline program in the user's current session
        user_session.helpline_program = 'MA Substance Use Helpline'
        # This event records a user was interested in the MA Substance Use Helpline
        event_helpline_view(hashed_phone_number, user_session.helpline_program, user_session.id)
        # The chatbot will set the state to HELPLINE_VIEW, because the user is next viewing/navigating to the helpline program info
        user_session.state = 'HELPLINE_VIEW'
        # The chatbot will send the user the helpline program info for the MA Substance Use Helpline
        resp.message(ma_substance_use_helpline + "\n\n" + helpline_view_boilerplate)
    # This logic triggers if the user selects the "safespot" option
    elif body == '2' or typos_check(body, "safespot"):
        # Code tracks the helpline program in the user's current session
        user_session.helpline_program = 'SafeSpot'
        # This event records a user was interested in the safespot helpline program
        event_helpline_view(hashed_phone_number, user_session.helpline_program, user_session.id)
        # The chatbot will set the state to HELPLINE_VIEW, because the user is next viewing/navigating to the helpline program info
        user_session.state = 'HELPLINE_VIEW'             
        # The chatbot will send the user the helpline program info for the safespot
        resp.message(safespot_info + "\n\n"+ helpline_view_boilerplate)
    # This logic triggers if the user selects the "suicide" option
    elif body == '3' or typos_check(body, "suicide"):
        # Code tracks the helpline program in the user's current session
        user_session.helpline_program = 'Suicide and Crisis Lifeline'
        # This event records a user was interested in the Suicide and Crisis Lifeline helpline program
        event_helpline_view(hashed_phone_number, user_session.helpline_program, user_session.id)
        # The chatbot will set the state to HELPLINE_VIEW, because the user is next viewing/navigating the helpline program info
        user_session.state = 'HELPLINE_VIEW'        
        # The chatbot will send the user the helpline program info for the Suicide and Crisis Lifeline
        resp.message(suicide_and_crisis_lifeline_info + "\n\n" + helpline_view_boilerplate)
    # This logic triggers if the user selects the "safe link" option
    elif body == '4' or typos_check(body, "safe link"):
        # Code tracks the helpline program in the user's current session
        user_session.helpline_program = 'SafeLink'
        # This event records a user was interested in the SafeLink helpline program
        event_helpline_view(hashed_phone_number, user_session.helpline_program, user_session.id)
        # The chatbot will set the state to HELPLINE_VIEW, because the user is next viewing/navigating the helpline program info
        user_session.state = 'HELPLINE_VIEW'
        # The chatbot will send the user the helpline program info for the SafeLink
        resp.message(safe_link_info + "\n\n" + helpline_view_boilerplate)   
    # This logic triggers if the user selects the "911" option
    elif body == '4' or typos_check(body, "immediate danger"):
        # Code tracks the helpline program in the user's current session
        user_session.helpline_program = '911'
        # This event records a user was interested in the 911 helpline program
        event_helpline_view(hashed_phone_number, user_session.helpline_program, user_session.id)
        # The chatbot will set the state to HELPLINE_VIEW, because the user is next viewing/navigating the helpline program info
        user_session.state = 'HELPLINE_VIEW'
        # The chatbot will send the user the helpline program info for the 911
        resp.message(nine_1_1_info + "\n\n" + helpline_view_boilerplate)
    # This logic triggers if the user decides to go back to the main menu
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        # The chatbot will set the state to MAIN_MENU
        user_session.state = "MAIN_MENU"
        # The chatbot will send the user the main menu response
        resp.message(main_menu_response)
    # This logic triggers if the user sends any other response
    else:
        # The chatbot will indicate the response was invalid and send the user the helpline menu response again
        resp.message("Invalid response.\n\n" + helpline_menu_response)
    # Log the SMS sent event
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the HELPLINE_VIEW state. Because all helpline program info is
# on one page, this function only allows the user to navigate back to the helpline menu
# or the main menu.
def state_HELPLINE_VIEW(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user seeks to navigate back to the helpline menu
    if body == '*' or typos_check(body, "helplines"):
        # The chatbot will set the state to HELPLINE_MENU 
        # because the user is next viewing/navigating the helpline menu
        user_session.state = "HELPLINE_MENU"
        # The chatbot will send the user the helpline menu response
        resp.message(helpline_menu_response)
    # This logic triggers if the user seeks to navigate back to the main menu
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        # The chatbot will set the state to MAIN_MENU
        # because the user is next viewing/navigating the main menu
        user_session.state = "MAIN_MENU"
        # The chatbot will send the user the main menu response
        resp.message(main_menu_response)
    # This logic triggers if the user sends any other response
    else:
        # The chatbot will indicate the response was invalid and send the user the helpline view boilerplate again
        resp.message("Invalid response.\n\n" + helpline_view_boilerplate)    
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)

# This function handles the NEW_ALERTS_USER state, which the session state would be set to
# if the user navigated to the emergency alerts menu and was not already subscribed
def state_NEW_ALERTS_USER(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user opts in to emergency alerts
    # The phone number is retrieved from the request values
    phone_number = request.values.get('From', None)
    if typos_check(body, "add"):
        # Adds the user to the EmergencyAlertUsers table
        new_user = EmergencyAlertUsers(phone_number=phone_number, total_alerts=0, timestamp_user_created=datetime.now(timezone.utc))
        db.session.add(new_user)
        # Notifies the user that they have been added to the emergency alerts list and provides the main menu info
        resp.message(added_to_alerts + main_menu_response)
        event_alerts_subscribe(hashed_phone_number, user_session.id)
        # Sets the user's session state to MAIN_MENU because they're sent there
        # after opting in to emergency alerts
        user_session.state = "MAIN_MENU"
    # This logic triggers if the user seeks to navigate back to the main menu
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        # Sets the user's session state to MAIN_MENU because they're seeking to return 
        user_session.state = "MAIN_MENU"
        # Sends the user the main menu response
        resp.message(main_menu_response)
    # This logic triggers if the user sends any other response
    else:
        # Notifies the user that their response was invalid and provides the not subscribed to emergency alerts boilerplate
        resp.message("Invalid response.\n\n" + not_subscribed_to_alerts_boilerplate)    
    # Logs the SMS sent event
    event_sms_sent(hashed_phone_number, user_session.id)
    # Commits the changes to the database
    db.session.commit()
    return str(resp)

# This function handles the EXISTING_ALERTS_USER state, which the session state would be set to
# if the user navigated to the emergency alerts menu and was already subscribed
def state_EXISTING_ALERTS_USER(user_session, hashed_phone_number, body):
    resp = MessagingResponse()
    # This logic triggers if the user decides to opt out of emergency alerts
    # The phone number is retrieved from the request values
    phone_number = request.values.get('From', None)
    if typos_check(body, "remove"):
        # First checks if the user is in the EmergencyAlertUsers table
        user_to_remove = EmergencyAlertUsers.query.filter_by(phone_number=phone_number).first()
        # If the user is in the table, remove them
        if user_to_remove:
            db.session.delete(user_to_remove)
            db.session.commit()
        event_alerts_unsubscribe(hashed_phone_number, user_session.id)
        # Set the user's session state to MAIN_MENU, because they're getting sent back to the main menu
        user_session.state = "MAIN_MENU"
        # Notifies the user that they have been removed from the emergency alerts list and provides the main menu info
        resp.message("You have been removed from the emergency alerts list.\n\n"
                    "Sending you back to the main menu..."
                    + main_menu_response)
    # Logic triggers if the user wants to see the latest emergency alert
    elif typos_check(body, "latest"):
        # Set the user's session state to MAIN_MENU, because they're getting sent back to the main menu after seeing the latest emergency alert
        user_session.state = "MAIN_MENU"
        # Get the latest emergency alert from the EmergencyAlerts table
        latest_alert = EmergencyAlerts.query.order_by(EmergencyAlerts.timestamp.desc()).first() 
        # If at least one emergency alert has been sent, notify the user what is 
        if latest_alert is not None:
            resp.message("The latest emergency alert is:\n\n'" +
                        latest_alert.message +
                         "'\n\nSending you back to the main menu...\n"
                         + main_menu_response)
        # If no emergency alerts have been sent, notify the user
        else:
            resp.message("No alerts have been sent out yet.\n"
                        "Sending you back to the main menu...\n"
                        + main_menu_response)
    # Logic triggers if the user seeks to navigate back to the main menu
    elif any(typos_check(body, option) for option in ['0', 'menu']):
        # Set the user's session state to MAIN_MENU, because they're seeking to return to the main menu
        user_session.state = "MAIN_MENU"
        # Send the user the main menu response
        resp.message(main_menu_response)
    # This logic triggers if the user sends any other response
    else:
        # Notify the user that their response was invalid and provide the already subscribed to emergency alerts boilerplate
        # The state will not change, so the user will be sent back to the emergency alerts menu
        resp.message("Invalid response.\n\n" + already_subscribed_to_alerts_boilerplate)    
    event_sms_sent(hashed_phone_number, user_session.id)
    db.session.commit()
    return str(resp)