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
from services.alerts_service import AlertsService, alerts_service
from services.compliance_service import ComplianceService, compliance_service, ComplianceStatus
from data.schema import AlertPriority, AlertType


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
        st.session_state.current_view = "dashboard"
    if "client_filter" not in st.session_state:
        st.session_state.client_filter = None


# ============== UI COMPONENTS ==============

def render_sidebar(client_service: ClientService):
    """Render sidebar with navigation and client list"""
    with st.sidebar:
        st.title("🤖 Jarvis")
        st.caption("Proactive Advisor Assistant")
        
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


def render_alerts(client_service: ClientService, llm_service: LLMService):
    """Render proactive alerts view - the heart of Jarvis"""
    st.header("🚨 Proactive Alerts")
    st.caption("Jarvis has scanned all your clients and found these items needing attention")
    
    # Generate all alerts
    clients = client_service.get_all_clients()
    all_alerts = alerts_service.generate_all_alerts(clients)
    summary = alerts_service.get_alert_summary(all_alerts)
    
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
    filtered_alerts = all_alerts
    
    if priority_filter != "All":
        priority_map = {"Urgent": AlertPriority.URGENT, "High": AlertPriority.HIGH, 
                       "Medium": AlertPriority.MEDIUM, "Low": AlertPriority.LOW}
        filtered_alerts = [a for a in filtered_alerts if a.priority == priority_map.get(priority_filter)]
    
    if type_filter != "All":
        type_value = type_filter.lower().replace(" ", "_")
        filtered_alerts = [a for a in filtered_alerts if a.alert_type.value == type_value]
    
    if not show_dismissed:
        filtered_alerts = [a for a in filtered_alerts if not a.is_dismissed]
    
    st.caption(f"Showing {len(filtered_alerts)} of {len(all_alerts)} alerts")
    
    # Daily briefing button
    if st.button("📋 Generate Daily Briefing", use_container_width=True):
        with st.spinner("Generating AI briefing..."):
            briefing_text = alerts_service.generate_daily_briefing(all_alerts)
            
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
            # Get priority color
            color = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(alert.priority.value, "⚪")
            
            with st.expander(f"{alert.title} | {alert.client_name}", expanded=(priority == AlertPriority.URGENT)):
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
                    
                    if st.button("✓ Dismiss", key=f"alert_dismiss_{alert.id}", use_container_width=True):
                        # In production, this would persist
                        st.toast(f"Alert dismissed: {alert.title}")
        
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
            
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Client ID *", value=auto_id, key="manual_id")
                new_title = st.selectbox("Title *", ["Mr", "Mrs", "Ms", "Dr", "Miss"], key="manual_title")
                new_first = st.text_input("First Name *", placeholder="John", key="manual_first")
                new_last = st.text_input("Last Name *", placeholder="Smith", key="manual_last")
                new_dob = st.date_input("Date of Birth *", value=None, key="manual_dob")
                new_occupation = st.text_input("Occupation", placeholder="Accountant", key="manual_occupation")
            
            with col2:
                new_email = st.text_input("Email *", placeholder="john.smith@email.com", key="manual_email")
                new_phone = st.text_input("Phone *", placeholder="07700 900123", key="manual_phone")
                new_address_line1 = st.text_input("Address Line 1 *", placeholder="123 High Street", key="manual_address")
                new_city = st.text_input("City *", placeholder="London", key="manual_city")
                new_postcode = st.text_input("Postcode *", placeholder="SW1A 1AA", key="manual_postcode")
                new_marital = st.selectbox("Marital Status", ["single", "married", "divorced", "widowed", "civil_partnership"], key="manual_marital")
            
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
    
    # Filters row
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
                for followup in client.pending_follow_ups:
                    fu_col1, fu_col2 = st.columns([3, 1])
                    with fu_col1:
                        overdue = "🔴 OVERDUE" if followup.deadline < date.today() else ""
                        st.write(f"• {followup.commitment} (Due: {followup.deadline}) {overdue}")
                    with fu_col2:
                        if st.button("✅ Done", key=f"complete_fu_{client.id}_{followup.commitment[:10]}", use_container_width=True):
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


if __name__ == "__main__":
    main()
