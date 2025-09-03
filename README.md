# Harm Reduction SMS Chatbot

A Flask-based SMS chatbot that provides harm reduction resources, connects users to hotlines, and sends emergency alerts about risks in the drug supply. Check out the proof-of-concept deployed [here](https://harm-reduction-chatbot-6ffe8d284c93.herokuapp.com/onepager)!

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Database Models](#database-models)
- [Web Interface](#web-interface)
- [Deployment](#deployment)
- [Security](#security)
- [Requirements](#requirements)

## Overview

The SMS Harm Reduction Chatbot is an SMS-based application that provides information about harm reduction resources, connects users to hotlines, and sends emergency alerts about risks in the drug supply. The system uses Twilio for SMS communication, Flask for the web framework, PostgreSQL for data storage, and is designed for deployment on Heroku.

This repository is a proof-of-concept communicating resources in Massachusets. If people like the tool then I will work on making the repository configurable to other jurisdictions!

## Project Structure

```
sms-harm-reduction-chatbot/
├── app.py                # Main Flask application entry point
├── chatbot.py            # SMS chatbot logic and Twilio integration
├── state_handlers.py     # Conversation state management
├── chatbot_utils.py      # Utility functions for chatbot operations
├── database.py           # Database models and configuration
├── event_handlers.py     # Event logging functions
├── response_content.py   # SMS response text content
├── website.py            # Web interface routes
├── templates/            # HTML templates
│   ├── base.html
│   ├── onepager.html
│   ├── admin_login.html
│   └── admin_dashboard.html
├── static/               # Static assets (CSS, JS, images)
├── requirements.txt      # Python dependencies
├── Procfile              # Heroku deployment configuration
└── .gitignore            # Git ignore rules
```

Flask Blueprints organize the application into modular components. The `chatbot_blueprint` handles all SMS-related routes (`/sms`), while the `website_blueprint` manages web interface routes (`/onepager`, `/admin_login`, `/admin_dashboard`). This separation improves maintainability and code organization by keeping SMS logic distinct from web interface logic.

## Core Components

### Flask Application (`app.py`)

The main entry point that:
- Initializes the Flask application
- Configures PostgreSQL database connection
- Sets up rate limiting and login management
- Registers blueprints for chatbot and website routes
- Creates database tables on startup (if they don't already exist)

### SMS Chatbot (`chatbot.py`)

Handles SMS interactions via Twilio:
- Processes incoming SMS messages
- Immediately hashes phone number hashing for privacy
- Manages user sessions and state transitions
- Routes messages to appropriate state handlers

### State Management (`state_handlers.py`)

Contains functions for managing conversation states:

| State | Purpose |
|-------|---------|
| `PRE_REGISTRATION` | Initial greeting and opt-in |
| `REGISTRATION` | Handles opt-in/opt-out responses |
| `ASK_RACE_ETHNICITY` | Collects race/ethnicity information |
| `ASK_MULTIRACIAL1` | Collects first racial identity for multiracial users |
| `ASK_MULTIRACIAL2` | Collects second racial identity for multiracial users |
| `ASK_GENDER` | Collects gender information |
| `ASK_GENDER_OTHER` | Handles custom gender input |
| `ASK_AGE_GROUP` | Collects age group information |
| `MAIN_MENU` | Main navigation menu |
| `RETURNING_USER` | Greets returning users and shows main menu |
| `RESOURCE_MENU` | Resource category selection |
| `ZIPCODE_INPUT` | Collects user zipcode for location-based resources |
| `RESOURCE_VIEW` | Individual resource information |
| `HELPLINE_MENU` | Hotline options |
| `HELPLINE_VIEW` | Hotline information |
| `NEW_ALERTS_USER` | Emergency alert subscription |
| `EXISTING_ALERTS_USER` | Alert management for subscribers |

### Utilities (`chatbot_utils.py`)

Helper functions for:
- Phone number hashing (`hash_phone_number`)
- User management (`check_create_user`)
- Session management (`is_session_expired`, `create_user_session`)
- Input processing (`typos_check`)
- Response formatting (`display_program_data`)
- Emergency alert management (`emergency_alerts_checker`)

### Event Logging (`event_handlers.py`)

Comprehensive event tracking for:
- SMS interactions (`event_sms_received`, `event_sms_sent`)
- User actions (`event_create_user`, `event_session_created`)
- Opt-in/opt-out (`event_opt_in`, `event_opt_out`)
- Demographic collection (`event_race_collected`, `event_gender_collected`, `event_age_collected`)
- Service usage (`event_chatbot_service`)
- Resource interactions (`event_resource_view`, `event_page_change`)
- Helpline interactions (`event_helpline_view`)
- Alert management (`event_alerts_subscribe`, `event_alerts_unsubscribe`)

### Response Content (`response_content.py`)

Centralized text content for:
- Greetings and opt-in messages
- Menu options and navigation
- Resource and hotline information
- Emergency alert messages
- Demographic data collection prompts

## Database Models

### Core Models (`database.py`)

- **`SMSUser`**: Stores user information and demographics
- **`SMSUserSession`**: Tracks conversation sessions and state
- **`Event`**: Logs all user interactions and system events
- **`EmergencyAlertUsers`**: Manages alert subscriptions
- **`EmergencyAlerts`**: Stores sent alert messages

## Web Interface

### Website Routes (`website.py`)

- **`/onepager`**: Public information page about the chatbot
- **`/admin_login`**: Admin authentication
- **`/admin_dashboard`**: Emergency alert sending interface
- **`/logout`**: Admin logout

### Templates

Jinja2 Templating provides dynamic HTML generation through template inheritance. The `base.html` template provides a common layout that other templates extend, allowing all pages to share the same header, footer, and styling. Templates display the tool one-pager, admin login, and admin dashboard while eliminating duplicate HTML across pages using `{% extends %}` and `{% block %}` syntax.

- **`base.html`**: Base template with common layout
- **`onepager.html`**: Public information page
- **`admin_login.html`**: Admin login form
- **`admin_dashboard.html`**: Alert sending dashboard

### Static Assets

- **CSS**: Styling for web interface
- **JavaScript**: Interactive features and maintenance mode
- **Images**: Logos and graphics

## Deployment

The application is configured for deployment on Heroku with:
- **`Procfile`**: Heroku deployment configuration
- **Environment variables**: Database URLs, API keys, admin credentials
- **Gunicorn**: Production WSGI server

Easily adaptable to deploy on other types of platforms. 

## Security

- **Phone number hashing**: SHA-256 hashing for user privacy
- **Admin authentication**: Protected admin routes
- **Rate limiting**: Prevents abuse of SMS and web endpoints
- **Input sanitization**: XSS protection for emergency alerts
- **Environment variables**: Secure credential management

## Requirements

### Python Dependencies

Key packages include:
- **Flask**: Web framework
- **Twilio**: SMS communication
- **SQLAlchemy**: Database ORM
- **psycopg2-binary**: PostgreSQL adapter
- **geopandas**: Geographic data processing
- **rapidfuzz**: Fuzzy string matching
- **bleach**: Input sanitization

### Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `TWILIO_ACCOUNT_SID`: Twilio account identifier
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_FROM`: Twilio phone number
- `ADMIN_USERNAME`: Admin login username
- `ADMIN_PASSWORD`: Admin login password

## Getting Started

1. **Set up a Twilio account and phone number** 
2. **Clone the repository**
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Set up environment variables**
5. **Initialize database**: The app creates tables on startup
6. **Run locally**: `python app.py` (Use NGROK for local testing and add the webhook URL to Twilio)
7. **Deploy**: Push to Heroku or other cloud platform (update Twilio webhooks with your Heroku URL)

## Contributions

This is an open-source project! Feel free to contribute or flag any issues!

## License

This project is licensed under the GNU AFFERO GPL - see the [LICENSE](LICENSE) file for details.
