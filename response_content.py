# Description: This file contains most response content for the chatbot. It's separated from the main file to make the code more readable and maintainable.

# Greeting message for the chatbot
greeting = "I'm a Harm Reduction Chatbot! I'm helping out in Massachusetts."

# Opt-in question for the chatbot
opt_in_question = (
    "\nYou'll need to opt-in to use this app.\n\n"
    "This chatbot anonymously and securely collects the app user activity.\n\n"
    "The info improves the chatbot.\n\n"
    "Type 'Yes' to opt-in or 'No' to opt-out"
)

# Beta testing boilerplate for the chatbot
beta_testing_boilerplate = "**We're beta testing, so service may go under maintenance. Check the status here: bit.ly/hrcb_status. Users may need to re-register when the chatbot updates. Encounter a bug or have a suggestion? Tell the developer! bit.ly/hrc_feedback **"

# Message for when a user opts out of the chatbot
you_opted_out = (
    "You have opted out.\n"
        "You cannot use the app unless you opt-in.\n" 
        "You can opt-in anytime by sending a new message.\n"
        "Otherwise, have a nice day!"
)

# Race/ethnicity dictionary for the chatbot, used both in sending the race/ethnicity question and in logging the race/ethnicity of the user
race_ethnicity_dictionary = {
    '1': 'Asian', '2':'Native Hawaiian/Pacific Islander',
    '3': 'Black/African American', '4': 'White',
    '5': 'Hispanic/Latino(x)(e)', '6': 'Indigenous/Native American',
    '7': 'Middle Eastern/North African', '8': 'Multiracial','9': 'Other',
    '10': "Don't Know", '11': "Refuse to Answer"
}

# Multiracial dictionary for the chatbot, used both in sending the multiracial question and in logging the race/ethnicity of the user
multiracial_dictionary = {
'1': 'Asian', '2':'Native Hawaiian/Pacific Islander',
    '3': 'Black/African American', '4': 'White',
    '5': 'Hispanic/Latino(x)(e)', '6': 'Indigenous/Native American',
    '7': 'Middle Eastern/North African', '8': 'Other',
    '9': "Don't Know", '10': "Refuse to Answer"
}

# Gender dictionary for the chatbot, used both in sending the gender question and in logging the gender of the user
gender_dictionary = {
    '1': 'Woman', '2': 'Man', '3': 'Non-binary',
    '4': 'Transgender Women', '5': 'Transgender Man',
    '6': 'Other', '7': "Don't Know", '8': "Refuse to Answer"
}

# Age group dictionary for the chatbot, used both in sending the age group question and in logging the age group of the user
age_group_dictionary = {
'1': 'Under 18', '2': '18-24', '3': '25-34',
'4': '35-44', '5': '45-54', '6': '55-70',
'8': "More than 70", '9': "Don't Know",
'10': "Refuse to Answer"
}

# Main menu response for the chatbot
main_menu_response = (
    "\nWhat are you looking for? Reply with the number or category:\n" 
        "1) Harm reduction resources\n"
        "2) Talk with a helpline\n"
        "3) Alerts about emerging risks in the Massachusetts drug supply\n")

# Resource menu response for the chatbot
resource_menu_response = (
    "\nWhat are you looking for? Reply with the number or category:\n" 
        "1) Syringe Service Program 💉\n"
        "2) Medication for Opioid Use Disorder 💊\n"
        "3) Naloxone and Overdose Training 🚨\n"
        "4) Bridge Clinic (medical services) 🩺\n"
        "5) Emergency Shelter 🛏️\n"
        "6) Detox 🏥\n"
        "\nReply 'Menu' or '0' to return to the chatbot main menu."
)

# Zipcode input message for the chatbot
zipcode_input_message = (
    "What zipcode are you looking for? Reply with the Massachusetts zipcode."
)

# Emoji dictionary for the chatbot. This is used to add an emoji to the beginning of the resource view response.
emoji_dict = {
    "Syringe Service Program": "💉",
}

# Appended to the end of the resource view response to allow the user to view more resources.
more_resources = "Reply 'More' for the next page of resources."

# Boilerplate for the resource view response. This is appended to the end of the resource view response.
resource_view_boilerplate = (
    "\nReply '*' or 'Resources' to return to the resources menu."
    "\n\nReply '0' or 'Menu' to return to the chatbot main menu."  
)       

# Helpline menu response for the chatbot
helpline_menu_response = (
    "What helpline are you looking for? Reply with the number:\n"
        "1) Looking for treatment or other substance use services?\n"
        "2) Experiencing mental health crisis or need someone to talk to?\n"
        "3) In danger of domestic violence or need help?\n"
        "4) Need help with immediate danger or overdose!\n"
        "\nReply 'Menu' to return to the chatbot main menu."
)

# Boilerplate for the helpline view response. This is appended to the end of the helpline view response.
helpline_view_boilerplate = (
    "Reply '*' or 'Helplines' to return to the helpline menu."
    "\n\nReply '0' or 'Menu' to return to the chatbot main menu."
    )

# MA Substance Use Helpline info for the chatbot
ma_substance_use_helpline = (
    "MA Substance Use Helpline 🧭\n"
                "• Provides information about substance use treatment, helping with questions about location and insurance and more.\n"
                "• Call 800.327.5050\n"
                "• Text: “HOPE” to 8003275050\n"
                "• Available 24 hours per day"
)

# SafeSpot info for the chatbot
safespot_info = (
     "SafeSpot ❤️\n"
            "• Connect with trained operators and peers who support you while you use drugs, and call for help if you overdose.\n"
            "• Call 1-800-972-0590\n"
            "• Available 24/7"
)

# Crisis and Emotional Support info for the chatbot
suicide_and_crisis_lifeline_info = (
    "Suicide and Crisis Lifeline 🆘\n"
        "• Call for any emotional or mental health support or if you just need someone to talk to\n"
        "• Call or text: 988\n"
        "• Available 24/7"
)

# SafeLink (Massachusetts Domestic Violence) info for the chatbot
safe_link_info = (
    "SafeLink. Massachusetts Domestic Violence 🛡️\n"
        "• Call for help if you are in danger or need to talk to someone about domestic violence.\n"
        "• Call 1-877-785-2020\n"
        "• Available 24/7"
)

# 911 info for the chatbot
nine_1_1_info = (
    "911 🚨\n"
        "• Call for immediate danger, like an overdose or violence.\n"
        "• Available 24/7"
)

# What the user sees when they visit the alerts menu and are not subscribed to the emergency alerts
not_subscribed_to_alerts_boilerplate = (
    "Reply 'Add' to sign up for emergency alerts. 🔔\n\n"
    "Reply 'Menu' to return to the chatbot main menu.\n\n"
) 

# What the user sees when they visit the alerts menu and are already subscribed to the emergency alerts
already_subscribed_to_alerts_boilerplate = (
    "Reply 'Remove' to remove yourself from the list.\n\n"
    "Reply 'Latest' to get the latest emergency alert.\n\n"
    "Reply 'Menu' to return to the chatbot main menu."
)

# What the user sees when they are added to the emergency alerts list
added_to_alerts = (
    "You have been added to the emergency alerts list. The chatbot administrator will send out mass texts if new risks in the drug supply appear.\n\n"
    "Bringing you back to the main menu...\n"
)