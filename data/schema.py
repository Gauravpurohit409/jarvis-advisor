"""
Client Data Schema
Pydantic models for UK Financial Advisor client data
Covers all aspects needed for proactive advisor assistance
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# ============== ENUMS ==============

class ContactMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    SMS = "sms"


class RiskAttitude(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PolicyType(str, Enum):
    PENSION = "pension"
    ISA = "isa"
    GIA = "gia"  # General Investment Account
    LIFE_INSURANCE = "life_insurance"
    CRITICAL_ILLNESS = "critical_illness"
    INCOME_PROTECTION = "income_protection"
    MORTGAGE = "mortgage"
    ANNUITY = "annuity"


class ConcernSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConcernStatus(str, Enum):
    ACTIVE = "active"
    ADDRESSED = "addressed"
    MONITORING = "monitoring"


class FollowUpStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class LifeEventType(str, Enum):
    BIRTHDAY = "birthday"
    WEDDING = "wedding"
    BIRTH = "birth"  # New child/grandchild
    RETIREMENT = "retirement"
    ANNIVERSARY = "anniversary"
    GRADUATION = "graduation"
    NEW_JOB = "new_job"
    HOUSE_PURCHASE = "house_purchase"
    DEATH_IN_FAMILY = "death_in_family"
    DIVORCE = "divorce"
    INHERITANCE = "inheritance"
    HEALTH_ISSUE = "health_issue"
    OTHER = "other"


# ============== SUB-MODELS ==============

class FamilyMember(BaseModel):
    """Family member details for life event tracking"""
    name: str
    relationship: str  # spouse, child, grandchild, parent, sibling
    date_of_birth: Optional[date] = None
    notes: Optional[str] = None


class LifeEvent(BaseModel):
    """Life events - past and upcoming"""
    event_type: LifeEventType
    event_date: date
    description: str
    related_person: Optional[str] = None  # Family member name if applicable
    source: str = "client_mentioned"  # How we learned about it
    created_at: datetime = Field(default_factory=datetime.now)


class Concern(BaseModel):
    """Client concerns and anxieties to track and revisit"""
    topic: str  # e.g., "market volatility", "inheritance tax", "running out of money"
    details: str
    severity: ConcernSeverity
    date_raised: date
    status: ConcernStatus = ConcernStatus.ACTIVE
    last_discussed: Optional[date] = None
    notes: Optional[str] = None


class Policy(BaseModel):
    """Financial products and policies"""
    policy_type: PolicyType
    provider: str
    policy_number: Optional[str] = None
    current_value: Optional[float] = None
    monthly_contribution: Optional[float] = None
    start_date: Optional[date] = None
    renewal_date: Optional[date] = None
    maturity_date: Optional[date] = None
    notes: Optional[str] = None


class RiskProfile(BaseModel):
    """Client risk assessment data"""
    attitude_to_risk: RiskAttitude
    capacity_for_loss: RiskAttitude
    investment_experience: str  # "none", "limited", "moderate", "extensive"
    time_horizon_years: int
    last_assessed: date
    notes: Optional[str] = None


class MeetingNote(BaseModel):
    """Notes and transcripts from client meetings"""
    meeting_date: date
    meeting_type: ContactMethod
    duration_minutes: Optional[int] = None
    summary: str
    transcript: Optional[str] = None  # Full transcript if available
    key_points: List[str] = []
    action_items: List[str] = []
    concerns_raised: List[str] = []
    life_events_mentioned: List[str] = []


class FollowUp(BaseModel):
    """Commitments and follow-up tasks"""
    commitment: str  # What was promised
    deadline: date
    status: FollowUpStatus = FollowUpStatus.PENDING
    created_date: date = Field(default_factory=date.today)
    completed_date: Optional[date] = None
    notes: Optional[str] = None


class Interaction(BaseModel):
    """Record of every advisor-client touchpoint"""
    interaction_date: datetime
    method: ContactMethod
    direction: str  # "inbound" or "outbound"
    summary: str
    duration_minutes: Optional[int] = None
    next_action: Optional[str] = None


class ComplianceRecord(BaseModel):
    """FCA Consumer Duty compliance tracking"""
    last_annual_review: Optional[date] = None
    next_review_due: Optional[date] = None
    review_status: str = "pending"  # "completed", "pending", "overdue"
    suitability_confirmed: bool = False
    suitability_date: Optional[date] = None
    value_delivered: List[str] = []  # Log of value demonstrated
    notes: Optional[str] = None


class Address(BaseModel):
    """UK address format"""
    line1: str
    line2: Optional[str] = None
    city: str
    county: Optional[str] = None
    postcode: str
    country: str = "United Kingdom"


class ContactInfo(BaseModel):
    """Client contact information"""
    email: str
    phone: str
    mobile: Optional[str] = None
    address: Address
    preferred_contact_method: ContactMethod = ContactMethod.EMAIL
    best_time_to_call: Optional[str] = None


# ============== MAIN CLIENT MODEL ==============

class Client(BaseModel):
    """
    Complete client profile for UK Financial Advisor
    Covers demographics, policies, concerns, life events, interactions, and compliance
    """
    # Identifiers
    id: str
    
    # Demographics
    title: str  # Mr, Mrs, Ms, Dr
    first_name: str
    last_name: str
    date_of_birth: date
    national_insurance: Optional[str] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[float] = None
    
    # Contact
    contact_info: ContactInfo
    
    # Family
    marital_status: str  # single, married, divorced, widowed, civil_partnership
    family_members: List[FamilyMember] = []
    
    # Life Events (past and upcoming)
    life_events: List[LifeEvent] = []
    
    # Concerns and Anxieties
    concerns: List[Concern] = []
    
    # Financial Products
    policies: List[Policy] = []
    total_portfolio_value: Optional[float] = None
    
    # Risk Profile
    risk_profile: Optional[RiskProfile] = None
    
    # Meeting History
    meeting_notes: List[MeetingNote] = []
    
    # Follow-up Commitments
    follow_ups: List[FollowUp] = []
    
    # Interaction History
    interactions: List[Interaction] = []
    
    # Compliance
    compliance: ComplianceRecord = Field(default_factory=ComplianceRecord)
    
    # Metadata
    client_since: date
    assigned_advisor: str = "default"
    tags: List[str] = []  # Custom tags for categorization
    notes: Optional[str] = None  # General notes
    
    # Computed helper properties
    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def days_since_last_contact(self) -> Optional[int]:
        if not self.interactions:
            return None
        last_interaction = max(self.interactions, key=lambda x: x.interaction_date)
        return (datetime.now() - last_interaction.interaction_date).days
    
    @property
    def has_overdue_review(self) -> bool:
        if not self.compliance.next_review_due:
            return False
        return date.today() > self.compliance.next_review_due
    
    @property
    def active_concerns(self) -> List[Concern]:
        return [c for c in self.concerns if c.status == ConcernStatus.ACTIVE]
    
    @property
    def pending_follow_ups(self) -> List[FollowUp]:
        return [f for f in self.follow_ups if f.status == FollowUpStatus.PENDING]
    
    @property
    def overdue_follow_ups(self) -> List[FollowUp]:
        today = date.today()
        return [
            f for f in self.follow_ups 
            if f.status == FollowUpStatus.PENDING and f.deadline < today
        ]


# ============== COLLECTION MODEL ==============

class ClientDatabase(BaseModel):
    """Container for all clients"""
    clients: List[Client]
    last_updated: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
