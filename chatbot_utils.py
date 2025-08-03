# This contains helper functions and variables that are used in the chatbot.py and state_handlers.py files.
# It's separated to make the code more readable and maintainable.
from datetime import datetime, timedelta
from database import db, SMSUser, SMSUserSession, EmergencyAlertUsers
from event_handlers import event_create_user, event_session_created
from response_content import emoji_dict, more_resources, resource_view_boilerplate
from rapidfuzz import fuzz
from response_content import not_subscribed_to_alerts_boilerplate, already_subscribed_to_alerts_boilerplate
import os
import hashlib
import pandas as pd
import geopandas as gpd

# Loading the resource data from the csv file
df = pd.read_csv("resources_data.csv")

# Phone Number Hashing Function
# Hashes the phone number to a unique identifier
def hash_phone_number(phone_number):
    # (A fixed salt adds an additional layer of security and uniqueness to the hashed phone number)
    salt = os.environ.get("FIXED_SALT")
    salted_phone_number = salt.encode() + phone_number.encode()
    return hashlib.sha256(salted_phone_number).hexdigest()

# User Management Function
def check_create_user(hashed_phone_number):
    user = SMSUser.query.get(hashed_phone_number)
    # Checks if the user exists in the database, and creates a new user if they don't
    if not user:
        user = SMSUser(hashed_phone_number=hashed_phone_number, first_interaction=datetime.now())
        db.session.add(user)
        db.session.commit()
        event_create_user(hashed_phone_number)
        db.session.commit()
    return user 

# Session Management Functions
def is_session_expired(user_session):
    # Check if the user session is expired based on the last interaction time
    if datetime.now() - user_session.last_interaction <= timedelta(minutes=30):
        user_session.last_interaction = datetime.now()
        db.session.commit()
        return False
    return True
 
def create_user_session(hashed_phone_number):
    # Attempt to retrieve an existing session for the hashed phone number
    user_session = SMSUserSession.query.filter_by(hashed_phone_number=hashed_phone_number).order_by(SMSUserSession.last_interaction.desc()).first()
    # Check the existing user session; decide on the state based on its current state or lack thereof
    if user_session is None or user_session.state in ["REGISTRATION", "OPT-OUT", "ASK_RACE_ETHNICITY", "ASK_MULTIRACIAL1", "ASK_MULTIRACIAL2", "ASK_GENDER", "ASK_GENDER_OTHER", "ASK_AGE_GROUP"]:
        # If no session found or the user previously did not complete the registration process-
        # start a new session with the pre-registration state (they start registration over)
        state = "PRE-REGISTRATION"
    else:
        # Any other state implies returning user, thus moving to the main menu
        state = "RETURNING_USER"
    # Create a new session with the determined state
    new_user_session = SMSUserSession(
        hashed_phone_number=hashed_phone_number,
        state=state,
        last_interaction=datetime.now()
    )
    # Add the new session to the database and commit changes
    db.session.add(new_user_session)
    db.session.commit()
    # Log the event of session creation
    event_session_created(hashed_phone_number, new_user_session.id)
    db.session.commit()
    return new_user_session

# Alert Management Function
def emergency_alerts_checker(phone_number, user_session):
    # Check if the user is in the EmergencyAlertUsers table
    alert_user = EmergencyAlertUsers.query.filter_by(phone_number=phone_number).first()
    # If the user is not in the table, they are a new alerts user
    if alert_user is None:
        # Set the user's session state to 'NEW_ALERTS_USER'
        user_session.state = 'NEW_ALERTS_USER'
        db.session.commit()
        # Return the message indicating the user is not signed up for emergency alerts
        return ("You are not signed up for emergency alerts.\n\n" + not_subscribed_to_alerts_boilerplate) 
    # If the user is in the table, they are an existing alerts user
    else:
        # Set the user's session state to 'EXISTING_ALERTS_USER'
        user_session.state = 'EXISTING_ALERTS_USER'
        db.session.commit()
        # Return the message indicating the user is already signed up for emergency alerts
        return ("You are already signed up for emergency alerts.\n\n" + already_subscribed_to_alerts_boilerplate)

# Input Processing Functions
def typos_check(a, b, ratio=85):
    """Fuzz is a library that allows sfor "fuzzy" matching of strings
    It calculates the ratio of similarity between two strings
    If the ratio is greater than the given threshold, the strings are considered similar 
    """
    return fuzz.ratio(a.lower(), b.lower()) > ratio

def geolocate_resources(resource_category, zipcode):
    # Filter for resources matching the category
    filtered_df = df[df['resource_category'] == resource_category].copy()
    
    # Check if any resources found for this category
    if filtered_df.empty:
        return f" ⚠️ No {resource_category} resources found in the database. Check with the chatbot administrator."
    
    # Ensure filtered_df has longitude and latitude columns
    if 'longitude' not in filtered_df.columns or 'latitude' not in filtered_df.columns:
        return "⚠️Resource data missing longitude and latitude columns. Notify the chatbot administrator there's an issue with the dataset."    
    # Constants
    LL_CRS = "EPSG:4326"      # lon/lat WGS-84
    MA_SPCS = "EPSG:26986"    # NAD83 / Massachusetts Mainland - metres
    
    def build_gdfs(df, zip_path, zipcode):
        """
        Return (resources_gdf, zip_polygon_gdf) in the SAME projected CRS.
        Raises if zipcode not found.
        """
        # --- 1. ZIP polygons ---------------------------------------------------- #
        zip_gdf = gpd.read_file(zip_path)

        target_zip = zip_gdf.loc[zip_gdf["POSTCODE"] == str(zipcode)]
        if target_zip.empty:
            raise ValueError(f"⚠️ MA zipcode {zipcode} not found in shapefil. Check with the chatbot administrator if there's an issue.")

        # project once and cache
        target_zip = target_zip.to_crs(MA_SPCS)

        # --- 2. Resource points ------------------------------------------------- #
        # create points in lon/lat
        points_ll = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
            crs=LL_CRS,
        ).to_crs(MA_SPCS)          # re-project to same CRS as ZIPs

        return points_ll, target_zip

    try:
        resources_gdf, target_zip_gdf = build_gdfs(filtered_df, "./zipcodes_shapefile", zipcode)
    except ValueError as exc:
        return f"ERROR - {exc}"
    except Exception as e:
        return f"Error loading zipcode data: {str(e)}"

    zip_polygon = target_zip_gdf.geometry.iloc[0]
    
    # Distance from ZIP centroid for all rows
    zip_centroid = zip_polygon.centroid
    resources_gdf["distance_miles"] = resources_gdf.distance(zip_centroid) * 0.000621371
    
    # Now build the inside / outside subsets
    inside_mask = resources_gdf.within(zip_polygon)
    inside_resources = resources_gdf.loc[inside_mask]
    outside_resources = resources_gdf.loc[~inside_mask]
    
    # Build response string starting with resources inside zipcode
    response = f"Here are the closest {resource_category} resources to {zipcode}:\n\n---\n"
    
    # Add resources inside zipcode
    for _, row in inside_resources.iterrows():
        name = row.get('organization_name', 'N/A')
        address = row.get('address', 'N/A')
        phone = row.get('phone_number', 'N/A')
        response += f"{name}\n{address}\n{phone}\nDistance: inside zipcode {zipcode}\n---\n"
    
    # Calculate how many more resources we need
    remaining_count = 5 - len(inside_resources)
    
    if remaining_count > 0 and not outside_resources.empty:
        # Get the closest outside resources
        closest_outside = outside_resources.nsmallest(remaining_count, 'distance_miles')
        
        # Add closest outside resources
        for _, row in closest_outside.iterrows():
            name = row.get('organization_name', 'N/A')
            address = row.get('address', 'N/A')
            phone = row.get('phone_number', 'N/A')
            distance_miles = row['distance_miles']
            response += f"{name}\n{address}\n{phone}\nDistance: {distance_miles:.1f} miles away\n---\n"
    
    return response.strip()
