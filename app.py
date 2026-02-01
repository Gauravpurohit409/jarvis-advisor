"""
Jarvis - Proactive Financial Advisor Assistant
Main Streamlit Application
"""

import streamlit as st
from datetime import date, datetime
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


# ============== INITIALIZATION ==============

@st.cache_resource
def init_services():
    """Initialize services (cached)"""
    client_service = ClientService()
    llm_service = LLMService()
    vector_store = get_vector_store()
    
    # Index clients if vector store is empty
    if vector_store.is_available() and vector_store.collection.count() == 0:
        clients = client_service.get_all_clients()
        vector_store.index_all_clients(clients)
    
    return client_service, llm_service, vector_store


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_client" not in st.session_state:
        st.session_state.selected_client = None
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"
    if "client_filter" not in st.session_state:
        st.session_state.client_filter = None


# ============== UI COMPONENTS ==============

def render_sidebar(client_service: ClientService):
    """Render sidebar with navigation and client list"""
    with st.sidebar:
        st.title("🤖 Jarvis")
        st.caption("Proactive Advisor Assistant")
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        view = st.radio(
            "View",
            ["💬 Chat", "📊 Dashboard", "👥 Clients", "📧 Email Drafts"],
            label_visibility="collapsed"
        )
        
        st.session_state.current_view = {
            "💬 Chat": "chat",
            "📊 Dashboard": "dashboard", 
            "👥 Clients": "clients",
            "📧 Email Drafts": "emails"
        }.get(view, "chat")
        
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


def render_chat(client_service: ClientService, llm_service: LLMService, vector_store: VectorStoreService):
    """Render chat interface with semantic search"""
    st.header("💬 Chat with Jarvis")
    
    # Store LLM provider name
    st.session_state.llm_provider = llm_service.provider_name
    
    # Show vector store status
    if vector_store.is_available():
        st.caption(f"🧠 Semantic search active ({vector_store.collection.count()} documents indexed)")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🌅 Daily Briefing", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Give me my daily briefing. What should I focus on today?"
            })
    with col2:
        if st.button("⚠️ Overdue Reviews", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Which clients have overdue annual reviews?"
            })
    with col3:
        if st.button("📞 Who to Call", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Which clients should I call this week? Prioritize by urgency."
            })
    with col4:
        if st.button("🎂 Upcoming Birthdays", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Show me upcoming client birthdays in the next 30 days."
            })
    
    st.divider()
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask Jarvis anything about your clients..."):
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
                    
                    full_context = keyword_context
                    if semantic_context:
                        full_context += "\n\n" + semantic_context
                    
                    # Generate response
                    response = llm_service.chat(
                        user_message=prompt,
                        context=full_context,
                        conversation_history=st.session_state.messages[:-1][-6:]  # Last 6 messages for context
                    )
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = str(e)
                    if "connection" in error_msg.lower() or "api" in error_msg.lower():
                        st.error("⚠️ Connection error. Please check your internet connection and try again.")
                    else:
                        st.error(f"⚠️ Error: {error_msg}")
                    # Remove the pending user message from history
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()


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
                for followup in client.overdue_follow_ups:
                    with st.expander(f"{client.full_name}: {followup.commitment}"):
                        st.write(f"**Was due:** {followup.deadline}")
                        st.write(f"**Created:** {followup.created_date}")
                        if st.button("📧 Draft Follow-up", key=f"followup_{client.id}_{followup.commitment[:10]}"):
                            st.session_state.draft_for = client.id
                            st.session_state.draft_type = "follow_up"
                            st.session_state.current_view = "emails"
                            st.rerun()
        else:
            st.success("No overdue follow-ups! 🎉")


def render_clients(client_service: ClientService):
    """Render clients list view"""
    
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
    
    # Filters row
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search by name", "")
    with col2:
        filter_concern = st.selectbox("Filter by concern", 
            ["All", "retirement", "inheritance tax", "protection", "care home costs", "pension"])
    with col3:
        filter_status = st.selectbox("Filter by status",
            ["All", "Review Overdue", "Due in 30 Days", "Dormant (90+ days)", "Has Active Concerns", "Pending Follow-ups"])
    
    # Get clients based on filter
    if search:
        clients = client_service.search_by_name(search)
        st.session_state.client_filter = None  # Clear dashboard filter when searching
    elif filter_concern != "All":
        clients = client_service.search_by_concern(filter_concern)
        st.session_state.client_filter = None
    elif filter_status == "Review Overdue" or active_filter == "reviews_overdue":
        clients = client_service.get_clients_review_overdue()
    elif filter_status == "Due in 30 Days" or active_filter == "reviews_due_soon":
        briefing = client_service.get_daily_briefing_data()
        clients = briefing["reviews_due_soon"]
    elif filter_status == "Dormant (90+ days)" or active_filter == "dormant":
        clients = client_service.get_dormant_clients(90)
    elif filter_status == "Has Active Concerns":
        clients = client_service.get_clients_with_active_concerns()
    elif filter_status == "Pending Follow-ups" or active_filter == "pending_followups":
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
            
            # Recent meetings
            if client.meeting_notes:
                st.write("**Recent Meeting Notes:**")
                for note in client.meeting_notes[:2]:
                    st.caption(f"{note.meeting_date}: {note.summary}")


def render_emails(client_service: ClientService, llm_service: LLMService):
    """Render email drafting view"""
    st.header("📧 Email Drafts")
    
    # Check if we came from a button click
    draft_for = st.session_state.get("draft_for")
    draft_type = st.session_state.get("draft_type")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Create New Draft")
        
        # Client selection
        clients = client_service.get_all_clients()
        client_names = {f"{c.full_name} ({c.id})": c.id for c in clients}
        
        # Pre-select if coming from button
        default_index = 0
        if draft_for:
            for i, (name, cid) in enumerate(client_names.items()):
                if cid == draft_for:
                    default_index = i
                    break
        
        selected = st.selectbox("Select Client", list(client_names.keys()), index=default_index)
        selected_client_id = client_names[selected]
        
        # Email type
        email_types = {
            "Birthday Wishes": "birthday",
            "Review Reminder": "review_reminder", 
            "Check-in": "check_in",
            "Follow-up": "follow_up"
        }
        
        default_type = 0
        if draft_type:
            for i, (name, etype) in enumerate(email_types.items()):
                if etype == draft_type:
                    default_type = i
                    break
        
        selected_type = st.selectbox("Email Type", list(email_types.keys()), index=default_type)
        email_type = email_types[selected_type]
        
        additional_context = st.text_area("Additional context (optional)", 
            placeholder="Any specific points to include...")
        
        generate_btn = st.button("✨ Generate Draft", type="primary", use_container_width=True)
        
        # Clear the session state after using
        if "draft_for" in st.session_state:
            del st.session_state.draft_for
        if "draft_type" in st.session_state:
            del st.session_state.draft_type
    
    with col2:
        st.subheader("Email Preview")
        
        if generate_btn:
            with st.spinner("Drafting email..."):
                client_summary = client_service.get_client_summary(selected_client_id)
                
                email_draft = llm_service.draft_email(
                    client_summary=client_summary,
                    email_type=email_type,
                    additional_context=additional_context if additional_context else None
                )
                
                st.session_state.current_draft = email_draft
        
        if "current_draft" in st.session_state:
            st.markdown(st.session_state.current_draft)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📋 Copy to Clipboard"):
                    st.info("Draft copied! (Use Ctrl+C on the text)")
            with col_b:
                if st.button("🔄 Regenerate"):
                    if "current_draft" in st.session_state:
                        del st.session_state.current_draft
                    st.rerun()
        else:
            st.info("Select a client and email type, then click 'Generate Draft' to create an email.")


# ============== MAIN APP ==============

def main():
    """Main application entry point"""
    init_session_state()
    
    try:
        client_service, llm_service, vector_store = init_services()
        # Store vector_store in session state for sidebar access
        st.session_state.vector_store = vector_store
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        st.info("Make sure to run `python data/mock_generator.py` first to generate client data.")
        return
    
    render_sidebar(client_service)
    
    # Route to current view
    if st.session_state.current_view == "chat":
        render_chat(client_service, llm_service, vector_store)
    elif st.session_state.current_view == "dashboard":
        render_dashboard(client_service)
    elif st.session_state.current_view == "clients":
        render_clients(client_service)
    elif st.session_state.current_view == "emails":
        render_emails(client_service, llm_service)


if __name__ == "__main__":
    main()
