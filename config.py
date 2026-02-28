"""
Jarvis Configuration
Central configuration for the Proactive Financial Advisor Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to load Streamlit secrets (for Streamlit Cloud deployment)
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CLIENTS_FILE = DATA_DIR / "clients.json"
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" (free) or "openai"

# Groq (Free LLM)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# OpenAI (Fallback)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Application Settings
APP_NAME = "Jarvis - Proactive Advisor Assistant"
APP_VERSION = "1.0.0"

# Compliance Thresholds (UK IFA specific)
ANNUAL_REVIEW_MONTHS = 12  # FCA Consumer Duty requirement
DORMANT_CLIENT_DAYS = 90  # Days without contact before flagging
COLD_CLIENT_DAYS = 180  # Days without contact - high priority
CRITICAL_CLIENT_DAYS = 365  # Days without contact - compliance risk

# Milestone Birthdays (pension/retirement significance)
MILESTONE_BIRTHDAYS = [55, 60, 65, 70, 75]

# Tax Year Deadlines (UK)
TAX_YEAR_END = "04-05"  # 5th April
ISA_DEADLINE = "04-05"

# ============================================
# Google API Configuration
# ============================================
CREDENTIALS_DIR = BASE_DIR / "credentials"
GOOGLE_ENABLED = os.getenv("GOOGLE_ENABLED", "true").lower() == "true"
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", str(CREDENTIALS_DIR / "client_secret.json"))
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", str(CREDENTIALS_DIR / "google_token.json"))

# Try to load Google credentials from Streamlit secrets (for cloud deployment)
GOOGLE_CLIENT_ID = None
GOOGLE_CLIENT_SECRET = None
try:
    import streamlit as st
    GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", os.getenv("GOOGLE_CLIENT_ID"))
    GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", os.getenv("GOOGLE_CLIENT_SECRET"))
except:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Gmail & Calendar API scopes (includes userinfo for login)
GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]

# Login Settings
REQUIRE_LOGIN = os.getenv("REQUIRE_LOGIN", "true").lower() == "true"
