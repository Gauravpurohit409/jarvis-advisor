"""
Google API Service - Gmail & Calendar Integration
Direct API integration without MCP server complexity
"""

import os
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    GOOGLE_CREDENTIALS_PATH, 
    GOOGLE_TOKEN_PATH, 
    GOOGLE_SCOPES,
    GOOGLE_ENABLED
)


class GoogleService:
    """Service for Gmail and Calendar operations with per-user authentication"""
    
    def __init__(self):
        self.creds = None
        self.gmail_service = None
        self.calendar_service = None
        self._authenticated = False
        self._google_available = self._check_google_libs()
        self._user_info = None  # Store logged in user info
    
    def _check_google_libs(self) -> bool:
        """Check if Google API libraries are installed"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            return True
        except ImportError:
            return False
    
    def is_enabled(self) -> bool:
        """Check if Google integration is enabled and credentials exist"""
        return (
            GOOGLE_ENABLED and 
            self._google_available and 
            Path(GOOGLE_CREDENTIALS_PATH).exists()
        )
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        return self._authenticated and self.creds is not None and self.creds.valid
    
    def get_auth_url(self) -> Tuple[str, Any]:
        """
        Get OAuth authorization URL for user to authenticate.
        Returns (auth_url, None) - we don't need the flow object anymore.
        """
        if not self.is_enabled():
            raise ValueError("Google integration not enabled or credentials missing")
        
        import json
        
        # Load client config
        with open(GOOGLE_CREDENTIALS_PATH) as f:
            client_config = json.load(f)
        
        # Get client info (handle both "web" and "installed" formats)
        if "web" in client_config:
            client_info = client_config["web"]
        else:
            client_info = client_config["installed"]
        
        client_id = client_info["client_id"]
        
        # Build auth URL manually
        scopes_str = "%20".join([s.replace(":", "%3A").replace("/", "%2F") for s in GOOGLE_SCOPES])
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri=http://localhost:8501&"
            f"response_type=code&"
            f"scope={scopes_str}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return auth_url, None
    
    def complete_auth_with_code(self, auth_code: str) -> Tuple[bool, str]:
        """
        Complete OAuth flow with authorization code using direct HTTP request.
        Returns (success, error_message)
        """
        if not self.is_enabled():
            return False, "Google integration not enabled"
            
        try:
            import json
            import requests
            from google.oauth2.credentials import Credentials
            
            # Load client config
            with open(GOOGLE_CREDENTIALS_PATH) as f:
                client_config = json.load(f)
            
            # Get client info (handle both "web" and "installed" formats)
            if "web" in client_config:
                client_info = client_config["web"]
            else:
                client_info = client_config["installed"]
            
            client_id = client_info["client_id"]
            client_secret = client_info["client_secret"]
            
            # Exchange code for tokens using direct HTTP POST
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "code": auth_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "http://localhost:8501",
                "grant_type": "authorization_code"
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error_description", error_data.get("error", "Unknown error"))
                print(f"Token exchange failed: {error_data}")
                return False, error_msg
            
            token_data = response.json()
            
            # Create credentials object
            self.creds = Credentials(
                token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=GOOGLE_SCOPES
            )
            
            # Save credentials for future use
            self._save_credentials()
            
            # Initialize services
            self._init_services()
            self._authenticated = True
            
            return True, ""
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Auth error: {e}\n{error_details}")
            return False, str(e)
    
    def complete_auth(self, flow: Any, auth_code: str) -> bool:
        """
        Complete OAuth flow with authorization code.
        Returns True if successful.
        """
        try:
            flow.fetch_token(code=auth_code)
            self.creds = flow.credentials
            
            # Save credentials for future use
            self._save_credentials()
            
            # Initialize services
            self._init_services()
            self._authenticated = True
            
            return True
        except Exception as e:
            print(f"Auth error: {e}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate using saved credentials or return False if user action needed.
        """
        if not self.is_enabled():
            return False
        
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        # Try to load existing token
        if Path(GOOGLE_TOKEN_PATH).exists():
            try:
                self.creds = Credentials.from_authorized_user_file(
                    GOOGLE_TOKEN_PATH, 
                    GOOGLE_SCOPES
                )
            except Exception:
                self.creds = None
        
        # Check if credentials need refresh
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                self._save_credentials()
            except Exception:
                self.creds = None
        
        # If we have valid credentials, initialize services
        if self.creds and self.creds.valid:
            self._init_services()
            self._authenticated = True
            return True
        
        return False
    
    def _save_credentials(self):
        """Save credentials to token file"""
        if self.creds:
            Path(GOOGLE_TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
            with open(GOOGLE_TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())
    
    def _init_services(self):
        """Initialize Gmail and Calendar API services"""
        if self.creds:
            from googleapiclient.discovery import build
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            # Fetch user profile info on login
            self._fetch_user_info()
    
    def _fetch_user_info(self):
        """Fetch the logged in user's profile information"""
        if not self.creds:
            return
        
        try:
            from googleapiclient.discovery import build
            oauth2_service = build('oauth2', 'v2', credentials=self.creds)
            user_info = oauth2_service.userinfo().get().execute()
            self._user_info = {
                'email': user_info.get('email', ''),
                'name': user_info.get('name', ''),
                'given_name': user_info.get('given_name', ''),
                'picture': user_info.get('picture', ''),
                'id': user_info.get('id', '')
            }
        except Exception as e:
            print(f"Error fetching user info: {e}")
            # Fallback to Gmail profile
            try:
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                self._user_info = {
                    'email': profile.get('emailAddress', ''),
                    'name': profile.get('emailAddress', '').split('@')[0],
                    'given_name': '',
                    'picture': '',
                    'id': ''
                }
            except:
                self._user_info = None
    
    def get_logged_in_user(self) -> Optional[Dict[str, str]]:
        """Get the currently logged in user's info"""
        return self._user_info
    
    def logout(self):
        """Logout the current user"""
        self._authenticated = False
        self.creds = None
        self.gmail_service = None
        self.calendar_service = None
        self._user_info = None
        
        # Remove saved token
        if Path(GOOGLE_TOKEN_PATH).exists():
            Path(GOOGLE_TOKEN_PATH).unlink()
    
    # ==================== GMAIL OPERATIONS ====================
    
    def get_user_email(self) -> Optional[str]:
        """Get the authenticated user's email address"""
        if not self.is_authenticated():
            return None
        
        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except Exception:
            return None
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        html: bool = False
    ) -> Tuple[bool, str]:
        """
        Send an email via Gmail.
        Returns (success, message_id or error)
        """
        if not self.is_authenticated():
            return False, "Not authenticated with Google"
        
        try:
            if html:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'html'))
            else:
                message = MIMEText(body)
            
            message['to'] = to
            message['subject'] = subject
            
            # Encode the message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return True, sent.get('id', 'sent')
        
        except Exception as e:
            return False, f"Gmail error: {e}"
    
    def create_draft(
        self, 
        to: str, 
        subject: str, 
        body: str,
        html: bool = False
    ) -> Tuple[bool, str]:
        """
        Create a draft email in Gmail.
        Returns (success, draft_id or error)
        """
        if not self.is_authenticated():
            return False, "Not authenticated with Google"
        
        try:
            if html:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'html'))
            else:
                message = MIMEText(body)
            
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.gmail_service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            return True, draft.get('id', 'created')
        
        except Exception as e:
            return False, f"Gmail error: {e}"
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from inbox"""
        if not self.is_authenticated():
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in email_data.get('payload', {}).get('headers', [])}
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': email_data.get('snippet', '')
                })
            
            return emails
        
        except Exception:
            return []
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails with Gmail query syntax"""
        if not self.is_authenticated():
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in email_data.get('payload', {}).get('headers', [])}
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': email_data.get('snippet', '')
                })
            
            return emails
        
        except Exception:
            return []
    
    # ==================== CALENDAR OPERATIONS ====================
    
    def get_upcoming_events(self, days: int = 7, max_results: int = 20) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        if not self.is_authenticated():
            return []
        
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [{
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'attendees': [a.get('email') for a in event.get('attendees', [])]
            } for event in events]
        
        except Exception:
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        attendee_emails: List[str] = None,
        send_notifications: bool = True
    ) -> Tuple[bool, str]:
        """
        Create a calendar event.
        Returns (success, event_id or error)
        """
        if not self.is_authenticated():
            return False, "Not authenticated with Google"
        
        try:
            # Get local timezone
            import time
            local_tz = time.tzname[0]
            # Map common abbreviations to IANA timezone names
            tz_map = {
                'IST': 'Asia/Kolkata',
                'GMT': 'Europe/London',
                'BST': 'Europe/London',
                'EST': 'America/New_York',
                'PST': 'America/Los_Angeles',
                'UTC': 'UTC',
            }
            timezone = tz_map.get(local_tz, 'Asia/Kolkata')  # Default to IST for India
            
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            if attendee_emails:
                event['attendees'] = [{'email': email} for email in attendee_emails]
            
            created = self.calendar_service.events().insert(
                calendarId='primary',
                body=event,
                sendNotifications=send_notifications
            ).execute()
            
            return True, created.get('id', 'created')
        
        except Exception as e:
            return False, f"Calendar error: {e}"
    
    def find_free_slots(
        self, 
        duration_minutes: int = 60,
        days_ahead: int = 7,
        working_hours: Tuple[int, int] = (9, 17)
    ) -> List[Dict[str, datetime]]:
        """
        Find free time slots in calendar.
        Returns list of {'start': datetime, 'end': datetime} dicts.
        """
        if not self.is_authenticated():
            return []
        
        try:
            # Get existing events
            events = self.get_upcoming_events(days=days_ahead, max_results=50)
            
            # Parse busy times
            busy_times = []
            for event in events:
                start_str = event.get('start')
                end_str = event.get('end')
                if start_str and end_str:
                    try:
                        # Handle both datetime and date-only formats
                        if 'T' in str(start_str):
                            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                            end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                        else:
                            start = datetime.strptime(start_str, '%Y-%m-%d')
                            end = datetime.strptime(end_str, '%Y-%m-%d')
                        busy_times.append((start.replace(tzinfo=None), end.replace(tzinfo=None)))
                    except:
                        pass
            
            # Find free slots
            free_slots = []
            current = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            end_search = current + timedelta(days=days_ahead)
            
            while current < end_search:
                # Skip weekends
                if current.weekday() >= 5:
                    current += timedelta(days=1)
                    current = current.replace(hour=working_hours[0])
                    continue
                
                # Skip outside working hours
                if current.hour < working_hours[0]:
                    current = current.replace(hour=working_hours[0])
                    continue
                if current.hour >= working_hours[1]:
                    current += timedelta(days=1)
                    current = current.replace(hour=working_hours[0])
                    continue
                
                slot_end = current + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with busy times
                is_free = True
                for busy_start, busy_end in busy_times:
                    if not (slot_end <= busy_start or current >= busy_end):
                        is_free = False
                        break
                
                if is_free:
                    free_slots.append({
                        'start': current,
                        'end': slot_end
                    })
                    if len(free_slots) >= 10:  # Limit results
                        break
                
                current += timedelta(minutes=30)
            
            return free_slots
        
        except Exception:
            return []
    
    def delete_event(self, event_id: str) -> Tuple[bool, str]:
        """Delete a calendar event"""
        if not self.is_authenticated():
            return False, "Not authenticated with Google"
        
        try:
            self.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True, "Event deleted"
        except Exception as e:
            return False, f"Error: {e}"


# Singleton instance
google_service = GoogleService()
