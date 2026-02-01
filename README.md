# Jarvis - Proactive Financial Advisor Assistant

An AI-powered assistant that helps UK Independent Financial Advisors (IFAs) stay proactive with their clients. Built for the AdvisoryAI Hack-to-Hire hackathon.

## The Problem

Financial advisors manage 150-250 clients but spend 60-70% of their time on admin, not advice. They:
- Miss important life events (weddings, birthdays, retirements)
- Forget concerns clients expressed months ago
- Let clients go "dormant" without realizing
- Struggle to track compliance deadlines (annual reviews)
- Make follow-up commitments they can't keep track of

## The Solution

Jarvis acts as the advisor's "second brain" - surfacing the right information at the right time:

✅ **Daily Briefing** - Know what to focus on each morning  
✅ **Client Memory Search** - Instantly recall any client detail  
✅ **Proactive Alerts** - Birthdays, review deadlines, dormant clients  
✅ **Concern Tracking** - Never forget what's worrying your clients  
✅ **Email Drafts** - One-click personalized communications  

## Quick Start

### 1. Install Dependencies

```bash
cd jarvis
pip install -r requirements.txt
```

### 2. Generate Mock Data

```bash
cd data
python mock_generator.py
```

This creates 20 realistic UK client profiles with:
- Demographics and family members
- Policies (pensions, ISAs, protection)
- Meeting notes and interaction history
- Concerns and follow-up commitments
- Compliance records

### 3. (Optional) Add LLM API Key

Get a **free** Groq API key at: https://console.groq.com/keys

Add to `.env`:
```
GROQ_API_KEY=your_key_here
```

Without an API key, Jarvis runs in mock mode with template responses.

### 4. Run the App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Features

### 💬 Chat Interface
Ask Jarvis anything:
- "Give me my daily briefing"
- "What do I need to know about Mrs. Patterson?"
- "Who should I call this week?"
- "Which clients have concerns about inheritance tax?"

### 📊 Dashboard
Visual overview of:
- Overdue annual reviews
- Dormant clients (no contact in 90+ days)
- Upcoming birthdays (including milestone ages)
- Pending follow-up commitments

### 👥 Client Directory
Search and filter clients by:
- Name
- Concern type
- Review status
- Contact recency

### 📧 Email Drafts
One-click personalized emails:
- Birthday wishes
- Review reminders
- Check-in messages
- Follow-up communications

## Project Structure

```
jarvis/
├── app.py                    # Streamlit main application
├── config.py                 # Configuration and settings
├── requirements.txt          # Python dependencies
├── .env                      # API keys (git-ignored)
├── data/
│   ├── schema.py            # Pydantic data models
│   ├── mock_generator.py    # Generates realistic client data
│   └── clients.json         # Generated mock data
└── services/
    ├── client_service.py    # Client data operations
    └── llm_service.py       # LLM provider abstraction
```

## Tech Stack

- **Backend**: Python 3.10+
- **UI**: Streamlit
- **Data Models**: Pydantic
- **LLM**: Groq (free) / OpenAI (fallback)
- **Vector Store**: ChromaDB (Phase 2)

## Roadmap (Phases)

### Phase 1 ✅ Foundation
- [x] Project structure
- [x] Client data schema
- [x] Mock data generator
- [x] Client service (CRUD)
- [x] LLM service abstraction
- [x] Basic Streamlit app

### Phase 2 🔜 Semantic Search
- [ ] Vector store with ChromaDB
- [ ] Semantic search over meeting notes
- [ ] Client context retrieval

### Phase 3 🔜 Proactive Alerts
- [ ] Milestone birthday detection
- [ ] Policy renewal alerts
- [ ] Dormant client flagging
- [ ] Concern re-surfacing

### Phase 4 🔜 Compliance
- [ ] Annual review tracker
- [ ] Consumer Duty value log
- [ ] Suitability validation

### Phase 5 🔜 Polish
- [ ] Enhanced chat
- [ ] Email templates
- [ ] Dashboard refinements

## License

Built for AdvisoryAI Hack-to-Hire 2026
