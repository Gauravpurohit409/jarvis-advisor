"""
Jarvis Configuration
Central configuration for the Proactive Financial Advisor Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CLIENTS_FILE = DATA_DIR / "clients.json"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" (free) or "openai"

# Groq (Free LLM)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# OpenAI (Fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
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
