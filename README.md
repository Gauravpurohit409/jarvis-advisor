# 🤖 Jarvis - Proactive Financial Advisor Assistant

> **Your AI-powered second brain for client relationship management**

An intelligent assistant that helps UK Independent Financial Advisors (IFAs) stay proactive with their clients. Built for the AdvisoryAI Hack-to-Hire hackathon.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 The Problem

Financial advisors manage **150-250 clients** but spend **60-70% of their time on admin**, not advice. They:

- ❌ Miss important life events (weddings, birthdays, retirements)
- ❌ Forget concerns clients expressed months ago
- ❌ Let clients go "dormant" without realizing
- ❌ Struggle to track compliance deadlines (annual reviews)
- ❌ Make follow-up commitments they can't keep track of
- ❌ Risk FCA Consumer Duty non-compliance

---

## ✨ The Solution

**Jarvis** acts as the advisor's "second brain" - surfacing the right information at the right time:

| Feature | Description |
|---------|-------------|
| 💬 **Smart Chat** | Ask anything about your clients using natural language |
| 🚨 **Proactive Alerts** | Never miss birthdays, renewals, or overdue reviews |
| 🔍 **Semantic Search** | Find clients by context, not just keywords |
| 🏛️ **Compliance Tracking** | FCA Consumer Duty scoring and reporting |
| 📧 **Email Drafts** | AI-generated personalized communications |
| 📊 **Dashboard** | Visual overview of what needs attention |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Gauravpurohit409/jarvis-advisor.git
cd jarvis-advisor
pip3 install -r requirements.txt
```

### 2. Generate Client Data

```bash
python3 data/mock_clients.py
```

Creates **13 realistic UK client profiles** with complete data:
- Demographics & family members
- Policies (pensions, ISAs, protection products)
- Meeting notes & interaction history
- Concerns & follow-up commitments
- Compliance records

### 3. (Optional) Add AI API Key

Get a **free** Groq API key: https://console.groq.com/keys

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

> Without an API key, Jarvis runs with intelligent template responses.

### 4. Launch Jarvis

```bash
python3 -m streamlit run app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

---

## 📱 Features in Detail

### 💬 Chat Interface
Natural language queries powered by LLM + semantic search:

```
"Give me my daily briefing"
"What do I need to know about Mrs. Patterson?"
"Which clients are worried about inheritance tax?"
"Who should I call this week?"
"Show me clients approaching retirement"
```

### 🚨 Proactive Alerts Engine
Automatically scans all clients and detects:

| Alert Type | Trigger |
|------------|---------|
| 🎂 Birthdays | Client/family birthdays within 14 days |
| 📋 Policy Renewals | Renewals due within 30 days |
| 💰 Policy Maturities | Maturities within 60 days |
| 📌 Follow-ups | Due or overdue commitments |
| 📊 Annual Reviews | FCA-required reviews due/overdue |
| 📞 No Contact | 90+ days since last interaction |
| 📈 Risk Profile | Stale profiles (12+ months) |
| 😟 Concerns | High-priority unaddressed concerns |
| 🎯 Retirement | Clients within 2 years of state pension age |

Each alert has:
- Priority level (Urgent/High/Medium/Low)
- One-click email drafting
- Direct link to client profile

### 🏛️ FCA Consumer Duty Compliance

Comprehensive compliance scoring based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Annual Review | 25% | Last review date |
| Risk Profile | 20% | Currency of risk assessment |
| Suitability | 20% | Suitability confirmation |
| Contact Frequency | 15% | Regular client engagement |
| Documentation | 10% | Completeness of records |
| Value Demonstrated | 10% | Logged value delivery |

Features:
- Individual client scores (0-100)
- Portfolio-wide compliance rate
- Automated issue detection
- Downloadable Consumer Duty reports

### 🔍 Semantic Search
ChromaDB-powered vector search finds clients by meaning:

- "clients worried about market volatility"
- "pension review needed"
- "spouse named Sarah"
- "concerned about care home costs"

### 📧 AI Email Drafts
One-click personalized emails for:
- Birthday wishes
- Review reminders
- Check-ins
- Follow-ups
- Policy renewals
- Retirement planning

---

## 🏗️ Architecture

```
jarvis/
├── app.py                          # Streamlit main application (900+ lines)
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env                           # API keys (git-ignored)
│
├── data/
│   ├── schema.py                  # Pydantic models (Client, Alert, etc.)
│   ├── mock_clients.py            # Realistic UK client generator
│   └── clients.json               # Generated client data
│
├── services/
│   ├── client_service.py          # Client CRUD & search operations
│   ├── llm_service.py             # LLM provider abstraction
│   ├── vector_store.py            # ChromaDB semantic search
│   ├── alerts_service.py          # Proactive alert detection
│   └── compliance_service.py      # FCA Consumer Duty tracking
│
└── chroma_db/                     # Persistent vector embeddings
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.30+ |
| **Backend** | Python 3.9+ |
| **Data Models** | Pydantic |
| **LLM** | Groq (free tier) / OpenAI |
| **Vector DB** | ChromaDB |
| **Embeddings** | all-MiniLM-L6-v2 |

---

## ✅ Development Phases

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Foundation: Schema, services, basic UI |
| **Phase 2** | ✅ Complete | Semantic search with ChromaDB |
| **Phase 3** | ✅ Complete | Proactive alerts engine |
| **Phase 4** | ✅ Complete | FCA Consumer Duty compliance |
| **Phase 5** | ✅ Complete | Polish, documentation, demo prep |

---

## 🎬 Demo Scenarios

### Scenario 1: Morning Briefing
1. Open Jarvis
2. Click "🌅 Daily Briefing" or ask "What should I focus on today?"
3. Review prioritized alerts and tasks

### Scenario 2: Client Preparation
1. Search for client name in sidebar
2. Click to view full profile
3. Review concerns, policies, and recent interactions
4. Use chat: "What do I need to know about [Client Name] before our call?"

### Scenario 3: Compliance Check
1. Navigate to 🏛️ Compliance
2. Review portfolio-wide compliance rate
3. Identify at-risk clients
4. Generate Consumer Duty report

### Scenario 4: Proactive Outreach
1. Navigate to 🚨 Alerts
2. Filter by "Birthday" or "No Contact"
3. Click "📧 Draft Email" on any alert
4. Review AI-generated personalized message

---

## 🔧 Configuration

Edit `config.py` or environment variables:

```python
# LLM Settings
GROQ_API_KEY = ""          # Free at console.groq.com
OPENAI_API_KEY = ""        # Fallback option

# Alert Thresholds
BIRTHDAY_DAYS_AHEAD = 14
POLICY_RENEWAL_DAYS = 30
NO_CONTACT_DAYS = 90
ANNUAL_REVIEW_MONTHS = 12
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

Built for **AdvisoryAI Hack-to-Hire 2026**

---

## 👨‍💻 Author

**Gaurav Purohit**

- GitHub: [@Gauravpurohit409](https://github.com/Gauravpurohit409)

---

<p align="center">
  <b>🤖 Jarvis - Because great advice starts with great information</b>
</p>
