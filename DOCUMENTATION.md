# 🤖 Jarvis - Technical Documentation

> Complete technical documentation for the Jarvis Proactive Financial Advisor Assistant

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Phase-by-Phase Development](#phase-by-phase-development)
6. [Application Flow](#application-flow)
7. [Key Code Concepts](#key-code-concepts)
8. [Data Models](#data-models)
9. [Services Documentation](#services-documentation)
10. [Configuration](#configuration)
11. [Demo Scenarios](#demo-scenarios)

---

## Problem Statement

UK Independent Financial Advisors (IFAs) manage **150-250 clients** but spend **60-70% of their time on admin**, not advice.

### Pain Points:

| Problem | Impact |
|---------|--------|
| ❌ Miss important life events | Clients feel forgotten |
| ❌ Forget concerns from months ago | Trust erosion |
| ❌ Clients go "dormant" | Revenue loss |
| ❌ Miss compliance deadlines | FCA regulatory risk |
| ❌ Can't track follow-up promises | Broken commitments |
| ❌ Information scattered | Inefficient prep time |

### The Core Issue:
> "Advisors have the data, but they don't get it at the right time"

---

## Solution Overview

**Jarvis** acts as the advisor's AI-powered "second brain" - surfacing the right information at the right time.

### Key Features:

| Feature | Description |
|---------|-------------|
| 💬 **Smart Chat** | Natural language queries about clients |
| 🚨 **Proactive Alerts** | Auto-detect birthdays, renewals, reviews |
| 🔍 **Semantic Search** | Find clients by meaning, not keywords |
| 🏛️ **Compliance Tracking** | FCA Consumer Duty scoring |
| 📧 **Email Drafts** | AI-generated personalized emails |
| 📊 **Dashboard** | Visual overview of priorities |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Financial Advisor)                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI (app.py)                       │
│  ┌─────────┐ ┌────────┐ ┌───────────┐ ┌──────────┐ ┌─────────┐ │
│  │  Chat   │ │ Alerts │ │ Dashboard │ │Compliance│ │ Clients │ │
│  └─────────┘ └────────┘ └───────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
         ┌──────────────┐ ┌────────────┐ ┌─────────────┐
         │ LLM Service  │ │   Vector   │ │   Client    │
         │  (AI Chat)   │ │   Store    │ │   Service   │
         └──────────────┘ └────────────┘ └─────────────┘
                │                │              │
                ▼                ▼              ▼
         ┌──────────────┐ ┌────────────┐ ┌─────────────┐
         │ Groq/OpenAI  │ │  ChromaDB  │ │clients.json │
         │     API      │ │(Embeddings)│ │   (Data)    │
         └──────────────┘ └────────────┘ └─────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit 1.30 | Interactive UI |
| **Data Models** | Pydantic | Type-safe schemas |
| **LLM** | Groq (free tier) | AI chat & generation |
| **Vector DB** | ChromaDB | Semantic search |
| **Embeddings** | all-MiniLM-L6-v2 | Text vectorization |

---

## Project Structure

```
jarvis/
├── app.py                          # Main Streamlit application (900+ lines)
│                                   # - Navigation routing
│                                   # - All render_* functions
│                                   # - Session state management
│
├── config.py                       # Configuration settings
│                                   # - API keys
│                                   # - Model settings
│                                   # - Thresholds
│
├── requirements.txt                # Python dependencies
├── .env                           # API keys (git-ignored)
├── .env.example                   # Template for .env
│
├── data/
│   ├── schema.py                  # Pydantic data models
│   │                              # - Client, Policy, Concern
│   │                              # - Alert, AlertType, AlertPriority
│   │                              # - 20+ model classes
│   │
│   ├── mock_clients.py            # Mock data generator
│   │                              # - 13 realistic UK clients
│   │                              # - Families, policies, concerns
│   │
│   └── clients.json               # Generated client data
│
├── services/
│   ├── client_service.py          # Client CRUD operations
│   │                              # - Load/save from JSON
│   │                              # - Search and filter
│   │                              # - Daily briefing data
│   │
│   ├── llm_service.py             # LLM provider abstraction
│   │                              # - Groq, OpenAI, Mock providers
│   │                              # - Chat, email drafting
│   │                              # - System prompts
│   │
│   ├── vector_store.py            # Semantic search
│   │                              # - ChromaDB integration
│   │                              # - Document indexing
│   │                              # - Similarity search
│   │
│   ├── alerts_service.py          # Proactive alerts engine
│   │                              # - 10+ alert types
│   │                              # - Priority scoring
│   │                              # - Daily briefing
│   │
│   └── compliance_service.py      # FCA Consumer Duty tracking
│                                  # - Compliance scoring
│                                  # - Report generation
│
└── chroma_db/                     # Persistent vector embeddings
```

---

## Phase-by-Phase Development

### Phase 1: Foundation ✅

**Goal:** Basic project structure and data handling

**What We Built:**

1. **Data Schema** (`data/schema.py`)
   - `Client` model with 20+ fields
   - `Policy` (pensions, ISAs, insurance)
   - `Concern` (client worries)
   - `FollowUp` (advisor commitments)
   - `MeetingNote` (interaction history)
   - `ComplianceRecord` (FCA tracking)

2. **Mock Data Generator** (`data/mock_clients.py`)
   - 13 realistic UK clients
   - Real names, addresses, policies
   - Varied concerns and situations

3. **Client Service** (`services/client_service.py`)
   - Load/save clients from JSON
   - Search by name
   - Get daily briefing data
   - Filter by status

4. **LLM Service** (`services/llm_service.py`)
   - Provider abstraction (Strategy Pattern)
   - Groq (free), OpenAI, Mock support
   - Chat and email generation

5. **Basic Streamlit App** (`app.py`)
   - Sidebar navigation
   - Chat interface
   - Dashboard view
   - Client directory

---

### Phase 2: Semantic Search ✅

**Goal:** Find clients by meaning, not just keywords

**What We Built:**

**Vector Store Service** (`services/vector_store.py`)

```
How it works:

1. Each client → 6 document types indexed:
   - Overview (name, age, portfolio)
   - Concerns (what worries them)
   - Policies (financial products)
   - Family (spouse, children)
   - Notes (meeting history)
   - Follow-ups (commitments)

2. Documents embedded using all-MiniLM-L6-v2 model

3. Stored in ChromaDB (77 documents for 13 clients)
```

**Example Searches:**
```
"clients worried about retirement"     → Finds retirement concerns
"spouse named Sarah"                   → Finds family relationships
"pension review needed"                → Finds pension-related notes
"market volatility concerns"           → Finds anxiety about markets
```

---

### Phase 3: Proactive Alerts ✅

**Goal:** Never miss important client events

**What We Built:**

**Alerts Service** (`services/alerts_service.py`)

| Alert Type | Trigger | Priority Logic |
|------------|---------|----------------|
| 🎂 Birthday | Within 14 days | High if ≤3 days |
| 📋 Policy Renewal | Within 30 days | Urgent if overdue |
| 💰 Policy Maturity | Within 60 days | High if ≤14 days |
| 📌 Follow-up Due | Within 3 days | Urgent if overdue |
| 📊 Annual Review | Within 30 days | Urgent if overdue |
| 📞 No Contact | 90+ days | High if 180+ days |
| 📈 Risk Profile | 12+ months old | Medium |
| 😟 High Concern | Active & undiscussed 30+ days | High |
| 🎯 Retirement | Within 2 years of age 67 | High |

**Alert Priority Levels:**
- 🔴 **Urgent** - Requires immediate action
- 🟠 **High** - Important, address this week
- 🟡 **Medium** - Address when possible
- 🟢 **Low** - Nice to do

**Features:**
- Filter by priority and type
- One-click email drafting
- AI-powered daily briefing
- Dismiss functionality

---

### Phase 4: FCA Compliance ✅

**Goal:** Track Consumer Duty requirements

**What We Built:**

**Compliance Service** (`services/compliance_service.py`)

**FCA Consumer Duty Background:**
> The Consumer Duty (effective July 2023) requires firms to:
> 1. Act in good faith towards retail customers
> 2. Avoid causing foreseeable harm
> 3. Enable customers to pursue their financial objectives

**Compliance Scoring (0-100):**

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| Annual Review | 25% | When was last review? |
| Risk Profile | 20% | Is risk assessment current? |
| Suitability | 20% | Products confirmed suitable? |
| Contact Frequency | 15% | Regular communication? |
| Documentation | 10% | Complete records? |
| Value Demonstrated | 10% | Logged value delivered? |

**Status Classification:**
- ✅ **Compliant** (80-100): Meeting all requirements
- ⚠️ **At Risk** (60-79): Some gaps to address
- ❌ **Non-Compliant** (<60): Urgent attention needed

**Features:**
- Portfolio-wide compliance rate
- Individual client scores
- Common issues identification
- Downloadable Consumer Duty report

---

### Phase 5: Polish ✅

**Goal:** Production-ready documentation and UX

**What We Built:**
- Comprehensive README.md
- This technical documentation
- Demo scenarios
- Error handling improvements
- Navigation fixes

---

## Application Flow

### 1. App Startup Flow

```
User runs: streamlit run app.py
            │
            ▼
    ┌───────────────────┐
    │   app.py main()   │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ init_session_state│  ← Creates empty messages[], selected_client, etc.
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │  init_services()  │  ← @st.cache_resource (runs once, cached)
    └───────────────────┘
            │
    ┌───────┴───────┬────────────────┐
    ▼               ▼                ▼
┌─────────┐   ┌───────────┐   ┌─────────────┐
│ Client  │   │    LLM    │   │   Vector    │
│ Service │   │  Service  │   │    Store    │
└─────────┘   └───────────┘   └─────────────┘
    │               │                │
    ▼               ▼                ▼
Load 13        Auto-select      Index 77 docs
clients        Groq → OpenAI    in ChromaDB
from JSON      → Mock
```

### 2. Chat Flow

```
User types: "What should I know about Mrs. Patterson?"
            │
            ▼
    ┌───────────────────┐
    │  render_chat()    │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Semantic Search   │  ← vector_store.get_relevant_context()
    │  "Patterson"      │     Returns matching documents
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Build Context     │  ← Combine: client data + search results
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │  LLM Service      │  ← System prompt + context + user message
    │    .chat()        │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │  Groq API Call    │  ← llama-3.3-70b-versatile model
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Display Response  │  ← st.markdown(response)
    └───────────────────┘
```

### 3. Alerts Flow

```
User clicks: 🚨 Alerts
            │
            ▼
    ┌───────────────────┐
    │  render_alerts()  │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Get All Clients   │  ← client_service.get_all_clients()
    └───────────────────┘
            │
            ▼
    ┌───────────────────────────────────────┐
    │     alerts_service.generate_all()     │
    │                                       │
    │  For each of 13 clients, check:       │
    │  ├── _check_birthday()                │
    │  ├── _check_policy_renewals()         │
    │  ├── _check_policy_maturities()       │
    │  ├── _check_follow_ups()              │
    │  ├── _check_annual_review()           │
    │  ├── _check_no_contact()              │
    │  ├── _check_life_events()             │
    │  ├── _check_risk_profile()            │
    │  ├── _check_concerns()                │
    │  └── _check_retirement()              │
    └───────────────────────────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Sort by Priority  │  ← Urgent → High → Medium → Low
    │ Then by Due Date  │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Display Alerts    │  ← Expandable cards with action buttons
    └───────────────────┘
```

### 4. Email Draft Flow

```
User clicks: 📧 Draft Email (from any alert or client)
            │
            ▼
    ┌───────────────────┐
    │ Set session state │  ← draft_for=client_id
    │                   │     draft_type="birthday"
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Navigate to Email │  ← current_view = "emails"
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ render_emails()   │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Get Client Summary│  ← Full profile as JSON context
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ llm_service       │
    │  .draft_email()   │  ← Prompt: "Draft a warm birthday email..."
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Groq generates    │  ← Personalized with client details
    │ email draft       │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Display in UI     │  ← Copy / Regenerate buttons
    └───────────────────┘
```

### 5. Compliance Flow

```
User clicks: 🏛️ Compliance
            │
            ▼
    ┌───────────────────┐
    │render_compliance()│
    └───────────────────┘
            │
            ▼
    ┌────────────────────────────────────────┐
    │ compliance_service                     │
    │  .get_portfolio_compliance_summary()   │
    │                                        │
    │ For each client, calculate:            │
    │  ├── _score_annual_review()   (25%)    │
    │  ├── _score_risk_profile()    (20%)    │
    │  ├── _score_suitability()     (20%)    │
    │  ├── _score_contact_frequency()(15%)   │
    │  ├── _score_documentation()   (10%)    │
    │  └── _score_value_demonstrated()(10%)  │
    │                                        │
    │ Total = Weighted Average (0-100)       │
    └────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Classify Status   │
    │ ≥80: Compliant ✅ │
    │ ≥60: At Risk ⚠️   │
    │ <60: Non-Comp ❌  │
    └───────────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Display Dashboard │  ← Metrics, tables, downloadable report
    └───────────────────┘
```

---

## Key Code Concepts

### 1. Abstract Base Classes (ABC)

**Location:** `services/llm_service.py`

```python
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Send chat messages and get response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        pass
```

**Why Use ABC?**

| Component | Purpose |
|-----------|---------|
| `ABC` | Makes class abstract - cannot instantiate directly |
| `@abstractmethod` | Methods MUST be implemented by child classes |

**Benefits:**
1. **Enforces contract** - All providers must implement `chat()` and `is_available()`
2. **Prevents bugs** - Python raises error if method not implemented
3. **Enables polymorphism** - Swap providers without changing calling code

**Example - Provider Pattern:**
```python
# All these work identically because they share the interface:
provider = GroqProvider()      # Uses Groq API
provider = OpenAIProvider()    # Uses OpenAI API  
provider = MockProvider()      # Uses templates

# Same method call works for all:
response = provider.chat(messages)
```

---

### 2. Temperature Parameter

**Location:** `services/llm_service.py`

```python
def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
```

**What is Temperature?**

Temperature controls the **randomness/creativity** of LLM responses.

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| **0.0** | Deterministic, picks most likely token | Math, code, facts |
| **0.3** | Very focused, minimal variation | Data extraction |
| **0.5** | Balanced, slight creativity | Business writing |
| **0.7** | **Good balance** - creative yet coherent | **Chat, emails** |
| **1.0** | More creative, varied | Brainstorming |
| **1.5+** | Very random, can be incoherent | Experimental |

**Why 0.7 for Jarvis?**

Jarvis needs to:
- ✅ Sound natural (not robotic)
- ✅ Vary email drafts (not identical)
- ✅ Stay coherent (not hallucinate)
- ✅ Be professional (financial context)

**Different Temperatures in Code:**
```python
# Daily briefing - more factual
temperature=0.5

# Email drafts - more creative
temperature=0.7

# General chat - balanced
temperature=0.7
```

---

### 3. Session State

**Location:** `app.py`

```python
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"
```

**What is Session State?**

Streamlit reruns the entire script on every interaction. Session state persists data across reruns.

**Key Variables:**

| Variable | Purpose |
|----------|---------|
| `messages` | Chat conversation history |
| `selected_client` | Currently viewed client ID |
| `current_view` | Active navigation tab |
| `client_filter` | Dashboard filter state |
| `draft_for` | Client ID for email draft |
| `draft_type` | Type of email to draft |
| `vector_store` | ChromaDB instance |

---

### 4. Caching with @st.cache_resource

**Location:** `app.py`

```python
@st.cache_resource
def init_services():
    """Initialize services (cached)"""
    client_service = ClientService()
    llm_service = LLMService()
    vector_store = get_vector_store()
    return client_service, llm_service, vector_store
```

**Why Cache?**

- Services are expensive to initialize (load data, connect to APIs)
- Without caching: reinitialize on every click
- With `@st.cache_resource`: initialize once, reuse forever

---

## Data Models

### Client Model (Simplified)

```python
class Client(BaseModel):
    # Identity
    id: str
    title: str                    # Mr, Mrs, Ms, Dr
    first_name: str
    last_name: str
    date_of_birth: date
    
    # Contact
    contact_info: ContactInfo     # Email, phone, address
    
    # Family
    marital_status: str
    family_members: List[FamilyMember]
    
    # Financial
    policies: List[Policy]        # Pensions, ISAs, insurance
    total_portfolio_value: float
    risk_profile: RiskProfile
    
    # Relationship
    concerns: List[Concern]       # What worries them
    follow_ups: List[FollowUp]    # Advisor commitments
    meeting_notes: List[MeetingNote]
    interactions: List[Interaction]
    life_events: List[LifeEvent]
    
    # Compliance
    compliance: ComplianceRecord
    
    # Metadata
    client_since: date
    tags: List[str]
```

### Alert Model

```python
class Alert(BaseModel):
    id: str
    client_id: str
    client_name: str
    alert_type: AlertType         # BIRTHDAY, POLICY_RENEWAL, etc.
    priority: AlertPriority       # URGENT, HIGH, MEDIUM, LOW
    title: str
    description: str
    due_date: Optional[date]
    days_until_due: Optional[int]
    is_dismissed: bool = False
    related_data: dict = {}       # Extra context
```

### Data Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                                │
├─────────────────────────────────────────────────────────────┤
│       │                                                      │
│       ├── family_members[]     → FamilyMember               │
│       │                           - name, relationship, dob │
│       │                                                      │
│       ├── policies[]           → Policy                     │
│       │                           - type, provider, value   │
│       │                                                      │
│       ├── concerns[]           → Concern                    │
│       │                           - topic, severity, status │
│       │                                                      │
│       ├── follow_ups[]         → FollowUp                   │
│       │                           - commitment, deadline    │
│       │                                                      │
│       ├── meeting_notes[]      → MeetingNote                │
│       │                           - date, summary, actions  │
│       │                                                      │
│       ├── interactions[]       → Interaction                │
│       │                           - date, method, summary   │
│       │                                                      │
│       ├── life_events[]        → LifeEvent                  │
│       │                           - type, date, description │
│       │                                                      │
│       └── compliance           → ComplianceRecord           │
│                                   - review dates, status    │
└─────────────────────────────────────────────────────────────┘
```

---

## Services Documentation

### ClientService

**File:** `services/client_service.py`

| Method | Purpose |
|--------|---------|
| `load_clients()` | Load from clients.json |
| `save_clients()` | Persist to clients.json |
| `get_all_clients()` | Return all clients |
| `get_client_by_id(id)` | Find specific client |
| `search_by_name(query)` | Search by name |
| `get_daily_briefing_data()` | Aggregated briefing data |
| `get_client_summary(id)` | Full client details as dict |

### LLMService

**File:** `services/llm_service.py`

| Method | Purpose |
|--------|---------|
| `chat(message, context)` | Send message, get response |
| `draft_email(client, type)` | Generate email draft |
| `generate_daily_briefing(data)` | AI briefing summary |
| `get_client_insights(client)` | AI client analysis |

### VectorStoreService

**File:** `services/vector_store.py`

| Method | Purpose |
|--------|---------|
| `index_client(client)` | Index client documents |
| `index_all_clients(clients)` | Batch index |
| `search(query, n_results)` | Semantic search |
| `search_clients(query)` | Return matching client IDs |
| `get_relevant_context(query)` | Formatted context for LLM |

### AlertsService

**File:** `services/alerts_service.py`

| Method | Purpose |
|--------|---------|
| `generate_all_alerts(clients)` | Scan all clients |
| `get_alerts_by_type(type)` | Filter by type |
| `get_alerts_by_priority(priority)` | Filter by priority |
| `get_alert_summary(alerts)` | Stats summary |
| `generate_daily_briefing(alerts)` | Text briefing |

### ComplianceService

**File:** `services/compliance_service.py`

| Method | Purpose |
|--------|---------|
| `get_client_compliance_score(client)` | Individual score |
| `get_portfolio_compliance_summary(clients)` | All clients |
| `get_consumer_duty_report(clients)` | Full report |
| `log_value_delivered(client, desc)` | Record value |

---

## Configuration

### Environment Variables (.env)

```bash
# LLM API Keys
GROQ_API_KEY=your_groq_key_here      # Free at console.groq.com
OPENAI_API_KEY=your_openai_key_here  # Optional fallback

# Settings
LLM_PROVIDER=auto                     # auto, groq, openai, mock
```

### Config Settings (config.py)

```python
# LLM Models
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL = "gpt-4o-mini"

# Data Paths
DATA_DIR = Path(__file__).parent / "data"
CLIENTS_FILE = DATA_DIR / "clients.json"

# Vector Store
CHROMA_PERSIST_DIR = str(Path(__file__).parent / "chroma_db")
```

### Alert Thresholds (alerts_service.py)

```python
self.config = {
    "birthday_days_ahead": 14,
    "policy_renewal_days_ahead": 30,
    "policy_maturity_days_ahead": 60,
    "follow_up_warning_days": 3,
    "annual_review_warning_days": 30,
    "no_contact_days": 90,
    "risk_profile_stale_years": 1,
    "retirement_warning_years": 2,
}
```

---

## Demo Scenarios

### Scenario 1: Morning Briefing

1. Open Jarvis at http://localhost:8501
2. You're in 💬 Chat by default
3. Click **"🌅 Daily Briefing"** button
4. Jarvis shows prioritized tasks for today
5. Review overdue items and upcoming events

### Scenario 2: Client Preparation

1. Type client name in sidebar search
2. Click on matching client
3. View full profile: concerns, policies, notes
4. Ask in chat: *"What should I know about Mrs. Patterson before our call?"*
5. Get AI-powered briefing

### Scenario 3: Proactive Outreach

1. Navigate to **🚨 Alerts**
2. Filter by "Birthday" type
3. See clients with upcoming birthdays
4. Click **"📧 Draft Email"**
5. Review AI-generated birthday message
6. Copy and send

### Scenario 4: Compliance Check

1. Navigate to **🏛️ Compliance**
2. View portfolio-wide compliance rate
3. See common issues across clients
4. Click on at-risk clients
5. Generate downloadable Consumer Duty report

### Scenario 5: Finding Clients by Concern

1. Use semantic search in sidebar: *"worried about inheritance tax"*
2. See matching clients
3. Click to view their profiles
4. Draft check-in email addressing their concern

---

## Quick Reference Commands

```bash
# Start the application
python3 -m streamlit run app.py --server.port 8501

# Generate mock data
python3 data/mock_clients.py

# Run from project root
cd /Users/techadmin/Projects/hack_to_hire/jarvis
python3 -m streamlit run app.py --server.headless true --server.port 8501
```

---

## Author

**Gaurav Purohit**
- GitHub: [@Gauravpurohit409](https://github.com/Gauravpurohit409)
- Repository: [jarvis-advisor](https://github.com/Gauravpurohit409/jarvis-advisor)

---

*Built for AdvisoryAI Hack-to-Hire 2026*
