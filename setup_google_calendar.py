import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Scopes for Google Calendar API (read/write access)
SCOPES = ['https://www.googleapis.com/auth/calendar']

def setup_google_calendar():
    creds = None
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, prompt user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=creds)
    print("Google Calendar API setup complete.")
    return service

def add_project_event(service, project_name, start_date, end_date):
    # Create an all-day event for the project
    event = {
        'summary': project_name,
        'start': {
            'date': start_date,
            'timeZone': 'America/New_York',
        },
        'end': {
            'date': end_date,
            'timeZone': 'America/New_York',
        },
    }
    
    # Insert the event into the primary calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {project_name} (ID: {event.get('id')})")

if __name__ == '__main__':
    service = setup_google_calendar()
    # Test with Driveway Paving project
    add_project_event(service, 'Driveway Paving', '2025-05-20', '2025-05-25')