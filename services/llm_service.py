"""
LLM Service
Abstraction layer for LLM providers (Groq free tier / OpenAI fallback)
"""

import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# Import config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    LLM_PROVIDER, 
    GROQ_API_KEY, GROQ_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL
)


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


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM Provider (FREE tier)
    Get API key at: https://console.groq.com/keys
    """
    
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.client = None
        
        if self.is_available():
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Groq package not installed. Run: pip install groq")
            except TypeError as e:
                # Handle httpx/proxies compatibility issue
                print(f"Groq client init error (likely httpx version issue): {e}")
                self.client = None
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "your_groq_api_key_here")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        if not self.client:
            raise RuntimeError("Groq client not initialized")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle connection errors, API errors, etc.
            error_msg = str(e)
            if "APIConnectionError" in error_msg or "Connection error" in error_msg:
                raise RuntimeError(f"Groq API connection failed. Please check your internet connection.")
            raise RuntimeError(f"Groq API error: {error_msg}")


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM Provider (Paid, fallback)
    Get API key at: https://platform.openai.com/api-keys
    """
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        self.client = None
        
        if self.is_available():
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Run: pip install openai")
            except TypeError as e:
                # Handle httpx/proxies compatibility issue
                print(f"OpenAI client init error (likely httpx version issue): {e}")
                self.client = None
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "your_openai_api_key_here")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=2048
        )
        
        return response.choices[0].message.content


class MockProvider(BaseLLMProvider):
    """
    Mock LLM Provider for testing without API keys
    Returns template responses
    """
    
    def is_available(self) -> bool:
        return True
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break
        
        # Template responses based on keywords
        if "briefing" in user_message or "morning" in user_message or "today" in user_message:
            return """Good morning! Here's your daily briefing:

            📋 **Priority Actions:**
            • 3 clients have overdue annual reviews
            • 2 follow-up commitments are due this week
            • Mrs. Patterson's birthday is in 5 days (turning 65 - pension access milestone!)

            📞 **Clients to Contact:**
            • Mr. Singh - no contact in 95 days, has active concern about market volatility
            • Mrs. Chen - review due in 2 weeks, schedule meeting

            💡 **Opportunities:**
            • Mr. Thompson mentioned daughter's wedding - consider protection review
            • 2 clients approaching tax year end - ISA top-up reminder

            Would you like me to draft any emails or provide more details on any client?"""
        
        elif "client" in user_message or any(name in user_message for name in ["patterson", "singh", "chen", "thompson"]):
            return """Here's what I found about this client:

            **Overview:**
            • Long-standing client since 2018
            • Portfolio value: £287,000 across 3 pension schemes
            • Last contacted: 45 days ago via video call

            **Key Concerns (Active):**
            • Inheritance tax planning - raised 6 months ago, severity: High
            • Worried about market volatility affecting retirement plans

            **Upcoming:**
            • Annual review due in 3 weeks
            • Birthday next month (milestone: 65)

            **Recent Notes:**
            • Last meeting discussed pension consolidation options
            • Action item: Send comparison of transfer fees (pending)

            **Family:**
            • Spouse: Margaret
            • 2 adult children, 3 grandchildren
            • Mentioned daughter's wedding planned for summer

            Would you like me to draft a check-in email or schedule a review?"""
        
        elif "email" in user_message or "draft" in user_message:
            return """Here's a draft email:

            ---
            **Subject:** Checking in - thinking of you

            Dear Mrs. Patterson,

            I hope this email finds you well. I wanted to reach out as it's been a little while since we last spoke.

            I remember you mentioned some concerns about inheritance tax planning during our last conversation, and I wanted to let you know I've been researching some options that might be helpful for your situation.

            Also, I noticed your birthday is coming up next month - a significant milestone! This might be a good time to review your pension access options now that you're approaching 65.

            Would you have time for a brief call next week to catch up? I'm available Tuesday or Thursday afternoon if either works for you.

            Warm regards,
            [Advisor Name]

            ---

            Shall I adjust the tone or add anything specific?"""
        
        else:
            return """I'm here to help you stay proactive with your clients. I can:

            • **Daily Briefing** - Show priority actions, overdue reviews, upcoming events
            • **Client Lookup** - Get full context on any client quickly
            • **Draft Emails** - Birthday wishes, review reminders, check-ins
            • **Find Clients** - Search by concerns, last contact, upcoming events

            What would you like to know?"""


class LLMService:
    """
    Main LLM Service - automatically selects best available provider
    Priority: Groq (free) -> OpenAI (paid) -> Mock (testing)
    """
    
    def __init__(self, force_provider: Optional[str] = None):
        """
        Initialize LLM service
        
        Args:
            force_provider: Force specific provider ("groq", "openai", "mock")
        """
        self.provider: BaseLLMProvider
        self.provider_name: str
        
        if force_provider:
            self.provider, self.provider_name = self._get_provider(force_provider)
        else:
            self.provider, self.provider_name = self._auto_select_provider()
        
        print(f"LLM Service initialized with: {self.provider_name}")
    
    def _get_provider(self, name: str) -> tuple[BaseLLMProvider, str]:
        """Get specific provider by name"""
        providers = {
            "groq": (GroqProvider(), "Groq (Free)"),
            "openai": (OpenAIProvider(), "OpenAI"),
            "mock": (MockProvider(), "Mock (Testing)"),
        }
        return providers.get(name.lower(), (MockProvider(), "Mock (Testing)"))
    
    def _auto_select_provider(self) -> tuple[BaseLLMProvider, str]:
        """Auto-select best available provider"""
        # Try Groq first (free)
        groq = GroqProvider()
        if groq.is_available():
            return groq, "Groq (Free)"
        
        # Try OpenAI (paid fallback)
        openai = OpenAIProvider()
        if openai.is_available():
            return openai, "OpenAI"
        
        # Fall back to mock
        print("⚠️  No LLM API keys configured. Using mock responses.")
        print("   Get free Groq API key at: https://console.groq.com/keys")
        return MockProvider(), "Mock (Testing)"
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Jarvis"""
        return """You are Jarvis, a proactive AI assistant for UK Independent Financial Advisors (IFAs).

    Your role is to help advisors:
    1. Stay proactive instead of reactive
    2. Remember important client details (life events, concerns, commitments)
    3. Track compliance requirements (annual reviews, Consumer Duty)
    4. Surface the right information at the right time
    5. Draft personalized client communications
    6. Send emails and book calendar meetings directly (when Google is connected)

    Context you have access to:
    - Client profiles (demographics, family, occupation)
    - Meeting notes and conversation history
    - Active concerns and anxieties clients have expressed
    - Follow-up commitments the advisor has made
    - Policy and portfolio information
    - Compliance status (review dates, suitability)
    - Upcoming life events and milestones
    - Proactive alerts (urgent and upcoming deadlines)

    GOOGLE INTEGRATION - SCHEDULING MEETINGS:
    When the user asks to schedule/book a meeting, call, or appointment:
    - Simply confirm: "I'll schedule that for you. Please confirm the details in the form below."
    - Do NOT give lengthy instructions about how to book meetings
    - Do NOT mention "Book Meeting feature" or "Settings"
    - Do NOT list steps - the form appears automatically
    - Keep your response to 1-2 sentences max
    
    Example scheduling responses:
    - "Setting up a call with [name] for [date]. Please confirm below."
    - "Got it! Scheduling form is ready - just confirm the details."
    - "I'll book that meeting. Check the form below to confirm."

    EMAIL CAPABILITY:
    When the user asks to send an email, write an email, or draft an email:
    - IMMEDIATELY draft a complete email - do NOT ask for more information
    - Always include "Subject:" line at the very top
    - Keep emails warm, professional, and personalized
    - End the email properly with "Best regards," or "Warm regards,"
    - After your email draft, the send form will appear automatically
    - If recipient name is unknown, use "Dear Friend," or a generic greeting
    - Do NOT ask clarifying questions - just draft the email based on available info
    - Keep any explanation to 1 sentence before the email - just draft it
    
    Email format example:
    Subject: [Subject Line Here]
    
    Dear [Name],
    
    [Email body...]
    
    Best regards,
    [Advisor]

    Guidelines:
    - Be concise and actionable
    - Prioritize what's most urgent/important
    - Reference specific client details when relevant
    - Suggest proactive actions the advisor can take
    - Format responses clearly with bullets/sections
    - Use a professional but warm tone
    - When PROACTIVE ALERTS are provided in context, weave them naturally into your response
    - For urgent alerts (🔴), mention them prominently
    - For upcoming alerts (🟡), mention as "by the way" or "also worth noting"

    UK Financial Advice Context:
    - FCA Consumer Duty requires demonstrating ongoing value
    - Annual reviews must happen within 12 months
    - Milestone birthdays (55, 60, 65, 75) have pension significance
    - Tax year ends 5th April (ISA/pension deadlines)"""
    
    def chat(
        self, 
        user_message: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Send a chat message and get response
        
        Args:
            user_message: The user's message
            context: Optional context about clients/data to include
            conversation_history: Optional previous messages
            temperature: Response creativity (0-1)
        
        Returns:
            Assistant's response
        """
        messages = []
        
        # System prompt
        system_content = self.get_system_prompt()
        if context:
            system_content += f"\n\n--- CURRENT CONTEXT ---\n{context}"
        
        messages.append({"role": "system", "content": system_content})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response
        return self.provider.chat(messages, temperature)
    
    def generate_daily_briefing(self, briefing_data: Dict[str, Any]) -> str:
        """Generate daily briefing from structured data"""
        context = self._format_briefing_context(briefing_data)
        
        return self.chat(
            user_message="Generate my daily briefing. What should I focus on today?",
            context=context,
            temperature=0.5
        )
    
    def get_client_insights(self, client_summary: Dict[str, Any]) -> str:
        """Get insights about a specific client"""
        context = f"CLIENT DATA:\n{self._format_client_context(client_summary)}"
        
        return self.chat(
            user_message="Give me a quick briefing on this client. What should I know before contacting them?",
            context=context,
            temperature=0.5
        )
    
    def draft_email(
        self, 
        client_summary: Dict[str, Any], 
        email_type: str,
        additional_context: Optional[str] = None
    ) -> str:
        """Draft an email for a client"""
        context = f"CLIENT DATA:\n{self._format_client_context(client_summary)}"
        if additional_context:
            context += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"
        
        format_instructions = """

FORMAT REQUIREMENTS:
- Start directly with "Subject:" line (no markdown heading)
- Then a blank line
- Then "Dear [Name]," greeting
- Write 2-4 paragraphs of body text
- End with appropriate sign-off like "Kind regards," or "Best wishes,"
- Sign off with "[Advisor Name]" as placeholder (this email will be sent by the financial advisor, NOT by an AI)
- Do NOT use any markdown headings (no # symbols)
- Do NOT use bold or italic formatting
- Keep it as plain text email format
- Do NOT sign as "Jarvis" or any AI - this is a draft for the human advisor to send"""
        
        prompts = {
            "birthday": f"Draft a warm birthday email for this client. Make it personal by referencing what you know about them (family, interests, recent conversations).{format_instructions}",
            "review_reminder": f"Draft a professional email reminding this client their annual review is due. Emphasize the value of the review and what you'll cover.{format_instructions}",
            "check_in": f"Draft a friendly check-in email. Reference any concerns they've expressed or life events happening.{format_instructions}",
            "follow_up": f"Draft a follow-up email. Reference any commitments made or actions pending.{format_instructions}",
            "policy_renewal": f"Draft an email about their upcoming policy renewal. Explain the importance of reviewing their cover.{format_instructions}",
            "policy_maturity": f"Draft an email about their policy reaching maturity. Explain the options available to them.{format_instructions}",
            "retirement_planning": f"Draft an email about retirement planning. Reference their retirement timeline and any concerns.{format_instructions}",
            "general_update": f"Draft a general update email. Keep it friendly and reference recent conversations or their situation.{format_instructions}",
        }
        
        prompt = prompts.get(email_type, f"Draft a {email_type} email for this client.{format_instructions}")
        
        return self.chat(user_message=prompt, context=context, temperature=0.7)
    
    def _format_briefing_context(self, data: Dict[str, Any]) -> str:
        """Format briefing data for LLM context"""
        lines = [f"Total clients: {data.get('total_clients', 0)}"]
        
        if data.get('reviews_overdue'):
            lines.append(f"\nOVERDUE REVIEWS ({len(data['reviews_overdue'])}):")
            for c in data['reviews_overdue'][:5]:
                lines.append(f"  - {c.full_name}: review was due {c.compliance.next_review_due}")
        
        if data.get('dormant_90_days'):
            lines.append(f"\nDORMANT CLIENTS - NO CONTACT 90+ DAYS ({len(data['dormant_90_days'])}):")
            for c in data['dormant_90_days'][:5]:
                lines.append(f"  - {c.full_name}: {c.days_since_last_contact} days since contact")
        
        if data.get('upcoming_birthdays'):
            lines.append(f"\nUPCOMING BIRTHDAYS:")
            for b in data['upcoming_birthdays'][:5]:
                milestone = " (MILESTONE!)" if b['is_milestone'] else ""
                lines.append(f"  - {b['client'].full_name}: turning {b['turning_age']} in {b['days_until']} days{milestone}")
        
        if data.get('overdue_follow_ups'):
            lines.append(f"\nOVERDUE FOLLOW-UPS ({len(data['overdue_follow_ups'])}):")
            for c in data['overdue_follow_ups'][:5]:
                for f in c.overdue_follow_ups:
                    lines.append(f"  - {c.full_name}: {f.commitment} (was due {f.deadline})")
        
        if data.get('active_concerns'):
            lines.append(f"\nCLIENTS WITH ACTIVE CONCERNS ({len(data['active_concerns'])}):")
            for c in data['active_concerns'][:5]:
                concerns = ", ".join([con.topic for con in c.active_concerns])
                lines.append(f"  - {c.full_name}: {concerns}")
        
        return "\n".join(lines)
    
    def _format_client_context(self, summary: Dict[str, Any]) -> str:
        """Format client summary for LLM context"""
        import json
        return json.dumps(summary, indent=2, default=str)
