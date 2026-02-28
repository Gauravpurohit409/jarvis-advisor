"""
Jarvis - Proactive Financial Advisor Assistant
Main Streamlit Application
"""

import streamlit as st
from datetime import date, datetime, timedelta
import json

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Jarvis - Advisor Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports after page config
from services.client_service import ClientService
from services.llm_service import LLMService
from services.vector_store import VectorStoreService, get_vector_store
from services.alerts_service import AlertsService, alerts_service
from services.compliance_service import ComplianceService, compliance_service, ComplianceStatus
from services.dismissal_service import dismissal_service
from services.google_service import google_service
from data.schema import AlertPriority, AlertType
from config import REQUIRE_LOGIN


# ============== LOGIN PAGE ==============

def render_login_page():
    """Render the Google login page for unauthenticated users"""
    
    # Check for OAuth callback (code in URL params)
    params = st.query_params
    auth_code = params.get("code")
    
    # If we got a code from Google redirect, process it
    if auth_code:
        # Prevent double-processing - check if we already processed this code
        if st.session_state.get("_last_auth_code") == auth_code:
            st.error("❌ This authorization code has already been used. Please try again.")
            if st.button("🔄 Start Over"):
                st.session_state.pop("_last_auth_code", None)
                st.query_params.clear()
                st.rerun()
            return
        
        # Mark this code as being processed
        st.session_state["_last_auth_code"] = auth_code
        
        # Clear URL params FIRST to prevent reprocessing on rerun
        st.query_params.clear()
        
        with st.spinner("🔄 Completing sign-in..."):
            try:
                success, error_msg = google_service.complete_auth_with_code(auth_code)
                if success:
                    # Clear login flow state
                    if "login_flow" in st.session_state:
                        del st.session_state["login_flow"]
                    if "login_auth_url" in st.session_state:
                        del st.session_state["login_auth_url"]
                    st.session_state.pop("_last_auth_code", None)
                    st.success("🎉 Welcome to Jarvis!")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state.pop("_last_auth_code", None)
                    st.error(f"❌ Authentication failed: {error_msg}")
                    if st.button("🔄 Try Again"):
                        st.rerun()
            except Exception as e:
                st.session_state.pop("_last_auth_code", None)
                st.error(f"❌ Auth error: {e}")
                if st.button("🔄 Try Again"):
                    st.rerun()
        return
    
    # Center the login content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 50px 0;">
            <h1>🤖 Jarvis</h1>
            <p style="font-size: 1.2em; color: #666;">Your Proactive Financial Advisor Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Check if Google integration is configured
        if not google_service.is_enabled():
            st.error("⚠️ Google Sign-In is not configured")
            
            # Debug info
            from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_CREDENTIALS_PATH
            from pathlib import Path
            with st.expander("🔍 Debug Info"):
                st.write(f"CLIENT_ID set: {bool(GOOGLE_CLIENT_ID)}")
                st.write(f"CLIENT_SECRET set: {bool(GOOGLE_CLIENT_SECRET)}")
                st.write(f"REDIRECT_URI: {GOOGLE_REDIRECT_URI}")
                st.write(f"Credentials file exists: {Path(GOOGLE_CREDENTIALS_PATH).exists()}")
                st.write(f"Google libs available: {google_service._google_available}")
            
            with st.expander("📋 Admin Setup Required"):
                st.markdown("""
                **For administrators:**
                
                1. Create a [Google Cloud Project](https://console.cloud.google.com/)
                2. Enable **Gmail API** and **Google Calendar API**
                3. Create OAuth 2.0 credentials (Web application)
                4. Add `http://localhost:8501` as authorized redirect URI
                5. Download `client_secret.json` to `credentials/` folder
                
                **For Streamlit Cloud:**
                Add these to your app's Secrets:
                ```
                GOOGLE_CLIENT_ID = "your_client_id"
                GOOGLE_CLIENT_SECRET = "your_client_secret"
                GOOGLE_REDIRECT_URI = "https://your-app.streamlit.app/"
                ```
                """)
            return
        
        # Check if we're in the middle of OAuth flow (waiting for redirect)
        if "login_flow" in st.session_state and not auth_code:
            st.info("🔄 Waiting for Google sign-in...")
            st.markdown("If the sign-in window didn't open, click the button below:")
            
            auth_url = st.session_state.get("login_auth_url", "")
            st.link_button("🔗 Open Google Sign-In", auth_url, use_container_width=True)
            
            if st.button("❌ Cancel Sign-In", use_container_width=True):
                del st.session_state["login_flow"]
                if "login_auth_url" in st.session_state:
                    del st.session_state["login_auth_url"]
                st.rerun()
        else:
            # Show login button
            st.markdown("""
            <div style="text-align: center; padding: 30px;">
                <p>Sign in with your Google account to access Jarvis</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 Sign in with Google", type="primary", use_container_width=True):
                try:
                    auth_url, flow = google_service.get_auth_url()
                    st.session_state.login_flow = flow
                    st.session_state.login_auth_url = auth_url
                    # Redirect to Google
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error starting login: {e}")
            
            st.markdown("---")
            
            # Skip login option
            if st.button("👤 Continue as Guest", use_container_width=True):
                st.session_state.guest_mode = True
                st.rerun()
            
            st.caption("Guest mode: Email & Calendar features will be disabled")
            
            st.markdown("""
            <div style="text-align: center; padding: 20px; color: #888; font-size: 0.9em;">
                <p>By signing in with Google, you allow Jarvis to:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Send emails on your behalf</li>
                    <li>Access your calendar</li>
                    <li>View your email address</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


def is_user_logged_in() -> bool:
    """Check if user is logged in"""
    if not REQUIRE_LOGIN:
        return True
    # Allow guest mode
    if st.session_state.get("guest_mode"):
        return True
    return google_service.is_authenticated()


def get_current_user():
    """Get the current logged-in user info"""
    return google_service.get_logged_in_user()


# ============== INITIALIZATION ==============

@st.cache_resource
def init_services():
    """Initialize services (cached)"""
    client_service = ClientService()
    llm_service = LLMService()
    vector_store = get_vector_store()
    
    # Index clients if vector store is empty or client count changed
    if vector_store.is_available():
        clients = client_service.get_all_clients()
        # Get unique client IDs from vector store
        existing_docs = vector_store.collection.count()
        # Re-index if empty or if client count doesn't match indexed clients
        # Each client has at least 1 document (overview), so if docs < clients, reindex needed
        if existing_docs == 0 or existing_docs < len(clients):
            vector_store.clear_collection()
            vector_store.index_all_clients(clients)
    
    return client_service, llm_service, vector_store


# Valid page names for URL routing
VALID_PAGES = {"dashboard", "alerts", "chat", "compliance", "clients", "emails"}


def sync_url_to_state():
    """Read URL query params and sync to session state (on page load)"""
    params = st.query_params
    page = params.get("page", "dashboard")
    
    if page in VALID_PAGES:
        if "current_view" not in st.session_state or st.session_state.get("_url_initialized") != True:
            st.session_state.current_view = page
            st.session_state._url_initialized = True
    
    # Also check for client_id in URL
    client_id = params.get("client")
    if client_id and "selected_client" not in st.session_state:
        st.session_state.selected_client = client_id


def sync_state_to_url():
    """Update URL query params to match current session state"""
    current_view = st.session_state.get("current_view", "dashboard")
    selected_client = st.session_state.get("selected_client")
    
    new_params = {"page": current_view}
    
    # Add client ID to URL if viewing a specific client
    if selected_client and current_view == "clients":
        new_params["client"] = selected_client
    
    # Only update if changed to avoid unnecessary reruns
    current_params = dict(st.query_params)
    if current_params.get("page") != new_params.get("page") or current_params.get("client") != new_params.get("client"):
        st.query_params.update(new_params)


def navigate_to(view: str, client_id: str = None, **kwargs):
    """Navigate to a view and update URL"""
    st.session_state.current_view = view
    if client_id:
        st.session_state.selected_client = client_id
    # Update any additional state
    for key, value in kwargs.items():
        st.session_state[key] = value
    # URL will be synced in main()
    st.rerun()


def init_session_state():
    """Initialize session state variables"""
    # Sync URL to state first (for initial page load / bookmarks)
    sync_url_to_state()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    if "current_view" not in st.session_state:
        st.session_state.current_view = "dashboard"
    if "client_filter" not in st.session_state:
        st.session_state.client_filter = None


# ============== UI COMPONENTS ==============

def render_sidebar(client_service: ClientService):
    """Render sidebar with navigation and client list"""
    with st.sidebar:
        st.title("🤖 Jarvis")
        st.caption("Proactive Advisor Assistant")
        
        # Show logged-in user info at the top
        if REQUIRE_LOGIN and is_user_logged_in():
            user = get_current_user()
            if user:
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 10px; background: #f0f2f6; border-radius: 8px; margin-bottom: 10px;">
                    <img src="{user.get('picture', '')}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;" onerror="this.style.display='none'">
                    <div>
                        <strong>{user.get('name', user.get('email', 'User'))}</strong><br>
                        <small style="color: #666;">{user.get('email', '')}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
                    google_service.logout()
                    st.rerun()
                
                st.divider()
        
        # Navigation using buttons for better state control
        st.subheader("Navigation")
        
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("🚨 Alerts", "alerts"),
            ("💬 Chat", "chat"),
            ("🏛️ Compliance", "compliance"),
            ("👥 Clients", "clients"),
            ("📧 Email Drafts", "emails"),
            ("⚙️ Settings", "settings"),
        ]
        
        current = st.session_state.get("current_view", "dashboard")
        
        for label, key in nav_items:
            btn_label = f"▸ {label}" if current == key else label
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_view = key
                st.rerun()
        
        st.divider()
        
        # Quick Stats - Clickable
        st.subheader("📈 Quick Stats")
        briefing = client_service.get_daily_briefing_data()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"👥 {briefing['total_clients']}", key="stat_total", help="View all clients", use_container_width=True):
                st.session_state.client_filter = "all"
                st.session_state.current_view = "clients"
                st.rerun()
            st.caption("Total Clients")
            
            if st.button(f"⚠️ {len(briefing['reviews_overdue'])}", key="stat_overdue", help="View overdue reviews", use_container_width=True):
                st.session_state.client_filter = "reviews_overdue"
                st.session_state.current_view = "clients"
                st.rerun()
            st.caption("Reviews Overdue")
        with col2:
            if st.button(f"📞 {len(briefing['dormant_90_days'])}", key="stat_dormant", help="View dormant clients", use_container_width=True):
                st.session_state.client_filter = "dormant"
                st.session_state.current_view = "clients"
                st.rerun()
            st.caption("Dormant (90d)")
            
            if st.button(f"📋 {len(briefing['pending_follow_ups'])}", key="stat_followups", help="View pending follow-ups", use_container_width=True):
                st.session_state.client_filter = "pending_followups"
                st.session_state.current_view = "clients"
                st.rerun()
            st.caption("Pending Follow-ups")
        
        st.divider()
        
        # Quick Client Search (by name)
        st.subheader("🔍 Search")
        search_query = st.text_input("Search by name...", placeholder="Name", key="name_search")
        
        if search_query:
            results = client_service.search_by_name(search_query)
            for client in results[:5]:
                if st.button(f"{client.full_name}", key=f"search_{client.id}"):
                    st.session_state.selected_client = client.id
                    st.session_state.current_view = "clients"
        
        # Semantic Search
        st.caption("🧠 Smart Search")
        semantic_query = st.text_input("Natural language...", placeholder="e.g. worried about retirement", key="semantic_search")
        
        if semantic_query and 'vector_store' in st.session_state:
            vs = st.session_state.vector_store
            if vs and vs.is_available():
                client_ids = vs.search_clients(semantic_query, n_results=5)
                if client_ids:
                    for cid in client_ids:
                        client = client_service.get_client_by_id(cid)
                        if client:
                            if st.button(f"🎯 {client.full_name}", key=f"semantic_{client.id}"):
                                st.session_state.selected_client = client.id
                                st.session_state.current_view = "clients"
                else:
                    st.caption("No matches found")
        
        st.divider()
        
        # LLM Status
        st.caption(f"LLM: {st.session_state.get('llm_provider', 'Loading...')}")
        
        # Inactive Clients Recovery Section
        inactive_clients = dismissal_service.get_inactive_clients_with_names()
        if inactive_clients:
            st.divider()
            with st.expander(f"👻 Inactive Clients ({len(inactive_clients)})", expanded=False):
                st.caption("Clients marked as 'not with us anymore'")
                for client_id, client_name in inactive_clients.items():
                    col_name, col_btn = st.columns([3, 1])
                    with col_name:
                        st.write(client_name)
                    with col_btn:
                        if st.button("↩️", key=f"reactivate_{client_id}", help="Reactivate client"):
                            dismissal_service.reactivate_client(client_id)
                            st.rerun()

def get_time_of_day() -> str:
    """Get time of day category for proactive messaging"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 14:
        return "afternoon_early"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 22:
        return "night"
    else:  # 22:00 - 4:59
        return "late_night"


def get_greeting_date_key() -> str:
    """Get today's date as a key for tracking daily greetings"""
    return date.today().isoformat()


def should_show_greeting() -> bool:
    """Check if we should show the proactive greeting (once per day only)"""
    today_key = get_greeting_date_key()
    last_greeting_date = st.session_state.get("last_greeting_date")
    return last_greeting_date != today_key


def mark_greeting_shown():
    """Mark that we've shown the greeting for today"""
    st.session_state.last_greeting_date = get_greeting_date_key()


def parse_email_request(user_message: str) -> dict:
    """
    Parse if the user is requesting to send an email.
    Returns email info if detected, None otherwise.
    """
    import re
    
    msg_lower = user_message.lower()
    
    # Check for email-related words
    has_mail_word = any(w in msg_lower for w in ["email", "mail", "e-mail"])
    has_send_word = any(w in msg_lower for w in ["send", "draft", "write", "compose"])
    
    # Intent: has both a send action AND mail word
    has_email_intent = has_mail_word and has_send_word
    
    if not has_email_intent:
        return None
    
    result = {
        "detected": True,
        "recipient_email": None,
        "recipient_name": None,
        "email_type": "general",
    }
    
    # Extract email if present
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
    if email_match:
        result["recipient_email"] = email_match.group()
    
    # Detect email type
    if any(w in user_message.lower() for w in ["birthday", "wish"]):
        result["email_type"] = "birthday"
    elif any(w in user_message.lower() for w in ["review", "annual"]):
        result["email_type"] = "review_reminder"
    elif any(w in user_message.lower() for w in ["follow up", "follow-up"]):
        result["email_type"] = "follow_up"
    elif any(w in user_message.lower() for w in ["check in", "check-in", "checking in"]):
        result["email_type"] = "check_in"
    
    return result


def extract_email_content(llm_response: str) -> dict:
    """Extract subject and body from LLM-generated email response"""
    import re
    
    subject = ""
    body = ""
    
    # Try to extract subject line
    subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', llm_response, re.IGNORECASE)
    if subject_match:
        subject = subject_match.group(1).strip()
    
    # Get everything after the subject line as body
    if subject_match:
        body_start = subject_match.end()
        body = llm_response[body_start:].strip()
    else:
        body = llm_response.strip()
    
    # Clean up body - remove markdown artifacts
    body = body.replace("---", "").strip()
    
    # Replace [Advisor] placeholder with actual logged-in user's name
    user_info = google_service.get_logged_in_user()
    if user_info:
        advisor_name = user_info.get("name") or user_info.get("given_name") or user_info.get("email", "").split("@")[0]
        body = body.replace("[Advisor]", advisor_name)
        body = body.replace("[Your Name]", advisor_name)
        body = body.replace("[Advisor Name]", advisor_name)
    
    return {"subject": subject, "body": body}


def render_email_send_form(email_info: dict, draft_content: dict):
    """Render a form to confirm and send an email"""
    st.markdown("---")
    st.subheader("📧 Send Email")
    
    with st.form("send_email_form"):
        recipient = st.text_input(
            "To", 
            value=email_info.get("recipient_email", ""),
            placeholder="recipient@email.com"
        )
        
        subject = st.text_input(
            "Subject",
            value=draft_content.get("subject", "")
        )
        
        body = st.text_area(
            "Message",
            value=draft_content.get("body", ""),
            height=200
        )
        
        col1, col2 = st.columns(2)
        with col1:
            send_btn = st.form_submit_button("📤 Send Email", type="primary", use_container_width=True)
        with col2:
            save_draft_btn = st.form_submit_button("💾 Save as Draft", use_container_width=True)
        
        if send_btn:
            if not recipient:
                st.error("Please enter a recipient email")
            elif not subject:
                st.error("Please enter a subject")
            else:
                success, result = google_service.send_email(
                    to=recipient,
                    subject=subject,
                    body=body
                )
                if success:
                    st.success(f"✅ Email sent to {recipient}!")
                    st.session_state.pop("pending_email", None)
                    st.balloons()
                else:
                    st.error(f"❌ Failed to send: {result}")
        
        if save_draft_btn:
            if recipient and subject:
                success, result = google_service.create_draft(
                    to=recipient,
                    subject=subject,
                    body=body
                )
                if success:
                    st.success("✅ Draft saved to Gmail!")
                    st.session_state.pop("pending_email", None)
                else:
                    st.error(f"❌ Failed to save draft: {result}")


def parse_scheduling_request(user_message: str, llm_response: str) -> dict:
    """
    Parse if the user is requesting to schedule a meeting.
    Returns scheduling info if detected, None otherwise.
    """
    import re
    
    user_lower = user_message.lower()
    
    # If this is an email request, don't treat it as scheduling
    email_keywords = ["send email", "send an email", "email to", "send a mail", "send mail", 
                      "write email", "draft and send", "birthday wish", "wish mail"]
    if any(kw in user_lower for kw in email_keywords):
        return None
    
    # Keywords indicating scheduling intent (only in user message, not response)
    schedule_keywords = ["schedule", "book a meeting", "book meeting", "set up a call", 
                         "schedule a call", "calendar event", "book a call", "meeting with"]
    has_schedule_intent = any(kw in user_lower for kw in schedule_keywords)
    
    if not has_schedule_intent:
        return None
    
    # Try to extract details from the message
    result = {
        "detected": True,
        "client_name": None,
        "client_email": None,
        "date": None,
        "time": None,
        "duration": 60,  # default 60 minutes
        "title": None
    }
    
    # Extract email if present
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
    if email_match:
        result["client_email"] = email_match.group()
    
    # Extract date patterns (e.g., "March 1st", "tomorrow", "next Monday")
    date_patterns = [
        r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december))',
        r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?)',
        r'(\d{1,2}/\d{1,2}/\d{2,4})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, user_message.lower())
        if match:
            result["date"] = match.group(1)
            break
    
    # Extract time patterns (e.g., "10am", "2:30 PM", "14:00")
    time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', user_message.lower())
    if time_match:
        result["time"] = time_match.group(1)
    
    return result


def render_scheduling_form(scheduling_info: dict, client_service: ClientService):
    """Render a form to complete scheduling a meeting"""
    st.markdown("---")
    st.subheader("📅 Schedule Meeting")
    
    with st.form("schedule_meeting_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Meeting Title", value=scheduling_info.get("title", "Client Meeting"))
            
            # Date picker - default to extracted date or tomorrow
            default_date = date.today() + timedelta(days=1)
            if scheduling_info.get("date"):
                # Try to parse the extracted date
                try:
                    from dateutil import parser
                    parsed = parser.parse(scheduling_info["date"], fuzzy=True)
                    default_date = parsed.date()
                except:
                    pass
            
            meeting_date = st.date_input("Date", value=default_date)
        
        with col2:
            # Time picker
            default_time = datetime.strptime("10:00", "%H:%M").time()
            if scheduling_info.get("time"):
                try:
                    from dateutil import parser
                    parsed = parser.parse(scheduling_info["time"], fuzzy=True)
                    default_time = parsed.time()
                except:
                    pass
            
            meeting_time = st.time_input("Time", value=default_time)
            duration = st.selectbox("Duration", [30, 45, 60, 90, 120], index=2)
        
        # Attendee email
        attendee_email = st.text_input(
            "Attendee Email", 
            value=scheduling_info.get("client_email", ""),
            placeholder="client@email.com"
        )
        
        description = st.text_area("Description (optional)", placeholder="Meeting notes or agenda...")
        
        submitted = st.form_submit_button("📅 Create Calendar Event", type="primary", use_container_width=True)
        
        if submitted:
            if not attendee_email:
                st.error("Please enter an attendee email")
            else:
                # Create the event
                start_datetime = datetime.combine(meeting_date, meeting_time)
                end_datetime = start_datetime + timedelta(minutes=duration)
                
                success, result = google_service.create_event(
                    summary=title,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    description=description,
                    attendee_emails=[attendee_email] if attendee_email else [],
                    send_notifications=True
                )
                
                if success:
                    st.success(f"✅ Meeting scheduled! Calendar invite sent to {attendee_email}")
                    st.session_state.pop("pending_schedule", None)
                    st.balloons()
                else:
                    st.error(f"❌ Failed to create event: {result}")


def render_chat(client_service: ClientService, llm_service: LLMService, vector_store: VectorStoreService):
    """Render chat interface with proactive intelligence"""
    st.header("💬 Chat with Jarvis")
    
    # Store LLM provider name
    st.session_state.llm_provider = llm_service.provider_name
    
    # Show vector store status
    if vector_store.is_available():
        st.caption(f"🧠 Semantic search active ({vector_store.collection.count()} documents indexed)")
    
    # Generate proactive greeting ONCE PER DAY only
    if should_show_greeting() and not st.session_state.messages:
        clients = client_service.get_all_clients()
        all_alerts = alerts_service.generate_all_alerts(clients)
        
        # Get proactive nudge with dismissals applied
        nudge_data = alerts_service.get_proactive_nudge(
            alerts=all_alerts,
            dismissed_alerts=dismissal_service.get_dismissed_alerts(),
            inactive_clients=dismissal_service.get_inactive_clients(),
            time_of_day=get_time_of_day()
        )
        
        # Add proactive greeting as assistant message
        if nudge_data["total_urgent"] > 0 or nudge_data["total_warning"] > 0:
            greeting = nudge_data["formatted_nudge"]
            st.session_state.messages.append({
                "role": "assistant", 
                "content": greeting,
                "type": "greeting",
                "nudge_data": nudge_data
            })
            mark_greeting_shown()
            st.session_state.current_nudge_data = nudge_data
    
    # Quick action buttons - set pending message and rerun
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🌅 Daily Briefing", use_container_width=True):
            st.session_state.pending_chat_message = "Give me my daily briefing. What should I focus on today?"
            st.rerun()
    with col2:
        if st.button("⚠️ Overdue Reviews", use_container_width=True):
            st.session_state.pending_chat_message = "Which clients have overdue annual reviews?"
            st.rerun()
    with col3:
        if st.button("📞 Who to Call", use_container_width=True):
            st.session_state.pending_chat_message = "Which clients should I call this week? Prioritize by urgency."
            st.rerun()
    with col4:
        if st.button("🎂 Upcoming Birthdays", use_container_width=True):
            st.session_state.pending_chat_message = "Show me upcoming client birthdays in the next 30 days."
            st.rerun()
    
    st.divider()
    
    # Check for pending message from quick action buttons
    pending_message = st.session_state.pop("pending_chat_message", None)
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Add action buttons for greeting messages
                if message.get("type") == "greeting" and message.get("nudge_data"):
                    nudge_data = message["nudge_data"]
                    render_greeting_actions(nudge_data, client_service)
    
    # Get prompt from either chat input or pending message
    prompt = st.chat_input("Ask Jarvis anything about your clients...")
    
    # Use pending message if no direct input
    if pending_message and not prompt:
        prompt = pending_message
    
    # Process the prompt
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get context from multiple sources
                    briefing_data = client_service.get_daily_briefing_data()
                    
                    # Use semantic search for relevant context
                    semantic_context = ""
                    if vector_store.is_available():
                        semantic_context = vector_store.get_relevant_context(prompt, n_results=5)
                    
                    # Combine with keyword-based context
                    keyword_context = format_chat_context(briefing_data, client_service, prompt)
                    
                    # Add proactive nudge context for specific client mentions
                    proactive_context = get_client_proactive_context(prompt, client_service)
                    
                    full_context = keyword_context
                    if semantic_context:
                        full_context += "\n\n" + semantic_context
                    if proactive_context:
                        full_context += "\n\n" + proactive_context
                    
                    # Handle "tell me more" expansion
                    if any(phrase in prompt.lower() for phrase in ["tell me more", "more details", "expand", "what else"]):
                        nudge_data = st.session_state.get("current_nudge_data")
                        if nudge_data:
                            full_context += "\n\n--- EXPANDED ALERT DETAILS ---\n"
                            for alert in nudge_data.get("red_alerts", [])[:5]:
                                full_context += f"\nURGENT - {alert.client_name}:\n{alert.description}\n"
                            for alert in nudge_data.get("yellow_alerts", [])[:5]:
                                full_context += f"\nUPCOMING - {alert.client_name}:\n{alert.description}\n"
                    
                    # Generate response - filter conversation history to only include serializable data
                    clean_history = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.messages[:-1][-6:]
                    ]
                    response = llm_service.chat(
                        user_message=prompt,
                        context=full_context,
                        conversation_history=clean_history
                    )
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Check if this was an email request and show email form
                    email_info = parse_email_request(prompt)
                    is_email_request = email_info and email_info.get("detected")
                    
                    if is_email_request:
                        if google_service.is_authenticated():
                            # Extract email content from LLM response
                            draft_content = extract_email_content(response)
                            st.session_state.pending_email = {
                                "email_info": email_info,
                                "draft_content": draft_content
                            }
                        else:
                            st.warning("🔐 To send emails, please sign in with Google. Go to sidebar and click 'Sign in with Google'.")
                    
                    # Check if this was a scheduling request (but NOT if it's an email request)
                    if not is_email_request:
                        scheduling_info = parse_scheduling_request(prompt, response)
                        if scheduling_info and scheduling_info.get("detected"):
                            if google_service.is_authenticated():
                                st.session_state.pending_schedule = scheduling_info
                            else:
                                st.warning("🔐 To schedule meetings, please sign in with Google. Go to sidebar and click 'Sign in with Google'.")
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Chat error: {type(e).__name__}: {error_msg}")  # Log to terminal
                    if "connection" in error_msg.lower() or "api" in error_msg.lower() or "APIConnectionError" in str(type(e)):
                        st.error("⚠️ Connection error. Please check your internet connection and try again.")
                    else:
                        st.error(f"⚠️ Error: {error_msg}")
                    # Remove the pending user message from history
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()
    
    # Clear chat button (resets for new session, but greeting won't show again today)
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.current_nudge_data = None
            st.session_state.pop("pending_schedule", None)
            st.session_state.pop("pending_email", None)
            st.rerun()
    
    # Show email form if pending
    if st.session_state.get("pending_email"):
        pending_email = st.session_state.pending_email
        render_email_send_form(
            pending_email.get("email_info", {}), 
            pending_email.get("draft_content", {})
        )
    
    # Show scheduling form if pending
    if st.session_state.get("pending_schedule"):
        render_scheduling_form(st.session_state.pending_schedule, client_service)


def render_greeting_actions(nudge_data: dict, client_service: ClientService):
    """Render action buttons for the proactive greeting message"""
    # Only render if we're on the chat page
    if st.session_state.get("current_view") != "chat":
        return
        
    st.markdown("---")
    
    # Show counts
    red_count = len(nudge_data.get("red_alerts", []))
    yellow_count = len(nudge_data.get("yellow_alerts", []))
    
    # Use unique timestamp-based key prefix to avoid conflicts
    key_prefix = f"greet_{date.today().isoformat()}"
    
    # Action buttons row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Tell me more", key=f"{key_prefix}_expand", use_container_width=True):
            st.session_state.pending_chat_message = "Tell me more details about these urgent items"
            st.rerun()
    
    with col2:
        if red_count > 0:
            if st.button(f"📧 Draft emails ({red_count})", key=f"{key_prefix}_draft", use_container_width=True):
                # Go to first urgent client's email draft
                first_alert = nudge_data["red_alerts"][0]
                st.session_state.draft_for = first_alert.client_id
                st.session_state.draft_type = _get_email_type_for_alert(first_alert.alert_type)
                st.session_state.current_view = "emails"
                st.rerun()
    
    with col3:
        if st.button("🚨 View all alerts", key=f"{key_prefix}_alerts", use_container_width=True):
            st.session_state.current_view = "alerts"
            st.rerun()
    
    # Quick client links for urgent items
    if red_count > 0:
        st.caption("**Quick actions for urgent items:**")
        for idx, alert in enumerate(nudge_data["red_alerts"][:3]):
            col_name, col_email, col_view = st.columns([2, 1, 1])
            with col_name:
                st.write(f"🔴 {alert.client_name}")
            with col_email:
                if st.button("📧", key=f"{key_prefix}_email_{idx}", help="Draft email"):
                    st.session_state.draft_for = alert.client_id
                    st.session_state.draft_type = _get_email_type_for_alert(alert.alert_type)
                    st.session_state.current_view = "emails"
                    st.rerun()
            with col_view:
                if st.button("👤", key=f"{key_prefix}_view_{idx}", help="View client"):
                    st.session_state.selected_client = alert.client_id
                    st.session_state.current_view = "clients"
                    st.rerun()
    
    # Expandable section for yellow alerts (upcoming items)
    if yellow_count > 0:
        with st.expander(f"🟡 Show {yellow_count} upcoming items (next 2 weeks)", expanded=False):
            for idx, alert in enumerate(nudge_data["yellow_alerts"][:10]):
                col_name, col_type, col_action = st.columns([2, 1, 1])
                with col_name:
                    st.write(f"🟡 {alert.client_name}")
                with col_type:
                    st.caption(alert.alert_type.value.replace("_", " ").title())
                with col_action:
                    if st.button("📧", key=f"{key_prefix}_yellow_email_{idx}", help="Draft email"):
                        st.session_state.draft_for = alert.client_id
                        st.session_state.draft_type = _get_email_type_for_alert(alert.alert_type)
                        st.session_state.current_view = "emails"
                        st.rerun()
            if yellow_count > 10:
                if st.button(f"...and {yellow_count - 10} more → View all in Alerts", key=f"{key_prefix}_view_more_alerts", use_container_width=True):
                    # Pass the yellow alert IDs to filter on the alerts page
                    st.session_state.alerts_filter_ids = [a.id for a in nudge_data["yellow_alerts"]]
                    st.session_state.alerts_filter_label = "🟡 Upcoming items (next 2 weeks)"
                    st.session_state.current_view = "alerts"
                    st.rerun()


def get_client_proactive_context(user_message: str, client_service: ClientService) -> str:
    """
    Get proactive nudges for any client mentioned in the user's message.
    Injects RED/YELLOW alerts for that client into context.
    """
    message_lower = user_message.lower()
    context_parts = []
    
    for client in client_service.get_all_clients():
        if client.last_name.lower() in message_lower or client.first_name.lower() in message_lower:
            # Skip inactive clients
            if dismissal_service.is_client_inactive(client.id):
                continue
            
            # Get this client's alerts
            all_alerts = alerts_service.generate_all_alerts([client])
            client_nudges = alerts_service.get_client_nudges(
                client.id, 
                all_alerts,
                dismissed_alerts=dismissal_service.get_dismissed_alerts()
            )
            
            if client_nudges:
                context_parts.append(f"\n--- PROACTIVE ALERTS FOR {client.full_name.upper()} ---")
                context_parts.append("(Mention these naturally in your response if relevant)")
                for alert in client_nudges[:3]:  # Max 3 per client
                    urgency = "🔴 URGENT" if alert.days_until_due <= 5 else "🟡 UPCOMING"
                    context_parts.append(f"{urgency}: {alert.title} - {alert.description[:100]}")
            break  # Only process first matched client
    
    return "\n".join(context_parts)


def format_chat_context(briefing_data: dict, client_service: ClientService, user_message: str) -> str:
    """Format context for chat based on user message"""
    context_parts = []
    
    context_parts.append(f"Today's date: {date.today().strftime('%A, %d %B %Y')}")
    context_parts.append(f"Total clients: {briefing_data['total_clients']}")
    
    # Add relevant context based on query keywords
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["briefing", "today", "morning", "focus", "priority"]):
        context_parts.append("\n--- BRIEFING DATA ---")
        if briefing_data['reviews_overdue']:
            context_parts.append(f"Overdue reviews: {len(briefing_data['reviews_overdue'])}")
            for c in briefing_data['reviews_overdue'][:5]:
                context_parts.append(f"  - {c.full_name} (due: {c.compliance.next_review_due})")
        
        if briefing_data['overdue_follow_ups']:
            context_parts.append(f"Overdue follow-ups: {len(briefing_data['overdue_follow_ups'])}")
            for c in briefing_data['overdue_follow_ups'][:3]:
                for f in c.overdue_follow_ups[:1]:
                    context_parts.append(f"  - {c.full_name}: {f.commitment}")
    
    if any(word in message_lower for word in ["birthday", "birthdays", "milestone"]):
        context_parts.append("\n--- UPCOMING BIRTHDAYS ---")
        for b in briefing_data['upcoming_birthdays'][:10]:
            milestone = " [MILESTONE - 65!]" if b['is_milestone'] else ""
            context_parts.append(f"  - {b['client'].full_name}: turning {b['turning_age']} on {b['date']}{milestone}")
    
    if any(word in message_lower for word in ["call", "contact", "dormant", "reach out"]):
        context_parts.append("\n--- CLIENTS NEEDING CONTACT ---")
        for c in briefing_data['dormant_90_days'][:8]:
            concerns = ", ".join([con.topic for con in c.active_concerns]) if c.active_concerns else "none noted"
            context_parts.append(f"  - {c.full_name}: {c.days_since_last_contact} days ago | Concerns: {concerns}")
    
    if any(word in message_lower for word in ["review", "overdue", "compliance"]):
        context_parts.append("\n--- REVIEW STATUS ---")
        context_parts.append(f"Overdue: {len(briefing_data['reviews_overdue'])}")
        context_parts.append(f"Due in 30 days: {len(briefing_data['reviews_due_soon'])}")
        for c in briefing_data['reviews_overdue'][:5]:
            context_parts.append(f"  - {c.full_name}: was due {c.compliance.next_review_due}")
    
    if any(word in message_lower for word in ["concern", "worried", "anxiety", "anxious"]):
        context_parts.append("\n--- CLIENTS WITH ACTIVE CONCERNS ---")
        for c in briefing_data['active_concerns'][:8]:
            for concern in c.active_concerns:
                context_parts.append(f"  - {c.full_name}: {concern.topic} ({concern.severity.value})")
    
    # Check for specific client name mentions
    for client in client_service.get_all_clients():
        if client.last_name.lower() in message_lower or client.first_name.lower() in message_lower:
            summary = client_service.get_client_summary(client.id)
            context_parts.append(f"\n--- CLIENT DETAILS: {client.full_name} ---")
            context_parts.append(json.dumps(summary, indent=2, default=str))
            break
    
    return "\n".join(context_parts)


def render_dashboard(client_service: ClientService):
    """Render dashboard view"""
    st.header("📊 Advisor Dashboard")
    st.caption(f"As of {date.today().strftime('%A, %d %B %Y')}")
    
    briefing = client_service.get_daily_briefing_data()
    
    # Top metrics - Clickable cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("### 👥 Total Clients")
        if st.button(f"**{briefing['total_clients']}**", key="dash_total", use_container_width=True, help="View all clients"):
            st.session_state.client_filter = "all"
            st.session_state.current_view = "clients"
            st.rerun()
    with col2:
        st.markdown("### ⚠️ Reviews Overdue")
        if st.button(f"**{len(briefing['reviews_overdue'])}**", key="dash_overdue", use_container_width=True, help="View overdue reviews"):
            st.session_state.client_filter = "reviews_overdue"
            st.session_state.current_view = "clients"
            st.rerun()
    with col3:
        st.markdown("### 📅 Due in 30 Days")
        if st.button(f"**{len(briefing['reviews_due_soon'])}**", key="dash_due_soon", use_container_width=True, help="View reviews due soon"):
            st.session_state.client_filter = "reviews_due_soon"
            st.session_state.current_view = "clients"
            st.rerun()
    with col4:
        st.markdown("### 📞 Dormant (90+ days)")
        if st.button(f"**{len(briefing['dormant_90_days'])}**", key="dash_dormant", use_container_width=True, help="View dormant clients"):
            st.session_state.client_filter = "dormant"
            st.session_state.current_view = "clients"
            st.rerun()
    with col5:
        st.markdown("### 📋 Pending Follow-ups")
        if st.button(f"**{len(briefing['pending_follow_ups'])}**", key="dash_followups", use_container_width=True, help="View pending follow-ups"):
            st.session_state.client_filter = "pending_followups"
            st.session_state.current_view = "clients"
            st.rerun()
    
    st.divider()
    
    # Two-column layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Overdue Reviews
        st.subheader("⚠️ Overdue Annual Reviews")
        if briefing["reviews_overdue"]:
            for client in briefing["reviews_overdue"][:5]:
                with st.expander(f"{client.full_name} - Due: {client.compliance.next_review_due}"):
                    st.write(f"**Age:** {client.age}")
                    st.write(f"**Portfolio:** £{client.total_portfolio_value:,.0f}" if client.total_portfolio_value else "N/A")
                    st.write(f"**Last Contact:** {client.days_since_last_contact} days ago")
                    if st.button("📧 Draft Review Reminder", key=f"review_{client.id}"):
                        st.session_state.draft_for = client.id
                        st.session_state.draft_type = "review_reminder"
                        st.session_state.current_view = "emails"
                        st.rerun()
        else:
            st.success("No overdue reviews! 🎉")
        
        st.divider()
        
        # Dormant Clients
        st.subheader("📞 Clients Needing Contact")
        if briefing["dormant_90_days"]:
            for client in briefing["dormant_90_days"][:5]:
                with st.expander(f"{client.full_name} - {client.days_since_last_contact} days"):
                    concerns = [c.topic for c in client.active_concerns]
                    if concerns:
                        st.write(f"**Active Concerns:** {', '.join(concerns)}")
                    st.write(f"**Portfolio:** £{client.total_portfolio_value:,.0f}" if client.total_portfolio_value else "N/A")
                    if st.button("📧 Draft Check-in", key=f"checkin_{client.id}"):
                        st.session_state.draft_for = client.id
                        st.session_state.draft_type = "check_in"
                        st.session_state.current_view = "emails"
                        st.rerun()
        else:
            st.success("All clients contacted recently! 🎉")
    
    with col_right:
        # Upcoming Birthdays
        st.subheader("🎂 Upcoming Birthdays (14 days)")
        if briefing["upcoming_birthdays"]:
            for bday in briefing["upcoming_birthdays"][:5]:
                client = bday["client"]
                milestone = "🌟 MILESTONE" if bday["is_milestone"] else ""
                with st.expander(f"{client.full_name} - {bday['days_until']} days (turning {bday['turning_age']}) {milestone}"):
                    st.write(f"**Date:** {bday['date']}")
                    if bday["is_milestone"]:
                        st.info("Milestone birthday - pension access significance!")
                    if st.button("📧 Draft Birthday Email", key=f"bday_{client.id}"):
                        st.session_state.draft_for = client.id
                        st.session_state.draft_type = "birthday"
                        st.session_state.current_view = "emails"
                        st.rerun()
        else:
            st.info("No birthdays in the next 14 days")
        
        st.divider()
        
        # Overdue Follow-ups
        st.subheader("📋 Overdue Follow-ups")
        if briefing["overdue_follow_ups"]:
            for client in briefing["overdue_follow_ups"][:5]:
                for ofu_idx, followup in enumerate(client.overdue_follow_ups):
                    with st.expander(f"{client.full_name}: {followup.commitment}"):
                        st.write(f"**Was due:** {followup.deadline}")
                        st.write(f"**Created:** {followup.created_date}")
                        if st.button("📧 Draft Follow-up", key=f"followup_{client.id}_{ofu_idx}"):
                            st.session_state.draft_for = client.id
                            st.session_state.draft_type = "follow_up"
                            st.session_state.current_view = "emails"
                            st.rerun()
        else:
            st.success("No overdue follow-ups! 🎉")


def render_alerts(client_service: ClientService, llm_service: LLMService):
    """Render proactive alerts view - the heart of Jarvis"""
    st.header("🚨 Proactive Alerts")
    
    # Check if we have a specific filter from chat page
    filter_ids = st.session_state.get("alerts_filter_ids")
    filter_label = st.session_state.get("alerts_filter_label", "")
    
    if filter_ids:
        st.info(f"Showing filtered view: {filter_label}")
        if st.button("✖ Clear filter", key="clear_alerts_filter"):
            del st.session_state["alerts_filter_ids"]
            if "alerts_filter_label" in st.session_state:
                del st.session_state["alerts_filter_label"]
            st.rerun()
        st.divider()
    else:
        st.caption("Jarvis has scanned all your clients and found these items needing attention")
    
    # Generate all alerts
    clients = client_service.get_all_clients()
    all_alerts = alerts_service.generate_all_alerts(clients)
    
    # Filter out inactive clients' alerts
    inactive_clients = dismissal_service.get_inactive_clients()
    dismissed_alerts = dismissal_service.get_dismissed_alerts()
    
    active_alerts = [
        a for a in all_alerts 
        if a.client_id not in inactive_clients
    ]
    
    # Apply ID filter if coming from chat page
    if filter_ids:
        active_alerts = [a for a in active_alerts if a.id in filter_ids]
    
    summary = alerts_service.get_alert_summary(active_alerts)
    
    # Top summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Alerts", summary["total"])
    with col2:
        st.metric("🔴 Urgent", summary["urgent"])
    with col3:
        st.metric("🟠 High", summary["high"])
    with col4:
        st.metric("🟡 Medium", summary["medium"])
    with col5:
        st.metric("🟢 Low", summary["low"])
    
    st.divider()
    
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "Urgent", "High", "Medium", "Low"],
            key="alert_priority_filter"
        )
    with col_filter2:
        type_options = ["All"] + [t.value.replace("_", " ").title() for t in AlertType]
        type_filter = st.selectbox(
            "Filter by Type",
            type_options,
            key="alert_type_filter"
        )
    with col_filter3:
        st.write("")  # Spacer
        show_dismissed = st.checkbox("Show Dismissed", key="show_dismissed")
    
    # Apply filters
    filtered_alerts = active_alerts
    
    if priority_filter != "All":
        priority_map = {"Urgent": AlertPriority.URGENT, "High": AlertPriority.HIGH, 
                       "Medium": AlertPriority.MEDIUM, "Low": AlertPriority.LOW}
        filtered_alerts = [a for a in filtered_alerts if a.priority == priority_map.get(priority_filter)]
    
    if type_filter != "All":
        type_value = type_filter.lower().replace(" ", "_")
        filtered_alerts = [a for a in filtered_alerts if a.alert_type.value == type_value]
    
    if not show_dismissed:
        filtered_alerts = [a for a in filtered_alerts if a.id not in dismissed_alerts]
    
    st.caption(f"Showing {len(filtered_alerts)} of {len(active_alerts)} alerts")
    
    # Show inactive clients count if any
    if inactive_clients:
        st.caption(f"👻 {len(inactive_clients)} inactive clients hidden (see sidebar to manage)")
    
    # Daily briefing button
    if st.button("📋 Generate Daily Briefing", use_container_width=True):
        with st.spinner("Generating AI briefing..."):
            briefing_text = alerts_service.generate_daily_briefing(filtered_alerts)
            
            # Enhance with LLM if available
            try:
                ai_summary = llm_service.chat(
                    user_message="Based on these alerts, give me a brief, actionable summary of what I should focus on today. Be concise and prioritize urgent items.",
                    context=briefing_text,
                    conversation_history=[]
                )
                st.info(ai_summary)
            except Exception:
                st.markdown(briefing_text)
    
    st.divider()
    
    # Display alerts by priority group
    if not filtered_alerts:
        st.success("🎉 No alerts matching your filters!")
        return
    
    # Group by priority
    priority_groups = {
        AlertPriority.URGENT: ("🔴 Urgent", []),
        AlertPriority.HIGH: ("🟠 High Priority", []),
        AlertPriority.MEDIUM: ("🟡 Medium Priority", []),
        AlertPriority.LOW: ("🟢 Low Priority", [])
    }
    
    for alert in filtered_alerts:
        priority_groups[alert.priority][1].append(alert)
    
    # Render each group
    for priority, (label, alerts_in_group) in priority_groups.items():
        if not alerts_in_group:
            continue
        
        st.subheader(f"{label} ({len(alerts_in_group)})")
        
        for alert in alerts_in_group:
            # Check if dismissed
            is_dismissed = alert.id in dismissed_alerts
            title_prefix = "~~" if is_dismissed else ""
            title_suffix = "~~ (dismissed)" if is_dismissed else ""
            
            with st.expander(f"{title_prefix}{alert.title} | {alert.client_name}{title_suffix}", expanded=(priority == AlertPriority.URGENT and not is_dismissed)):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.write(alert.description)
                    
                    # Show due date info
                    if alert.due_date:
                        if alert.days_until_due and alert.days_until_due < 0:
                            st.error(f"⚠️ Overdue by {abs(alert.days_until_due)} days")
                        elif alert.days_until_due == 0:
                            st.warning("📅 Due Today!")
                        else:
                            st.info(f"📅 Due: {alert.due_date.strftime('%d %B %Y')} ({alert.days_until_due} days)")
                    
                    # Show related data
                    if alert.related_data:
                        with st.container():
                            st.caption("**Additional Details:**")
                            for key, value in alert.related_data.items():
                                if value and key not in ["email", "phone"]:
                                    nice_key = key.replace("_", " ").title()
                                    st.caption(f"• {nice_key}: {value}")
                
                with col_actions:
                    # Action buttons
                    if st.button("📧 Draft Email", key=f"alert_email_{alert.id}", use_container_width=True):
                        st.session_state.draft_for = alert.client_id
                        st.session_state.draft_type = _get_email_type_for_alert(alert.alert_type)
                        st.session_state.alert_context = alert.description
                        st.session_state.current_view = "emails"
                        st.rerun()
                    
                    if st.button("👤 View Client", key=f"alert_client_{alert.id}", use_container_width=True):
                        st.session_state.selected_client = alert.client_id
                        st.session_state.current_view = "clients"
                        st.rerun()
                    
                    # Dismiss button (toggles)
                    if is_dismissed:
                        if st.button("↩️ Restore", key=f"alert_restore_{alert.id}", use_container_width=True):
                            dismissal_service.undismiss_alert(alert.id)
                            st.rerun()
                    else:
                        if st.button("✓ Dismiss", key=f"alert_dismiss_{alert.id}", use_container_width=True):
                            dismissal_service.dismiss_alert(alert.id)
                            st.toast(f"✓ Dismissed: {alert.title}")
                            st.rerun()
                    
                    # Mark client as inactive (permanently stop all nudges for this client)
                    if st.button("👻 Not with us", key=f"alert_inactive_{alert.id}", use_container_width=True, help="Mark client as 'not with us anymore' - stops ALL alerts"):
                        dismissal_service.mark_client_inactive(alert.client_id, alert.client_name)
                        st.toast(f"👻 {alert.client_name} marked inactive. Restore from sidebar.")
                        st.rerun()
        
        st.divider()


def _get_email_type_for_alert(alert_type: AlertType) -> str:
    """Map alert type to email draft type"""
    mapping = {
        AlertType.BIRTHDAY: "birthday",
        AlertType.POLICY_RENEWAL: "policy_renewal",
        AlertType.FOLLOW_UP_DUE: "follow_up",
        AlertType.FOLLOW_UP_OVERDUE: "follow_up",
        AlertType.ANNUAL_REVIEW_DUE: "review_reminder",
        AlertType.ANNUAL_REVIEW_OVERDUE: "review_reminder",
        AlertType.NO_CONTACT: "check_in",
        AlertType.LIFE_EVENT: "check_in",
        AlertType.RETIREMENT_APPROACHING: "retirement_planning",
        AlertType.POLICY_MATURITY: "policy_maturity",
    }
    return mapping.get(alert_type, "check_in")


def render_clients(client_service: ClientService, vector_store: VectorStoreService):
    """Render clients list view with upload capability"""
    
    # Check if we have a filter from dashboard click
    active_filter = st.session_state.get("client_filter")
    filter_title = ""
    
    if active_filter == "reviews_overdue":
        filter_title = " - ⚠️ Reviews Overdue"
    elif active_filter == "reviews_due_soon":
        filter_title = " - 📅 Reviews Due in 30 Days"
    elif active_filter == "dormant":
        filter_title = " - 📞 Dormant Clients (90+ days)"
    elif active_filter == "pending_followups":
        filter_title = " - 📋 Clients with Pending Follow-ups"
    
    st.header(f"👥 Client Directory{filter_title}")
    
    # Clear filter button if active
    if active_filter and active_filter != "all":
        if st.button("❌ Clear Filter", key="clear_filter"):
            st.session_state.client_filter = None
            st.rerun()
    
    # ============== ADD NEW CLIENT SECTION ==============
    with st.expander("➕ Add New Client", expanded=False):
        st.write("Upload a Word (.docx) or Excel (.xlsx) file with client details. Jarvis will extract the data and show you what's missing.")
        
        tab1, tab2, tab3 = st.tabs(["📄 Upload Document", "📝 Manual Entry", "📋 JSON Upload"])
        
        with tab1:
            st.info("💡 **Supported formats:** Word (.docx), Excel (.xlsx), Text (.txt). Documents with couples/partners are supported!")
            
            uploaded_doc = st.file_uploader(
                "Upload Client Document", 
                type=["docx", "xlsx", "xls", "txt"],
                key="doc_upload",
                help="Upload a document containing client information"
            )
            
            if uploaded_doc:
                from services.document_parser import document_parser
                
                # Parse the document for multiple people
                file_bytes = uploaded_doc.read()
                people, shared_data = document_parser.parse_document_multi(file_bytes, uploaded_doc.name)
                
                if len(people) == 0 or (len(people) == 1 and "_error" in people[0]):
                    error_msg = people[0].get("_error", "Could not extract data from document") if people else "Could not extract data from document"
                    st.error(f"❌ {error_msg}")
                else:
                    # Multiple people detected
                    if len(people) > 1:
                        st.success(f"👥 **Found {len(people)} people in document!**")
                        
                        # Show all people found
                        st.write("**People detected:**")
                        for i, person in enumerate(people):
                            name = f"{person.get('first_name', 'Unknown')} {person.get('last_name', '')}"
                            occ = person.get('occupation', 'Not specified')
                            st.write(f"  {i+1}. **{name}** - {occ}")
                        
                        if shared_data:
                            st.write("**Shared household data:**")
                            for key, value in shared_data.items():
                                nice_key = key.replace('_', ' ').title()
                                if key == "portfolio":
                                    st.write(f"  • {nice_key}: £{value:,.0f}")
                                else:
                                    st.write(f"  • {nice_key}: {value}")
                        
                        # Let user select which person to add
                        person_options = [f"{p.get('first_name', 'Unknown')} {p.get('last_name', '')}" for p in people]
                        selected_person_idx = st.selectbox(
                            "**Select person to add as primary client:**", 
                            range(len(people)),
                            format_func=lambda x: person_options[x],
                            key="select_person"
                        )
                        
                        # Use selected person's data merged with shared data
                        extracted_data = {**shared_data, **people[selected_person_idx]}
                        
                        # Offer to add the other person as family member
                        other_idx = 1 - selected_person_idx if len(people) == 2 else None
                        if other_idx is not None:
                            add_as_family = st.checkbox(
                                f"Add {person_options[other_idx]} as family member (spouse/partner)", 
                                value=True,
                                key="add_as_family"
                            )
                            if add_as_family:
                                st.session_state["family_member_data"] = people[other_idx]
                        
                        st.divider()
                    else:
                        # Single person
                        extracted_data = {**shared_data, **people[0]} if shared_data else people[0]
                        st.success(f"✅ Extracted {len(extracted_data)} fields from document")
                    
                    # Get missing fields
                    missing_fields = document_parser._get_missing_fields(extracted_data)
                    
                    if extracted_data:
                        st.write("**📋 Extracted Data:**")
                        for key, value in extracted_data.items():
                            if key not in ["_error"]:
                                nice_key = key.replace('_', ' ').title()
                                if key in ["income", "portfolio"] and value:
                                    st.write(f"- **{nice_key}:** £{value:,.0f}")
                                else:
                                    st.write(f"- **{nice_key}:** {value}")
                    
                    # Show missing fields warning
                    if missing_fields:
                        st.warning(f"⚠️ **Missing required fields:** {', '.join([f.replace('_', ' ').title() for f in missing_fields])}")
                        st.write("Please fill in the missing information below:")
                    
                    st.divider()
                    st.write("**Complete Client Details:**")
                    
                    # Generate ID
                    existing_ids = [c.id for c in client_service.get_all_clients()]
                    auto_id = document_parser.generate_client_id(existing_ids)
                    
                    # Form with pre-filled values from extraction
                    col1, col2 = st.columns(2)
                    with col1:
                        doc_id = st.text_input("Client ID *", value=auto_id, key="doc_id")
                        doc_title = st.selectbox("Title *", ["Mr", "Mrs", "Ms", "Dr", "Miss"], 
                            index=["Mr", "Mrs", "Ms", "Dr", "Miss"].index(extracted_data.get("title", "Mr")) if extracted_data.get("title") in ["Mr", "Mrs", "Ms", "Dr", "Miss"] else 0,
                            key="doc_title")
                        doc_first = st.text_input("First Name *", value=extracted_data.get("first_name", ""), key="doc_first",
                            help="⚠️ Required" if "first_name" in missing_fields else None)
                        doc_last = st.text_input("Last Name *", value=extracted_data.get("last_name", ""), key="doc_last",
                            help="⚠️ Required" if "last_name" in missing_fields else None)
                        
                        # Handle date of birth
                        dob_value = None
                        if extracted_data.get("date_of_birth"):
                            try:
                                from datetime import datetime as dt
                                dob_value = dt.strptime(extracted_data["date_of_birth"], "%Y-%m-%d").date()
                            except:
                                pass
                        doc_dob = st.date_input("Date of Birth *", value=dob_value, key="doc_dob",
                            help="⚠️ Required" if "date_of_birth" in missing_fields else None)
                        doc_occupation = st.text_input("Occupation", value=extracted_data.get("occupation", ""), key="doc_occupation")
                        doc_employer = st.text_input("Employer", value=extracted_data.get("employer", ""), key="doc_employer")
                    
                    with col2:
                        doc_email = st.text_input("Email *", value=extracted_data.get("email", ""), key="doc_email",
                            help="⚠️ Required" if "email" in missing_fields else None)
                        doc_phone = st.text_input("Phone *", value=extracted_data.get("phone", ""), key="doc_phone",
                            help="⚠️ Required" if "phone" in missing_fields else None)
                        doc_address = st.text_input("Address Line 1 *", value=extracted_data.get("address_line1", ""), key="doc_address",
                            help="⚠️ Required" if "address_line1" in missing_fields else None)
                        doc_city = st.text_input("City *", value=extracted_data.get("city", ""), key="doc_city",
                            help="⚠️ Required" if "city" in missing_fields else None)
                        doc_postcode = st.text_input("Postcode *", value=extracted_data.get("postcode", ""), key="doc_postcode",
                            help="⚠️ Required" if "postcode" in missing_fields else None)
                        
                        marital_options = ["single", "married", "divorced", "widowed", "civil_partnership"]
                        marital_index = 0
                        # If couple detected, default to married
                        if len(people) > 1:
                            marital_index = marital_options.index("married")
                        elif extracted_data.get("marital_status") in marital_options:
                            marital_index = marital_options.index(extracted_data["marital_status"])
                        doc_marital = st.selectbox("Marital Status", marital_options, index=marital_index, key="doc_marital")
                    
                    # Financial info
                    income_val = int(extracted_data.get("income", 0) or 0)
                    portfolio_val = int(extracted_data.get("portfolio", 0) or 0)
                    doc_income = st.number_input("Annual Income (£)", min_value=0, value=income_val, step=1000, key="doc_income")
                    doc_portfolio = st.number_input("Portfolio Value (£)", min_value=0, value=portfolio_val, step=1000, key="doc_portfolio")
                    
                    # Add button
                    if st.button("✅ Add Client & Index", key="add_from_doc"):
                        # Validate required fields
                        if all([doc_id, doc_first, doc_last, doc_dob, doc_email, doc_phone, doc_address, doc_city, doc_postcode]):
                            from datetime import date as date_type
                            
                            # Build family members list
                            family_members = []
                            family_data = st.session_state.get("family_member_data")
                            if family_data and st.session_state.get("add_as_family", False):
                                family_member = {
                                    "name": f"{family_data.get('first_name', '')} {family_data.get('last_name', '')}".strip(),
                                    "relationship": "spouse",
                                    "age": None,
                                    "occupation": family_data.get("occupation"),
                                    "dependent": False
                                }
                                # Calculate age from DOB if available
                                if family_data.get("date_of_birth"):
                                    try:
                                        from datetime import datetime as dt
                                        fam_dob = dt.strptime(family_data["date_of_birth"], "%Y-%m-%d").date()
                                        family_member["age"] = (date_type.today() - fam_dob).days // 365
                                    except:
                                        pass
                                family_members.append(family_member)
                            
                            client_data = {
                                "id": doc_id,
                                "title": doc_title,
                                "first_name": doc_first,
                                "last_name": doc_last,
                                "date_of_birth": doc_dob.isoformat() if doc_dob else None,
                                "occupation": doc_occupation or None,
                                "employer": doc_employer or None,
                                "annual_income": doc_income if doc_income > 0 else None,
                                "total_portfolio_value": doc_portfolio if doc_portfolio > 0 else None,
                                "marital_status": doc_marital,
                                "contact_info": {
                                    "email": doc_email,
                                    "phone": doc_phone,
                                    "address": {
                                        "line1": doc_address,
                                        "city": doc_city,
                                        "postcode": doc_postcode,
                                        "country": "United Kingdom"
                                    }
                                },
                                "client_since": date_type.today().isoformat(),
                                "policies": [],
                                "concerns": [],
                                "family_members": family_members,
                                "life_events": [],
                                "meeting_notes": [],
                                "follow_ups": [],
                                "interactions": []
                            }
                            
                            success, message, new_client = client_service.add_client_from_dict(client_data)
                            if success and new_client:
                                family_note = ""
                                if family_members:
                                    family_note = f" (with spouse: {family_members[0]['name']})"
                                if vector_store.is_available():
                                    vector_store.index_client(new_client)
                                    st.success(f"✅ {message}{family_note} and indexed for semantic search!")
                                else:
                                    st.success(f"✅ {message}{family_note}")
                                # Clear family member data
                                if "family_member_data" in st.session_state:
                                    del st.session_state["family_member_data"]
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Please fill in all required fields marked with *")
        
        with tab2:
            st.write("Enter client details manually:")
            
            # Generate auto ID
            existing_ids = [c.id for c in client_service.get_all_clients()]
            from services.document_parser import document_parser
            auto_id = document_parser.generate_client_id(existing_ids)
            
            # Check if form should be cleared
            clear_form = st.session_state.pop("clear_manual_form", False)
            
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Client ID *", value=auto_id if clear_form else st.session_state.get("manual_id", auto_id), key="manual_id")
                new_title = st.selectbox("Title *", ["Mr", "Mrs", "Ms", "Dr", "Miss"], index=0 if clear_form else None, key="manual_title")
                new_first = st.text_input("First Name *", placeholder="John", value="" if clear_form else st.session_state.get("manual_first", ""), key="manual_first")
                new_last = st.text_input("Last Name *", placeholder="Smith", value="" if clear_form else st.session_state.get("manual_last", ""), key="manual_last")
                new_dob = st.date_input("Date of Birth *", value=None, key="manual_dob")
                new_occupation = st.text_input("Occupation", placeholder="Accountant", value="" if clear_form else st.session_state.get("manual_occupation", ""), key="manual_occupation")
            
            with col2:
                new_email = st.text_input("Email *", placeholder="john.smith@email.com", value="" if clear_form else st.session_state.get("manual_email", ""), key="manual_email")
                new_phone = st.text_input("Phone *", placeholder="07700 900123", value="" if clear_form else st.session_state.get("manual_phone", ""), key="manual_phone")
                new_address_line1 = st.text_input("Address Line 1 *", placeholder="123 High Street", value="" if clear_form else st.session_state.get("manual_address", ""), key="manual_address")
                new_city = st.text_input("City *", placeholder="London", value="" if clear_form else st.session_state.get("manual_city", ""), key="manual_city")
                new_postcode = st.text_input("Postcode *", placeholder="SW1A 1AA", value="" if clear_form else st.session_state.get("manual_postcode", ""), key="manual_postcode")
                new_marital = st.selectbox("Marital Status", ["single", "married", "divorced", "widowed", "civil_partnership"], index=0 if clear_form else None, key="manual_marital")
            
            new_income = st.number_input("Annual Income (£)", min_value=0, value=0, step=1000, key="manual_income")
            new_portfolio = st.number_input("Total Portfolio Value (£)", min_value=0, value=0, step=1000, key="manual_portfolio")
            
            if st.button("✅ Add Client", key="add_manual"):
                if all([new_id, new_first, new_last, new_dob, new_email, new_phone, new_address_line1, new_city, new_postcode]):
                    from datetime import date as date_type
                    client_data = {
                        "id": new_id,
                        "title": new_title,
                        "first_name": new_first,
                        "last_name": new_last,
                        "date_of_birth": new_dob.isoformat() if new_dob else None,
                        "occupation": new_occupation or None,
                        "annual_income": new_income if new_income > 0 else None,
                        "total_portfolio_value": new_portfolio if new_portfolio > 0 else None,
                        "marital_status": new_marital,
                        "contact_info": {
                            "email": new_email,
                            "phone": new_phone,
                            "address": {
                                "line1": new_address_line1,
                                "city": new_city,
                                "postcode": new_postcode,
                                "country": "United Kingdom"
                            }
                        },
                        "client_since": date_type.today().isoformat(),
                        "policies": [],
                        "concerns": [],
                        "family_members": [],
                        "life_events": [],
                        "meeting_notes": [],
                        "follow_ups": [],
                        "interactions": []
                    }
                    
                    success, message, new_client = client_service.add_client_from_dict(client_data)
                    if success and new_client:
                        if vector_store.is_available():
                            vector_store.index_client(new_client)
                            st.success(f"✅ {message} and indexed for semantic search!")
                        else:
                            st.success(f"✅ {message}")
                        st.balloons()
                        # Set flag to clear form on next render
                        st.session_state.clear_manual_form = True
                        # Clear all form keys from session state
                        for key in list(st.session_state.keys()):
                            if key.startswith("manual_"):
                                del st.session_state[key]
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("Please fill in all required fields (*)")
        
        with tab3:
            st.write("Upload a JSON file with complete client data:")
            uploaded_json = st.file_uploader(
                "Upload Client JSON", 
                type=["json"],
                key="json_upload",
                help="Upload a JSON file with client data following the schema"
            )
            
            if uploaded_json:
                try:
                    client_data = json.load(uploaded_json)
                    st.json(client_data)
                    
                    if st.button("✅ Add Client & Index", key="add_from_json"):
                        success, message, new_client = client_service.add_client_from_dict(client_data)
                        if success and new_client:
                            if vector_store.is_available():
                                vector_store.index_client(new_client)
                                st.success(f"✅ {message} and indexed for semantic search!")
                            else:
                                st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON file: {e}")
            
            # Download template button
            st.divider()
            sample_template = {
                "id": "client_014",
                "title": "Mr",
                "first_name": "John",
                "last_name": "Smith",
                "date_of_birth": "1975-06-15",
                "occupation": "Software Engineer",
                "annual_income": 85000,
                "total_portfolio_value": 450000,
                "marital_status": "married",
                "contact_info": {
                    "email": "john.smith@email.com",
                    "phone": "07700 900123",
                    "address": {
                        "line1": "123 High Street",
                        "city": "Manchester",
                        "postcode": "M1 1AA",
                        "country": "United Kingdom"
                    }
                },
                "client_since": "2020-03-15"
            }
            st.download_button(
                "📥 Download JSON Template",
                json.dumps(sample_template, indent=2),
                "client_template.json",
                "application/json"
            )
    
    st.divider()
    
    # ============== SELECTED CLIENT DETAIL VIEW ==============
    selected_client_id = st.session_state.get("selected_client")
    if selected_client_id:
        client = client_service.get_client_by_id(selected_client_id)
        if client:
            # Show detailed client view
            st.subheader(f"📋 Client Details: {client.full_name}")
            
            # Back button
            if st.button("← Back to Client List", key="back_to_list"):
                st.session_state.selected_client = None
                st.rerun()
            
            st.divider()
            
            # Client overview in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 👤 Personal Information")
                st.write(f"**Name:** {client.title} {client.first_name} {client.last_name}")
                st.write(f"**Date of Birth:** {client.date_of_birth} (Age: {client.age})")
                st.write(f"**Marital Status:** {client.marital_status.title()}")
                st.write(f"**Occupation:** {client.occupation or 'Not specified'}")
                st.write(f"**Employer:** {client.employer or 'Not specified'}")
                st.write(f"**Annual Income:** £{client.annual_income:,.0f}" if client.annual_income else "**Annual Income:** Not specified")
                st.write(f"**Client Since:** {client.client_since}")
            
            with col2:
                st.markdown("### 📞 Contact Information")
                st.write(f"**Email:** {client.contact_info.email}")
                st.write(f"**Phone:** {client.contact_info.phone}")
                if client.contact_info.mobile:
                    st.write(f"**Mobile:** {client.contact_info.mobile}")
                st.write(f"**Address:**")
                st.write(f"  {client.contact_info.address.line1}")
                if client.contact_info.address.line2:
                    st.write(f"  {client.contact_info.address.line2}")
                st.write(f"  {client.contact_info.address.city}, {client.contact_info.address.postcode}")
                st.write(f"**Preferred Contact:** {client.contact_info.preferred_contact_method.value}")
                if client.contact_info.best_time_to_call:
                    st.write(f"**Best Time to Call:** {client.contact_info.best_time_to_call}")
            
            with col3:
                st.markdown("### 💰 Portfolio Summary")
                st.write(f"**Total Value:** £{client.total_portfolio_value:,.0f}" if client.total_portfolio_value else "**Total Value:** Not calculated")
                if client.risk_profile:
                    st.write(f"**Risk Attitude:** {client.risk_profile.attitude_to_risk.value.replace('_', ' ').title()}")
                    st.write(f"**Capacity for Loss:** {client.risk_profile.capacity_for_loss.value.replace('_', ' ').title()}")
                    st.write(f"**Time Horizon:** {client.risk_profile.time_horizon_years} years")
                    st.write(f"**Last Assessed:** {client.risk_profile.last_assessed}")
                st.write(f"**Last Contact:** {client.days_since_last_contact} days ago" if client.days_since_last_contact else "**Last Contact:** Never")
            
            st.divider()
            
            # Family Members
            if client.family_members:
                st.markdown("### 👨‍👩‍👧‍👦 Family Members")
                fam_cols = st.columns(min(len(client.family_members), 4))
                for idx, member in enumerate(client.family_members):
                    with fam_cols[idx % 4]:
                        st.write(f"**{member.name}** ({member.relationship})")
                        if member.date_of_birth:
                            st.caption(f"DOB: {member.date_of_birth}")
                        if member.notes:
                            st.caption(member.notes)
                st.divider()
            
            # Two column layout for policies and concerns
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("### 📜 Policies")
                if client.policies:
                    for policy in client.policies:
                        with st.container():
                            policy_value = f"£{policy.current_value:,.0f}" if policy.current_value else "N/A"
                            st.write(f"**{policy.policy_type.value.upper()}** - {policy.provider}")
                            st.caption(f"Value: {policy_value} | Policy #: {policy.policy_number or 'N/A'}")
                            if policy.renewal_date:
                                st.caption(f"Renewal: {policy.renewal_date}")
                            if policy.notes:
                                st.caption(f"📝 {policy.notes}")
                            st.write("---")
                else:
                    st.info("No policies on record")
            
            with detail_col2:
                st.markdown("### ⚠️ Concerns")
                if client.concerns:
                    for concern in client.concerns:
                        status_emoji = "🔴" if concern.status.value == "active" else "🟡" if concern.status.value == "monitoring" else "🟢"
                        severity_color = "🔥" if concern.severity.value == "high" else "⚡" if concern.severity.value == "medium" else ""
                        st.write(f"{status_emoji} **{concern.topic.title()}** {severity_color}")
                        st.caption(concern.details)
                        st.caption(f"Status: {concern.status.value} | Raised: {concern.date_raised}")
                        st.write("---")
                else:
                    st.success("No concerns on record")
            
            st.divider()
            
            # Compliance and Follow-ups
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.markdown("### ✅ Compliance")
                review_status_emoji = "🔴" if client.compliance.review_status == "overdue" else "🟡" if client.compliance.review_status == "pending" else "🟢"
                st.write(f"**Review Status:** {review_status_emoji} {client.compliance.review_status.title()}")
                st.write(f"**Last Review:** {client.compliance.last_annual_review}")
                st.write(f"**Next Review Due:** {client.compliance.next_review_due}")
                if client.compliance.value_delivered:
                    st.write("**Value Delivered:**")
                    for value in client.compliance.value_delivered:
                        st.caption(f"✓ {value}")
            
            with comp_col2:
                st.markdown("### 📋 Follow-ups")
                if client.follow_ups:
                    for fu in client.follow_ups:
                        status_emoji = "✅" if fu.status.value == "completed" else "🔴" if fu.deadline < date.today() else "🟡"
                        st.write(f"{status_emoji} {fu.commitment}")
                        st.caption(f"Due: {fu.deadline} | Status: {fu.status.value}")
                else:
                    st.info("No follow-ups on record")
            
            st.divider()
            
            # Recent Interactions
            st.markdown("### 📞 Recent Interactions")
            if client.interactions:
                for interaction in client.interactions[:5]:
                    int_date = interaction.interaction_date.strftime("%Y-%m-%d") if hasattr(interaction.interaction_date, 'strftime') else str(interaction.interaction_date)[:10]
                    direction_emoji = "📤" if interaction.direction == "outbound" else "📥"
                    st.write(f"{direction_emoji} **{int_date}** via {interaction.method.value} - {interaction.summary}")
            else:
                st.info("No interactions recorded")
            
            st.divider()
            
            # Action buttons
            st.markdown("### 🎯 Quick Actions")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button("📧 Draft Email", key="detail_draft_email", use_container_width=True):
                    st.session_state.draft_for = client.id
                    st.session_state.draft_type = "check_in"
                    st.session_state.current_view = "emails"
                    st.rerun()
            
            with action_col2:
                if st.button("✅ Mark Review Done", key="detail_mark_review", use_container_width=True):
                    success, msg = client_service.update_review_status(client.id, "completed")
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with action_col3:
                if st.button("📞 Log Contact", key="detail_log_contact", use_container_width=True):
                    st.session_state["show_detail_log_form"] = True
            
            with action_col4:
                if st.button("← Back to List", key="detail_back", use_container_width=True):
                    st.session_state.selected_client = None
                    st.rerun()
            
            # Log contact form
            if st.session_state.get("show_detail_log_form", False):
                st.write("**Log New Contact:**")
                log_col1, log_col2 = st.columns(2)
                with log_col1:
                    contact_method = st.selectbox("Method", ["Phone", "Email", "In_Person", "Video"], key="detail_method")
                    direction = st.selectbox("Direction", ["Outbound", "Inbound"], key="detail_dir")
                with log_col2:
                    duration = st.number_input("Duration (mins)", min_value=0, value=15, key="detail_dur")
                summary = st.text_input("Summary", placeholder="Brief note about the contact", key="detail_sum")
                
                log_btn_col1, log_btn_col2 = st.columns(2)
                with log_btn_col1:
                    if st.button("✅ Save Contact", key="detail_save_contact", use_container_width=True):
                        if summary:
                            from data.schema import ContactMethod as CM
                            method_map = {"Phone": CM.PHONE, "Email": CM.EMAIL, "In_Person": CM.IN_PERSON, "Video": CM.VIDEO_CALL}
                            success, msg = client_service.log_interaction(
                                client.id, 
                                method_map[contact_method],
                                direction.lower(),
                                summary,
                                duration if duration > 0 else None
                            )
                            if success:
                                st.success(msg)
                                st.session_state["show_detail_log_form"] = False
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.warning("Please enter a summary")
                with log_btn_col2:
                    if st.button("❌ Cancel", key="detail_cancel_log", use_container_width=True):
                        st.session_state["show_detail_log_form"] = False
                        st.rerun()
            
            # Don't show the client list when viewing details
            return
        else:
            # Client not found, clear selection
            st.session_state.selected_client = None
    
    # ============== CLIENT LIST SECTION ==============
    col1, col2, col3 = st.columns(3)
    
    # Map session filter to dropdown index
    status_options = ["All", "Review Overdue", "Due in 30 Days", "Dormant (90+ days)", "Has Active Concerns", "Pending Follow-ups"]
    filter_to_index = {
        "all": 0,
        "reviews_overdue": 1,
        "reviews_due_soon": 2,
        "dormant": 3,
        "active_concerns": 4,
        "pending_followups": 5,
    }
    default_status_idx = filter_to_index.get(active_filter, 0)
    
    with col1:
        search = st.text_input("🔍 Search by name", "")
    with col2:
        filter_concern = st.selectbox("Filter by concern", 
            ["All", "retirement", "inheritance tax", "protection", "care home costs", "pension"])
    with col3:
        filter_status = st.selectbox("Filter by status", status_options, index=default_status_idx)
    
    # Get clients based on filter
    if search:
        clients = client_service.search_by_name(search)
        st.session_state.client_filter = None  # Clear dashboard filter when searching
    elif filter_concern != "All":
        clients = client_service.search_by_concern(filter_concern)
        st.session_state.client_filter = None
    elif filter_status == "Review Overdue":
        clients = client_service.get_clients_review_overdue()
    elif filter_status == "Due in 30 Days":
        briefing = client_service.get_daily_briefing_data()
        clients = briefing["reviews_due_soon"]
    elif filter_status == "Dormant (90+ days)":
        clients = client_service.get_dormant_clients(90)
    elif filter_status == "Has Active Concerns":
        clients = client_service.get_clients_with_active_concerns()
    elif filter_status == "Pending Follow-ups":
        clients = [c for c in client_service.get_all_clients() if c.pending_follow_ups]
    else:
        clients = client_service.get_all_clients()
    
    st.caption(f"Showing {len(clients)} clients")
    st.divider()
    
    # Client cards
    for client in clients:
        with st.expander(f"**{client.full_name}** | Age: {client.age} | Portfolio: £{client.total_portfolio_value:,.0f}" if client.total_portfolio_value else f"**{client.full_name}** | Age: {client.age}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Contact:**")
                st.write(f"📧 {client.contact_info.email}")
                st.write(f"📞 {client.contact_info.phone}")
                st.write(f"Last contact: {client.days_since_last_contact} days ago" if client.days_since_last_contact else "No contact recorded")
                
                st.write("**Personal:**")
                st.write(f"Occupation: {client.occupation}")
                st.write(f"Marital Status: {client.marital_status}")
                if client.family_members:
                    family = ", ".join([f"{m.name} ({m.relationship})" for m in client.family_members[:3]])
                    st.write(f"Family: {family}")
            
            with col2:
                st.write("**Policies:**")
                for policy in client.policies[:4]:
                    st.write(f"- {policy.policy_type.value}: {policy.provider} (£{policy.current_value:,.0f})" if policy.current_value else f"- {policy.policy_type.value}: {policy.provider}")
                
                if client.active_concerns:
                    st.write("**Active Concerns:**")
                    for concern in client.active_concerns:
                        st.write(f"- {concern.topic} ({concern.severity.value})")
                
                st.write("**Compliance:**")
                st.write(f"Review Status: {client.compliance.review_status}")
                st.write(f"Next Review Due: {client.compliance.next_review_due}")
            
            # Pending Follow-ups section
            if client.pending_follow_ups:
                st.write("**📋 Pending Follow-ups:**")
                for fu_idx, followup in enumerate(client.pending_follow_ups):
                    fu_col1, fu_col2 = st.columns([3, 1])
                    with fu_col1:
                        overdue = "🔴 OVERDUE" if followup.deadline < date.today() else ""
                        st.write(f"• {followup.commitment} (Due: {followup.deadline}) {overdue}")
                    with fu_col2:
                        if st.button("✅ Done", key=f"complete_fu_{client.id}_{fu_idx}", use_container_width=True):
                            success, msg = client_service.complete_follow_up(client.id, followup.commitment)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            
            # Recent meetings
            if client.meeting_notes:
                st.write("**Recent Meeting Notes:**")
                for note in client.meeting_notes[:2]:
                    st.caption(f"{note.meeting_date}: {note.summary}")
            
            # Action buttons
            st.divider()
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("📞 Log Contact", key=f"log_contact_{client.id}", use_container_width=True):
                    st.session_state[f"show_log_form_{client.id}"] = True
            
            with action_col2:
                if st.button("✅ Mark Review Done", key=f"mark_review_{client.id}", use_container_width=True):
                    success, msg = client_service.update_review_status(client.id, "completed")
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with action_col3:
                if st.button("📧 Draft Email", key=f"draft_email_{client.id}", use_container_width=True):
                    st.session_state.draft_for = client.id
                    st.session_state.draft_type = "check_in"
                    st.session_state.current_view = "emails"
                    st.rerun()
            
            # Log contact form (shown when button clicked)
            if st.session_state.get(f"show_log_form_{client.id}", False):
                st.write("**Log New Contact:**")
                log_col1, log_col2 = st.columns(2)
                with log_col1:
                    contact_method = st.selectbox("Method", ["Phone", "Email", "In_Person", "Video"], key=f"method_{client.id}")
                    direction = st.selectbox("Direction", ["Outbound", "Inbound"], key=f"dir_{client.id}")
                with log_col2:
                    duration = st.number_input("Duration (mins)", min_value=0, value=15, key=f"dur_{client.id}")
                summary = st.text_input("Summary", placeholder="Brief note about the contact", key=f"sum_{client.id}")
                
                log_btn_col1, log_btn_col2 = st.columns(2)
                with log_btn_col1:
                    if st.button("✅ Save Contact", key=f"save_log_{client.id}", use_container_width=True):
                        if summary:
                            success, msg = client_service.log_interaction(
                                client.id, contact_method.lower(), direction.lower(), summary, duration
                            )
                            if success:
                                st.success(msg)
                                st.session_state[f"show_log_form_{client.id}"] = False
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.warning("Please enter a summary")
                with log_btn_col2:
                    if st.button("❌ Cancel", key=f"cancel_log_{client.id}", use_container_width=True):
                        st.session_state[f"show_log_form_{client.id}"] = False
                        st.rerun()


def render_emails(client_service: ClientService, llm_service: LLMService):
    """Render email drafting view with send capability"""
    st.header("📧 Email Drafts")
    
    # Check Google connection status
    google_connected = google_service.is_authenticated()
    
    if google_connected:
        st.success("✅ Google connected - you can send emails directly!")
    else:
        st.info("💡 Connect Google in Settings to send emails directly from Jarvis")
    
    # Check if we came from a button click (dashboard, alerts, etc.)
    draft_for = st.session_state.get("draft_for")
    draft_type = st.session_state.get("draft_type")
    auto_generate = draft_for is not None and draft_type is not None
    
    # Clear previous draft when coming from a button click
    if auto_generate and "current_draft" in st.session_state:
        del st.session_state.current_draft
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Create New Draft")
        
        # Client selection
        clients = client_service.get_all_clients()
        client_names = {f"{c.full_name} ({c.id})": c.id for c in clients}
        client_name_list = list(client_names.keys())
        
        # Pre-select client if coming from button - set widget state directly
        if draft_for:
            for name, cid in client_names.items():
                if cid == draft_for:
                    st.session_state["email_client_select"] = name
                    break
            del st.session_state["draft_for"]
        
        selected = st.selectbox("Select Client", client_name_list, key="email_client_select")
        selected_client_id = client_names[selected]
        selected_client = client_service.get_client_by_id(selected_client_id)
        
        # Email type - expanded for alert types
        email_types = {
            "Birthday Wishes": "birthday",
            "Review Reminder": "review_reminder", 
            "Check-in": "check_in",
            "Follow-up": "follow_up",
            "Policy Renewal": "policy_renewal",
            "Policy Maturity": "policy_maturity",
            "Retirement Planning": "retirement_planning",
            "General Update": "general_update"
        }
        email_type_list = list(email_types.keys())
        
        # Pre-select email type if coming from button - set widget state directly
        if draft_type:
            for name, etype in email_types.items():
                if etype == draft_type:
                    st.session_state["email_type_select"] = name
                    break
            del st.session_state["draft_type"]
        
        selected_type = st.selectbox("Email Type", email_type_list, key="email_type_select")
        email_type = email_types[selected_type]
        
        # Include alert context if coming from alerts page
        alert_context = st.session_state.pop("alert_context", "")
        additional_context = st.text_area("Additional context (optional)", 
            value=alert_context,
            placeholder="Any specific points to include...")
        
        generate_btn = st.button("✨ Generate Draft", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Email Preview")
        
        # Check if we should generate:
        # 1. User clicked generate button
        # 2. User clicked regenerate
        # 3. Auto-generate from dashboard/alerts redirect
        should_generate = generate_btn or st.session_state.get("regenerate_email", False) or auto_generate
        
        # Clear regenerate flag if it was set
        if st.session_state.get("regenerate_email"):
            st.session_state.regenerate_email = False
        
        if should_generate:
            with st.spinner("Drafting email..."):
                client_summary = client_service.get_client_summary(selected_client_id)
                
                email_draft = llm_service.draft_email(
                    client_summary=client_summary,
                    email_type=email_type,
                    additional_context=additional_context if additional_context else None
                )
                
                st.session_state.current_draft = email_draft
                st.session_state.current_draft_client_id = selected_client_id
                st.session_state.current_draft_type = email_type
                # Store the parameters used for this draft
                st.session_state.last_draft_params = {
                    "client_id": selected_client_id,
                    "email_type": email_type,
                    "context": additional_context
                }
        
        if "current_draft" in st.session_state and selected_client:
            # Extract subject and body from draft
            draft_text = st.session_state.current_draft
            
            # Try to parse subject line
            lines = draft_text.strip().split('\n')
            subject = ""
            body_start = 0
            for i, line in enumerate(lines):
                if line.lower().startswith("subject:"):
                    subject = line[8:].strip()
                    body_start = i + 1
                    break
                elif line.lower().startswith("**subject:**"):
                    subject = line[12:].strip()
                    body_start = i + 1
                    break
            
            if not subject:
                # Generate default subject
                type_subjects = {
                    "birthday": f"Happy Birthday, {selected_client.first_name}!",
                    "review_reminder": f"Annual Review - {selected_client.full_name}",
                    "check_in": f"Checking In - {selected_client.first_name}",
                    "follow_up": f"Following Up - {selected_client.first_name}",
                    "policy_renewal": f"Policy Renewal Reminder",
                    "policy_maturity": f"Policy Maturity Notice",
                    "retirement_planning": f"Retirement Planning Discussion",
                    "general_update": f"Update from Your Advisor"
                }
                subject = type_subjects.get(email_type, "Message from Your Financial Advisor")
            
            body = '\n'.join(lines[body_start:]).strip() if body_start > 0 else draft_text
            
            # Editable fields
            edited_subject = st.text_input("Subject", value=subject, key="email_subject")
            edited_body = st.text_area("Email Body", value=body, height=300, key="email_body")
            
            # Show recipient info
            st.caption(f"**To:** {selected_client.contact_info.email}")
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.regenerate_email = True
                    if "current_draft" in st.session_state:
                        del st.session_state.current_draft
                    st.rerun()
            
            with col_b:
                if google_connected:
                    if st.button("📝 Save to Gmail Drafts", use_container_width=True):
                        client_email = selected_client.contact_info.email
                        success, result = google_service.create_draft(
                            to=client_email,
                            subject=edited_subject,
                            body=edited_body
                        )
                        if success:
                            st.success(f"✅ Draft saved to Gmail!")
                        else:
                            st.error(f"❌ Failed: {result}")
                else:
                    st.button("📝 Save to Gmail", use_container_width=True, disabled=True, 
                             help="Connect Google in Settings")
            
            with col_c:
                if google_connected:
                    if st.button("📤 Send Email", type="primary", use_container_width=True):
                        client_email = selected_client.contact_info.email
                        # Confirm before sending
                        st.session_state.confirm_send = {
                            "to": client_email,
                            "subject": edited_subject,
                            "body": edited_body,
                            "client_id": selected_client_id
                        }
                        st.rerun()
                else:
                    st.button("📤 Send Email", type="primary", use_container_width=True, disabled=True,
                             help="Connect Google in Settings")
            
            # Send confirmation dialog
            if "confirm_send" in st.session_state:
                confirm = st.session_state.confirm_send
                st.divider()
                st.warning(f"⚠️ Send email to **{confirm['to']}**?")
                
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Send", type="primary", use_container_width=True):
                        success, result = google_service.send_email(
                            to=confirm["to"],
                            subject=confirm["subject"],
                            body=confirm["body"]
                        )
                        if success:
                            st.success(f"✅ Email sent to {confirm['to']}!")
                            del st.session_state.confirm_send
                            del st.session_state.current_draft
                            st.balloons()
                        else:
                            st.error(f"❌ Failed to send: {result}")
                            del st.session_state.confirm_send
                
                with col_no:
                    if st.button("❌ Cancel", use_container_width=True):
                        del st.session_state.confirm_send
                        st.rerun()
        
        elif "current_draft" not in st.session_state:
            st.info("Select a client and email type, then click 'Generate Draft' to create an email.")
    
    # Quick Book Meeting section (if Google connected)
    if google_connected and "current_draft" in st.session_state and selected_client:
        st.divider()
        with st.expander("📅 Book a Follow-up Meeting", expanded=False):
            st.caption("Schedule a meeting with this client directly to your Google Calendar")
            
            col_date, col_time, col_dur = st.columns(3)
            
            with col_date:
                meeting_date = st.date_input("Date", value=datetime.now().date() + timedelta(days=3), key="meeting_date")
            
            with col_time:
                meeting_time = st.time_input("Time", value=datetime.strptime("10:00", "%H:%M").time(), key="meeting_time")
            
            with col_dur:
                meeting_duration = st.selectbox("Duration (min)", [30, 45, 60, 90], index=2, key="meeting_duration")
            
            meeting_title = st.text_input("Meeting Title", 
                value=f"Meeting with {selected_client.full_name}", 
                key="meeting_title")
            
            meeting_notes = st.text_area("Meeting Notes/Agenda", 
                placeholder="Topics to discuss...",
                key="meeting_notes",
                height=100)
            
            include_client = st.checkbox("Send calendar invite to client", value=True, key="invite_client")
            
            if st.button("📅 Create Calendar Event", type="primary", use_container_width=True):
                start_datetime = datetime.combine(meeting_date, meeting_time)
                end_datetime = start_datetime + timedelta(minutes=meeting_duration)
                
                attendees = [selected_client.contact_info.email] if include_client else []
                
                success, result = google_service.create_event(
                    summary=meeting_title,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    description=meeting_notes,
                    attendee_emails=attendees,
                    send_notifications=include_client
                )
                
                if success:
                    invite_msg = f" (Invite sent to {selected_client.contact_info.email})" if include_client else ""
                    st.success(f"✅ Meeting booked!{invite_msg}")
                    st.balloons()
                else:
                    st.error(f"❌ Failed: {result}")


def render_settings(client_service: ClientService):
    """Render settings page with account info"""
    st.header("⚙️ Settings")
    
    # User Account Section (if login is enabled)
    if REQUIRE_LOGIN:
        st.subheader("👤 Your Account")
        user = get_current_user()
        
        if user:
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('picture'):
                    st.image(user.get('picture'), width=100)
                else:
                    st.markdown("👤")
            
            with col2:
                st.markdown(f"**Name:** {user.get('name', 'N/A')}")
                st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                st.markdown("**Status:** ✅ Connected")
                
                if st.button("🚪 Sign Out", key="settings_logout"):
                    google_service.logout()
                    st.rerun()
        
        st.divider()
    
    # Google Integration Status
    st.subheader("📧 Google Integration")
    
    if not google_service.is_enabled():
        st.warning("⚠️ Google integration is not configured.")
        with st.expander("📋 Admin Setup Required"):
            st.markdown("""
            **To enable Google integration:**
            
            1. Create a [Google Cloud Project](https://console.cloud.google.com/)
            2. Enable "Gmail API" and "Google Calendar API"
            3. Create OAuth credentials (Desktop app)
            4. Download `client_secret.json` to `credentials/` folder
            """)
        return
    
    if google_service.is_authenticated():
        st.success("✅ Google account connected")
        st.markdown("""
        **Available features:**
        - ✉️ Send emails directly from Email Drafts page
        - 📅 Book appointments on your Google Calendar
        - 📝 Save drafts to Gmail
        """)
    else:
        st.info("🔗 Not connected - sign in to enable Google features")
    
    # Calendar Settings (if authenticated)
    if google_service.is_authenticated():
        st.divider()
        st.subheader("📅 Upcoming Calendar Events")
        
        # Show upcoming events
        events = google_service.get_upcoming_events(days=7)
        if events:
            for event in events[:5]:
                start = event.get('start', '')
                if start:
                    try:
                        dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        start_str = dt.strftime("%a %d %b, %H:%M")
                    except:
                        start_str = start
                else:
                    start_str = "No time"
                st.caption(f"• {event.get('summary', 'No title')} - {start_str}")
        else:
            st.caption("No upcoming events in the next 7 days")
        
        # Find free slots
        st.divider()
        st.subheader("🕐 Find Free Slots")
        
        col_dur, col_days = st.columns(2)
        with col_dur:
            duration = st.selectbox("Meeting duration (min)", [30, 45, 60, 90], index=2, key="slot_duration")
        with col_days:
            days = st.selectbox("Days ahead", [3, 5, 7, 14], index=2, key="slot_days")
        
        if st.button("🔍 Find Available Slots", use_container_width=True):
            free_slots = google_service.find_free_slots(duration_minutes=duration, days_ahead=days)
            if free_slots:
                st.success(f"Found {len(free_slots)} available slots:")
                for slot in free_slots:
                    start_str = slot['start'].strftime("%A %d %b, %H:%M")
                    st.caption(f"✅ {start_str}")
            else:
                st.info("No free slots found in the selected period")
    
    st.divider()
    
    # Other Settings
    st.subheader("🎛️ Other Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**LLM Provider:**", st.session_state.get("llm_provider", "Unknown"))
    with col2:
        if st.button("🗑️ Clear All Dismissals", use_container_width=True):
            dismissal_service.clear_all()
            st.success("All dismissals cleared")
            st.rerun()


def render_compliance(client_service: ClientService):
    """Render FCA Consumer Duty compliance dashboard"""
    st.header("🏛️ FCA Consumer Duty Compliance")
    st.caption("Track regulatory requirements and demonstrate value to clients")
    
    clients = client_service.get_all_clients()
    summary = compliance_service.get_portfolio_compliance_summary(clients)
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "normal"
        if summary["average_score"] >= 80:
            score_color = "normal"
        elif summary["average_score"] >= 60:
            score_color = "off"
        else:
            score_color = "inverse"
        st.metric("Average Score", f"{summary['average_score']}/100", delta_color=score_color)
    
    with col2:
        st.metric("✅ Compliant", summary["compliant"], f"{round(summary['compliant']/summary['total_clients']*100)}%")
    
    with col3:
        st.metric("⚠️ At Risk", summary["at_risk"])
    
    with col4:
        st.metric("❌ Non-Compliant", summary["non_compliant"])
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Client Scores", "📋 Full Report"])
    
    with tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Common Issues")
            if summary["common_issues"]:
                for issue, count in list(summary["common_issues"].items())[:6]:
                    pct = round(count / summary["total_clients"] * 100)
                    st.progress(pct / 100, f"{issue}: {count} clients ({pct}%)")
            else:
                st.success("No common issues found! 🎉")
        
        with col_right:
            st.subheader("Priority Clients")
            st.caption("Lowest compliance scores - need attention")
            
            for client, score in summary["lowest_scoring"][:5]:
                status_icon = {"compliant": "✅", "at_risk": "⚠️", "non_compliant": "❌"}.get(score["status"].value, "❓")
                
                with st.expander(f"{status_icon} {client.full_name} - Score: {score['overall_score']}"):
                    # Score breakdown
                    st.caption("**Score Breakdown:**")
                    for metric, value in score["breakdown"].items():
                        nice_name = metric.replace("_", " ").title()
                        color = "🟢" if value >= 80 else "🟡" if value >= 50 else "🔴"
                        st.caption(f"{color} {nice_name}: {value}/100")
                    
                    st.caption("**Issues:**")
                    for issue in score["issues"]:
                        st.caption(f"• {issue}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📧 Schedule Review", key=f"comp_email_{client.id}"):
                            st.session_state.draft_for = client.id
                            st.session_state.draft_type = "review_reminder"
                            st.session_state.current_view = "emails"
                            st.rerun()
                    with col_b:
                        if st.button("👤 View Client", key=f"comp_client_{client.id}"):
                            st.session_state.selected_client = client.id
                            st.session_state.current_view = "clients"
                            st.rerun()
    
    with tab2:
        st.subheader("All Client Compliance Scores")
        
        # Filter options
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Compliant", "At Risk", "Non-Compliant"],
            key="compliance_filter"
        )
        
        # Build data for all clients
        client_data = []
        for client in clients:
            score = compliance_service.get_client_compliance_score(client)
            
            # Apply filter
            if status_filter != "All":
                filter_map = {"Compliant": "compliant", "At Risk": "at_risk", "Non-Compliant": "non_compliant"}
                if score["status"].value != filter_map.get(status_filter):
                    continue
            
            client_data.append({
                "Client": client.full_name,
                "Score": score["overall_score"],
                "Status": score["status"].value.replace("_", " ").title(),
                "Annual Review": score["breakdown"]["annual_review"],
                "Risk Profile": score["breakdown"]["risk_profile"],
                "Contact": score["breakdown"]["contact_frequency"],
                "Issues": len(score["issues"])
            })
        
        if client_data:
            # Sort by score
            client_data.sort(key=lambda x: x["Score"])
            
            # Display as table
            st.dataframe(
                client_data,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        min_value=0,
                        max_value=100,
                        format="%d"
                    ),
                    "Annual Review": st.column_config.ProgressColumn(
                        "Annual Review",
                        min_value=0,
                        max_value=100,
                        format="%d"
                    ),
                    "Risk Profile": st.column_config.ProgressColumn(
                        "Risk Profile",
                        min_value=0,
                        max_value=100,
                        format="%d"
                    ),
                    "Contact": st.column_config.ProgressColumn(
                        "Contact",
                        min_value=0,
                        max_value=100,
                        format="%d"
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No clients match the selected filter.")
    
    with tab3:
        st.subheader("Consumer Duty Compliance Report")
        
        if st.button("📋 Generate Full Report", type="primary"):
            with st.spinner("Generating compliance report..."):
                report = compliance_service.get_consumer_duty_report(clients)
                st.markdown(report)
                
                # Download option
                st.download_button(
                    "📥 Download Report",
                    report,
                    file_name=f"consumer_duty_report_{date.today()}.md",
                    mime="text/markdown"
                )
        else:
            st.info("Click the button above to generate a full FCA Consumer Duty compliance report.")
        
        st.divider()
        
        # Consumer Duty explainer
        with st.expander("ℹ️ About FCA Consumer Duty"):
            st.markdown("""
            **The Consumer Duty** came into force on 31 July 2023 and sets higher standards 
            of consumer protection in financial services.
            
            **Three Cross-Cutting Rules:**
            1. Act in good faith towards retail customers
            2. Avoid causing foreseeable harm
            3. Enable and support customers to pursue their financial objectives
            
            **Four Outcomes:**
            - **Products & Services:** Designed to meet target market needs
            - **Price & Value:** Fair value for money
            - **Consumer Understanding:** Clear, understandable communications
            - **Consumer Support:** Accessible, helpful support
            
            **Key Requirements for Advisors:**
            - Regular annual reviews (at least every 12 months)
            - Current risk profiles and suitability assessments
            - Documentation of value delivered
            - Proactive client communication
            """)


# ============== MAIN APP ==============

def main():
    """Main application entry point"""
    init_session_state()
    
    # Try to authenticate Google silently (if credentials exist)
    if google_service.is_enabled() and not google_service.is_authenticated():
        google_service.authenticate()
    
    # Check if login is required and user is not logged in
    if REQUIRE_LOGIN and not is_user_logged_in():
        render_login_page()
        return
    
    try:
        # Show loading message during initialization (only visible when actually loading)
        with st.spinner("🚀 Initializing Jarvis... Loading client data and setting up semantic search. This may take a moment on first load."):
            client_service, llm_service, vector_store = init_services()
        # Store vector_store in session state for sidebar access
        st.session_state.vector_store = vector_store
        
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        st.info("Make sure to run `python data/mock_generator.py` first to generate client data.")
        return
    
    # Sync current state to URL (for navigation changes)
    sync_state_to_url()
    
    render_sidebar(client_service)
    
    # Route to current view
    if st.session_state.current_view == "chat":
        render_chat(client_service, llm_service, vector_store)
    elif st.session_state.current_view == "alerts":
        render_alerts(client_service, llm_service)
    elif st.session_state.current_view == "dashboard":
        render_dashboard(client_service)
    elif st.session_state.current_view == "compliance":
        render_compliance(client_service)
    elif st.session_state.current_view == "clients":
        render_clients(client_service, vector_store)
    elif st.session_state.current_view == "emails":
        render_emails(client_service, llm_service)
    elif st.session_state.current_view == "settings":
        render_settings(client_service)


if __name__ == "__main__":
    main()
