# 🤖 Jarvis - Proactive Financial Advisor Assistant

> **Your AI-powered second brain for client relationship management**

An intelligent assistant that helps UK Independent Financial Advisors (IFAs) stay proactive with their clients. Built for the **AdvisoryAI Hack-to-Hire Hackathon**.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Groq](https://img.shields.io/badge/LLM-Groq%20(Free)-orange.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Tech Stack](#️-tech-stack)
- [Setup Instructions](#-setup-instructions)
- [Environment Variables](#-environment-variables)
- [Running the Project](#-running-the-project)
- [Features](#-features-in-detail)
- [Project Structure](#-project-structure)
- [Demo Scenarios](#-demo-scenarios)

---

## 🎯 The Problem

**Problem Statement: Proactive AI Chatbot for UK IFAs**

Financial advisors manage **150-250 clients** but spend **60-70% of their time on admin**, not advice. They face critical challenges:

| Challenge | Impact |
|-----------|--------|
| ❌ Missing life events | Birthdays, weddings, retirements go unnoticed |
| ❌ Forgotten concerns | Issues discussed months ago get lost |
| ❌ Dormant clients | Clients slip away without the advisor realizing |
| ❌ Compliance gaps | FCA Consumer Duty annual reviews get missed |
| ❌ Scattered follow-ups | Commitments made but not tracked |
| ❌ Information overload | No quick way to prep before client calls |

---

## ✨ The Solution

**Jarvis** acts as the advisor's intelligent "second brain" - surfacing the right information at the right time through:

| Feature | Description |
|---------|-------------|
| 💬 **Smart Chat** | Natural language queries about your clients using RAG |
| 🚨 **Proactive Alerts** | Never miss birthdays, renewals, or overdue reviews |
| 🔍 **Semantic Search** | Find clients by context, not just keywords |
| 🏛️ **Compliance Tracking** | FCA Consumer Duty scoring and reporting |
| 📧 **AI Email Drafts** | One-click personalized client communications |
| 📊 **Dashboard** | Visual overview of what needs attention today |
| 👥 **Client Profiles** | Complete client details at your fingertips |

### Key Differentiators
- **Proactive, not reactive**: Jarvis tells you what you need to know *before* you ask
- **Context-aware**: Understands client relationships, history, and concerns
- **Compliance-first**: Built around FCA Consumer Duty requirements
- **Free to run**: Uses Groq's free LLM tier (no API costs)

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit 1.30+ | Interactive web UI |
| **Backend** | Python 3.9+ | Core application logic |
| **Data Models** | Pydantic 2.5+ | Type-safe data validation |
| **LLM** | Groq (llama-3.3-70b) | Natural language processing (FREE) |
| **Vector DB** | ChromaDB 0.4+ | Semantic search & RAG |
| **Embeddings** | all-MiniLM-L6-v2 | Client profile vectorization |

---

## 📦 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Gauravpurohit409/jarvis-advisor.git
cd jarvis-advisor
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

This installs:
- `streamlit` - Web UI framework
- `pydantic` - Data validation
- `groq` - LLM API client
- `chromadb` - Vector database
- `python-dotenv` - Environment management
- `python-docx`, `openpyxl` - Document parsing

### Step 3: Generate Mock Client Data

```bash
cd data
python3 mock_clients.py
cd ..
```

This generates **100 realistic UK client profiles** with:
- Demographics & family members
- Financial policies (pensions, ISAs, insurance)
- Meeting notes & interaction history
- Concerns & follow-up commitments
- Compliance records

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API key (see [Environment Variables](#-environment-variables) section).

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# ============================================
# LLM Provider API Keys
# ============================================

# Groq API Key (FREE - Recommended)
# Get your free key at: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# OpenAI API Key (Optional fallback)
# Get at: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# ============================================
# LLM Configuration
# ============================================

# Provider: "groq" (free) or "openai"
LLM_PROVIDER=groq

# Model names
GROQ_MODEL=llama-3.3-70b-versatile
OPENAI_MODEL=gpt-4o-mini
```

### Getting a Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys
4. Create a new API key
5. Copy and paste into your `.env` file

> **Note**: Jarvis works without an API key using intelligent template responses, but LLM features (chat, email drafts) require a valid key.

---

## 🚀 Running the Project

### Start the Application

```bash
python3 -m streamlit run app.py --server.port 8501
```

### Access Jarvis

Open your browser and navigate to:

- **Local**: http://localhost:8501
- **Network**: http://[your-ip]:8501

### Page URLs

Each page has a dedicated URL for easy navigation and bookmarking:

| Page | URL |
|------|-----|
| Dashboard | `http://localhost:8501/?page=dashboard` |
| Alerts | `http://localhost:8501/?page=alerts` |
| Chat | `http://localhost:8501/?page=chat` |
| Compliance | `http://localhost:8501/?page=compliance` |
| Clients | `http://localhost:8501/?page=clients` |
| Email Drafts | `http://localhost:8501/?page=emails` |

---

## 📱 Features in Detail

### 💬 Chat Interface (RAG-Powered)

Natural language queries powered by LLM + semantic search:

```
"Give me my daily briefing"
"What do I need to know about Mrs. Patterson?"
"Which clients are worried about inheritance tax?"
"Who should I call this week?"
"Show me clients approaching retirement"
"Find clients with children at university"
```

### 🚨 Proactive Alerts Engine

Automatically scans all clients and surfaces actionable alerts:

| Alert Type | Trigger | Priority |
|------------|---------|----------|
| 🎂 Birthdays | Client/family birthdays within 14 days | Medium |
| 💍 Anniversaries | Wedding anniversaries within 30 days | Low |
| 📋 Policy Renewals | Renewals due within 30 days | High |
| 📌 Follow-ups | Due or overdue commitments | High/Urgent |
| 📊 Annual Reviews | FCA-required reviews due/overdue | Urgent/High |
| 📞 No Contact | 90+ days since last interaction | Medium |
| 📈 Risk Profile | Stale profiles (12+ months) | Medium |
| 😟 Concerns | High-priority unaddressed concerns | High |

### 🏛️ FCA Consumer Duty Compliance

Comprehensive compliance scoring:

| Factor | Weight | Description |
|--------|--------|-------------|
| Annual Review | 25% | Last review date |
| Risk Profile | 20% | Currency of risk assessment |
| Suitability | 20% | Suitability confirmation |
| Contact Frequency | 15% | Regular client engagement |
| Documentation | 10% | Completeness of records |
| Value Demonstrated | 10% | Logged value delivery |

### 📧 AI Email Drafts

One-click personalized emails:
- Birthday wishes (with family awareness)
- Review reminders
- Check-ins for dormant clients
- Follow-up on commitments
- Policy renewal notices

### 👥 Client Profiles

Complete client view including:
- Personal & contact information
- Family members & relationships
- All financial policies
- Concerns & their status
- Compliance status
- Interaction history
- Quick action buttons

---

## 📁 Project Structure

```
jarvis/
├── app.py                    # Main Streamlit application (1700+ lines)
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # API keys (git-ignored)
├── .env.example              # Template for environment variables
├── README.md                 # This file
├── DOCUMENTATION.md          # Detailed technical documentation
│
├── data/
│   ├── schema.py             # Pydantic data models
│   ├── mock_clients.py       # Client data generator (100 clients)
│   └── clients.json          # Generated client database
│
├── services/
│   ├── client_service.py     # Client CRUD & search operations
│   ├── llm_service.py        # LLM provider abstraction (Groq/OpenAI)
│   ├── vector_store.py       # ChromaDB semantic search
│   ├── alerts_service.py     # Proactive alert detection
│   └── compliance_service.py # FCA Consumer Duty tracking
│
├── .streamlit/
│   └── config.toml           # Streamlit configuration
│
└── chroma_db/                # Persistent vector embeddings
```

---

## 🎬 Demo Scenarios

### Scenario 1: Morning Briefing
1. Open Jarvis at http://localhost:8501
2. View the Dashboard for today's priorities
3. Or type "Give me my daily briefing" in Chat

### Scenario 2: Client Call Preparation
1. Search for a client name in the sidebar
2. Click to view their full profile
3. Review concerns, policies, and recent notes
4. Ask: "What do I need to know about [Client Name]?"

### Scenario 3: Compliance Audit
1. Navigate to 🏛️ Compliance page
2. Review portfolio-wide compliance rate
3. Identify at-risk clients (red/amber scores)
4. Schedule reviews directly from the interface

### Scenario 4: Proactive Outreach
1. Navigate to 🚨 Alerts page
2. Filter by "Birthday" or "Dormant"
3. Click "Draft Email" on any alert
4. Review AI-generated personalized message
5. Copy and send via your email client

### Scenario 5: Semantic Client Search
1. Go to 💬 Chat
2. Ask natural questions like:
   - "Who is worried about retirement income?"
   - "Show clients with children starting university"
   - "Find high net worth clients needing reviews"

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip3 install -r requirements.txt` |
| "No clients found" | Run `python3 data/mock_clients.py` |
| LLM errors | Check your `GROQ_API_KEY` in `.env` |
| Port already in use | Change port: `--server.port 8502` |

### Regenerating Client Data

```bash
cd data
python3 mock_clients.py
```

This creates fresh client data with:
- 100 clients total
- ~15 dormant clients
- ~20 overdue reviews
- ~12 reviews due soon
- ~8 birthdays in next 14 days
- Various follow-ups and alerts

---

## 👨‍💻 Author

**Gaurav Purohit**

- GitHub: [@Gauravpurohit409](https://github.com/Gauravpurohit409)

---

## 📄 License

Built for **AdvisoryAI Hack-to-Hire 2026**

---

<p align="center">
  <b>🤖 Jarvis - Because great advice starts with great information</b>
</p>
