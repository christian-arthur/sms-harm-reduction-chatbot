# SMS Chatbot Application

A Flask-based SMS chatbot application that provides resources and emergency alerts through text messaging, with an administrative web interface.

## Features

- **SMS Chatbot**: Interactive SMS-based chatbot using Twilio
- **User Registration**: Multi-step user registration with demographic information
- **Resource Directory**: Browse and search resources by location (zipcode-based)
- **Emergency Alerts**: Administrative system for sending emergency notifications
- **Web Dashboard**: Admin interface for managing alerts and monitoring usage
- **Rate Limiting**: Built-in rate limiting for API protection
- **Database Integration**: PostgreSQL database with SQLAlchemy ORM

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **SMS Service**: Twilio API
- **Authentication**: Flask-Login
- **Rate Limiting**: Flask-Limiter
- **Deployment**: Heroku-ready with Gunicorn
- **Geographic Data**: GeoPandas for zipcode/location handling

## Setup Instructions

### Prerequisites

- Python 3.7+
- PostgreSQL database
- Twilio account with SMS capabilities

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DATABASE_URL=postgresql://username:password@localhost/dbname
   export SECRET_KEY=your-secret-key-here
   export TWILIO_ACCOUNT_SID=your-twilio-account-sid
   export TWILIO_AUTH_TOKEN=your-twilio-auth-token
   ```

4. Initialize the database:
   ```bash
   python app.py
   ```

### Running the Application

#### Local Development
```bash
python app.py
```

#### Production (Heroku)
The application includes a `Procfile` for Heroku deployment:
```bash
git push heroku main
```

## Project Structure

```
├── app.py                 # Main Flask application entry point
├── chatbot.py            # SMS chatbot blueprint and routes
├── website.py            # Web interface blueprint and routes
├── database.py           # Database models and configuration
├── chatbot_utils.py      # Utility functions for chatbot logic
├── state_handlers.py     # State management for chatbot conversations
├── event_handlers.py     # Event handling logic
├── response_content.py   # Response templates and content
├── templates/            # HTML templates for web interface
├── static/              # Static assets (CSS, JS, images)
├── zipcodes_shapefile/  # Geographic data for location services
├── resources_data.csv   # Resource directory data
└── requirements.txt     # Python dependencies
```

## Usage

### SMS Interface
Users can interact with the chatbot by sending SMS messages to the configured Twilio phone number. The bot guides users through:
- Registration process
- Resource discovery by location
- Emergency alert subscriptions

### Web Interface
- Access the admin dashboard at `/onepager`
- Login required for administrative functions
- Manage emergency alerts and view user analytics

## Configuration

Key configuration options in `app.py`:
- Database URL configuration for local vs. production
- Secret key for session management
- Rate limiting settings

## License

See `LICENSE` file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request