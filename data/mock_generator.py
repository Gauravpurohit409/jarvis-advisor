"""
Mock Data Generator for Jarvis
Generates realistic UK Financial Advisor client data
Run this script to regenerate clients.json
"""

from datetime import date, datetime, timedelta
from typing import List
import json
import random

from schema import (
    Client, ClientDatabase, ContactInfo, Address, FamilyMember,
    LifeEvent, Concern, Policy, RiskProfile, MeetingNote, 
    FollowUp, Interaction, ComplianceRecord,
    ContactMethod, RiskAttitude, PolicyType, ConcernSeverity,
    ConcernStatus, FollowUpStatus, LifeEventType
)


# ============== HELPER DATA ==============

UK_FIRST_NAMES_MALE = [
    "James", "William", "Oliver", "George", "Thomas", "Henry", "Charles",
    "David", "Richard", "Michael", "Robert", "John", "Peter", "Andrew"
]

UK_FIRST_NAMES_FEMALE = [
    "Margaret", "Elizabeth", "Susan", "Patricia", "Sarah", "Emma", "Charlotte",
    "Victoria", "Catherine", "Anne", "Helen", "Mary", "Jennifer", "Linda"
]

UK_SURNAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Wilson", "Taylor", "Clark", "Thompson", "White", "Harrison", "Patterson",
    "Mitchell", "Chen", "Singh", "Patel", "O'Brien", "Campbell", "Stewart"
]

UK_CITIES = [
    ("London", "Greater London", "SW1A 1AA"),
    ("Manchester", "Greater Manchester", "M1 1AE"),
    ("Birmingham", "West Midlands", "B1 1AA"),
    ("Leeds", "West Yorkshire", "LS1 1AA"),
    ("Bristol", "Avon", "BS1 1AA"),
    ("Edinburgh", "Midlothian", "EH1 1AA"),
    ("Liverpool", "Merseyside", "L1 1AA"),
    ("Oxford", "Oxfordshire", "OX1 1AA"),
    ("Cambridge", "Cambridgeshire", "CB1 1AA"),
    ("Bath", "Somerset", "BA1 1AA"),
]

OCCUPATIONS = [
    ("Doctor", "NHS Trust", 95000),
    ("Software Engineer", "Tech Solutions Ltd", 75000),
    ("Teacher", "Local Academy", 45000),
    ("Accountant", "Price & Partners", 65000),
    ("Solicitor", "Legal Associates", 85000),
    ("Business Owner", "Self-employed", 120000),
    ("Retired", None, 35000),
    ("Nurse", "NHS Trust", 38000),
    ("Civil Servant", "HMRC", 55000),
    ("Marketing Director", "Brand Agency Ltd", 80000),
]

PENSION_PROVIDERS = [
    "Aviva", "Scottish Widows", "Standard Life", "Legal & General",
    "Royal London", "Aegon", "Fidelity", "Hargreaves Lansdown"
]

CONCERN_TOPICS = [
    ("market volatility", "Worried about market fluctuations affecting pension value"),
    ("inheritance tax", "Concerned about IHT liability for children"),
    ("running out of money", "Anxiety about longevity and pension lasting"),
    ("care home costs", "Worried about funding potential care needs"),
    ("inflation", "Concerned about inflation eroding savings"),
    ("leaving enough for spouse", "Want to ensure spouse is provided for"),
    ("pension consolidation", "Unsure whether to consolidate old pensions"),
    ("drawdown vs annuity", "Uncertain about retirement income strategy"),
]


def random_date(start_year: int, end_year: int) -> date:
    """Generate random date between years"""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def random_past_date(days_back: int) -> date:
    """Generate random date within last N days"""
    return date.today() - timedelta(days=random.randint(1, days_back))


def random_future_date(days_ahead: int) -> date:
    """Generate random date within next N days"""
    return date.today() + timedelta(days=random.randint(1, days_ahead))


def generate_client_id(index: int) -> str:
    """Generate unique client ID"""
    return f"CLT-{2024000 + index:07d}"


# ============== CLIENT BUILDERS ==============

def build_address(city_data: tuple) -> Address:
    """Build a UK address"""
    city, county, postcode = city_data
    return Address(
        line1=f"{random.randint(1, 200)} {random.choice(['High Street', 'Church Road', 'Mill Lane', 'Park Avenue', 'Station Road'])}",
        city=city,
        county=county,
        postcode=postcode
    )


def build_contact_info(first_name: str, last_name: str) -> ContactInfo:
    """Build contact information"""
    city_data = random.choice(UK_CITIES)
    email_domain = random.choice(["gmail.com", "outlook.com", "btinternet.com", "yahoo.co.uk"])
    
    return ContactInfo(
        email=f"{first_name.lower()}.{last_name.lower()}@{email_domain}",
        phone=f"0{random.randint(1, 2)}{random.randint(100, 999)} {random.randint(100000, 999999)}",
        mobile=f"07{random.randint(100, 999)} {random.randint(100000, 999999)}",
        address=build_address(city_data),
        preferred_contact_method=random.choice([ContactMethod.EMAIL, ContactMethod.PHONE]),
        best_time_to_call=random.choice(["Morning", "Afternoon", "Evening", None])
    )


def build_family_members(marital_status: str, client_age: int) -> List[FamilyMember]:
    """Build family members based on client profile"""
    members = []
    
    # Spouse
    if marital_status in ["married", "civil_partnership"]:
        spouse_name = random.choice(UK_FIRST_NAMES_FEMALE if random.random() > 0.5 else UK_FIRST_NAMES_MALE)
        members.append(FamilyMember(
            name=spouse_name,
            relationship="spouse",
            date_of_birth=random_date(date.today().year - client_age - 5, date.today().year - client_age + 5),
            notes=None
        ))
    
    # Children (if age appropriate)
    if client_age > 35:
        num_children = random.choice([0, 0, 1, 1, 2, 2, 3])
        for i in range(num_children):
            child_age = random.randint(5, min(35, client_age - 25))
            child_name = random.choice(UK_FIRST_NAMES_MALE + UK_FIRST_NAMES_FEMALE)
            members.append(FamilyMember(
                name=child_name,
                relationship="child",
                date_of_birth=random_date(date.today().year - child_age - 1, date.today().year - child_age),
                notes=random.choice([None, "Lives locally", "Lives abroad", None])
            ))
    
    # Grandchildren (if age appropriate)
    if client_age > 55 and random.random() > 0.5:
        num_grandchildren = random.randint(0, 4)
        for i in range(num_grandchildren):
            gc_name = random.choice(UK_FIRST_NAMES_MALE + UK_FIRST_NAMES_FEMALE)
            members.append(FamilyMember(
                name=gc_name,
                relationship="grandchild",
                date_of_birth=random_date(date.today().year - 15, date.today().year - 1),
                notes=None
            ))
    
    return members


def build_policies(client_age: int, income: float) -> List[Policy]:
    """Build realistic policy portfolio"""
    policies = []
    
    # Most clients have at least one pension
    if random.random() > 0.1:
        num_pensions = random.randint(1, 4)
        for i in range(num_pensions):
            policies.append(Policy(
                policy_type=PolicyType.PENSION,
                provider=random.choice(PENSION_PROVIDERS),
                policy_number=f"PEN{random.randint(100000, 999999)}",
                current_value=random.randint(20000, 500000),
                monthly_contribution=random.randint(0, 1000) if client_age < 65 else 0,
                start_date=random_date(2000, 2020),
                notes=random.choice([None, "Old employer scheme", "Personal pension", "SIPP"])
            ))
    
    # ISA
    if random.random() > 0.3:
        policies.append(Policy(
            policy_type=PolicyType.ISA,
            provider=random.choice(["Hargreaves Lansdown", "Vanguard", "AJ Bell", "Fidelity"]),
            policy_number=f"ISA{random.randint(100000, 999999)}",
            current_value=random.randint(10000, 200000),
            monthly_contribution=random.randint(100, 500),
            start_date=random_date(2015, 2023)
        ))
    
    # Life insurance
    if random.random() > 0.4 and client_age < 70:
        policies.append(Policy(
            policy_type=PolicyType.LIFE_INSURANCE,
            provider=random.choice(["Aviva", "Legal & General", "Zurich", "AIG"]),
            policy_number=f"LIF{random.randint(100000, 999999)}",
            current_value=random.randint(100000, 500000),
            renewal_date=random_future_date(365),
            notes="Level term"
        ))
    
    return policies


def build_concerns(client_age: int) -> List[Concern]:
    """Build realistic client concerns"""
    concerns = []
    num_concerns = random.randint(0, 3)
    
    selected_concerns = random.sample(CONCERN_TOPICS, min(num_concerns, len(CONCERN_TOPICS)))
    
    for topic, details in selected_concerns:
        concerns.append(Concern(
            topic=topic,
            details=details,
            severity=random.choice([ConcernSeverity.LOW, ConcernSeverity.MEDIUM, ConcernSeverity.HIGH]),
            date_raised=random_past_date(365),
            status=random.choice([ConcernStatus.ACTIVE, ConcernStatus.ACTIVE, ConcernStatus.MONITORING]),
            last_discussed=random_past_date(180) if random.random() > 0.3 else None
        ))
    
    return concerns


def build_life_events(family_members: List[FamilyMember], client_age: int) -> List[LifeEvent]:
    """Build life events - past and upcoming"""
    events = []
    
    # Upcoming birthday for family members
    for member in family_members:
        if member.date_of_birth and random.random() > 0.7:
            next_birthday = member.date_of_birth.replace(year=date.today().year)
            if next_birthday < date.today():
                next_birthday = next_birthday.replace(year=date.today().year + 1)
            
            if (next_birthday - date.today()).days < 60:
                events.append(LifeEvent(
                    event_type=LifeEventType.BIRTHDAY,
                    event_date=next_birthday,
                    description=f"{member.name}'s birthday coming up",
                    related_person=member.name,
                    source="client_mentioned"
                ))
    
    # Random upcoming events
    if random.random() > 0.6:
        event_type = random.choice([
            (LifeEventType.WEDDING, "Daughter's wedding"),
            (LifeEventType.RETIREMENT, "Retirement party planned"),
            (LifeEventType.GRADUATION, "Grandchild's graduation"),
            (LifeEventType.ANNIVERSARY, "Wedding anniversary"),
        ])
        events.append(LifeEvent(
            event_type=event_type[0],
            event_date=random_future_date(180),
            description=event_type[1],
            source="mentioned_in_meeting"
        ))
    
    # Past events
    if random.random() > 0.5:
        past_event = random.choice([
            (LifeEventType.BIRTH, "New grandchild born"),
            (LifeEventType.HOUSE_PURCHASE, "Helped child with house deposit"),
            (LifeEventType.NEW_JOB, "Started new position"),
        ])
        events.append(LifeEvent(
            event_type=past_event[0],
            event_date=random_past_date(365),
            description=past_event[1],
            source="client_mentioned"
        ))
    
    return events


def build_meeting_notes(client_name: str, concerns: List[Concern]) -> List[MeetingNote]:
    """Build realistic meeting notes history"""
    notes = []
    num_meetings = random.randint(1, 5)
    
    meeting_summaries = [
        f"Annual review with {client_name}. Discussed portfolio performance and rebalancing options.",
        f"Pension consolidation discussion with {client_name}. Reviewed old workplace schemes.",
        f"Retirement planning session. Discussed target retirement date and income requirements.",
        f"Protection review. Assessed current life cover and critical illness needs.",
        f"Ad-hoc call regarding market conditions. Provided reassurance about long-term strategy.",
        f"Initial fact-find meeting. Gathered information about financial goals and circumstances.",
    ]
    
    for i in range(num_meetings):
        meeting_date = random_past_date(400)
        summary = random.choice(meeting_summaries)
        
        key_points = [
            random.choice([
                "Client happy with current strategy",
                "Needs to update beneficiary details",
                "Considering increasing pension contributions",
                "Interested in sustainable investments",
                "Wants to review protection needs",
            ])
        ]
        
        action_items = []
        if random.random() > 0.5:
            action_items.append(random.choice([
                "Send pension projection",
                "Provide comparison of consolidation options",
                "Follow up on risk questionnaire",
                "Arrange meeting with spouse",
            ]))
        
        notes.append(MeetingNote(
            meeting_date=meeting_date,
            meeting_type=random.choice([ContactMethod.VIDEO_CALL, ContactMethod.IN_PERSON, ContactMethod.PHONE]),
            duration_minutes=random.choice([30, 45, 60, 90]),
            summary=summary,
            key_points=key_points,
            action_items=action_items,
            concerns_raised=[c.topic for c in concerns[:1]] if concerns and random.random() > 0.5 else []
        ))
    
    return sorted(notes, key=lambda x: x.meeting_date, reverse=True)


def build_follow_ups() -> List[FollowUp]:
    """Build follow-up commitments"""
    follow_ups = []
    
    if random.random() > 0.4:
        num_follow_ups = random.randint(1, 3)
        
        commitments = [
            ("Send pension transfer analysis", 14),
            ("Provide ISA top-up options", 7),
            ("Follow up on signed LOA", 21),
            ("Send annual review summary", 10),
            ("Provide protection quote comparison", 14),
            ("Arrange call to discuss inheritance planning", 30),
        ]
        
        for commitment, days in random.sample(commitments, min(num_follow_ups, len(commitments))):
            deadline = date.today() + timedelta(days=random.randint(-10, days))
            status = FollowUpStatus.PENDING
            
            if deadline < date.today():
                status = random.choice([FollowUpStatus.OVERDUE, FollowUpStatus.COMPLETED])
            
            follow_ups.append(FollowUp(
                commitment=commitment,
                deadline=deadline,
                status=status,
                created_date=deadline - timedelta(days=random.randint(7, 30)),
                completed_date=deadline if status == FollowUpStatus.COMPLETED else None
            ))
    
    return follow_ups


def build_interactions() -> List[Interaction]:
    """Build interaction history"""
    interactions = []
    num_interactions = random.randint(2, 8)
    
    for i in range(num_interactions):
        interaction_date = datetime.combine(
            random_past_date(400),
            datetime.min.time()
        ) + timedelta(hours=random.randint(9, 17))
        
        method = random.choice([ContactMethod.EMAIL, ContactMethod.PHONE, ContactMethod.VIDEO_CALL])
        direction = random.choice(["inbound", "outbound"])
        
        summaries = {
            ContactMethod.EMAIL: [
                "Sent portfolio valuation update",
                "Responded to query about pension statement",
                "Sent meeting confirmation",
                "Client requested callback",
            ],
            ContactMethod.PHONE: [
                "Discussed market conditions",
                "Answered questions about pension options",
                "Arranged follow-up meeting",
                "Quick catch-up call",
            ],
            ContactMethod.VIDEO_CALL: [
                "Annual review meeting",
                "Retirement planning discussion",
                "Portfolio review session",
            ],
        }
        
        interactions.append(Interaction(
            interaction_date=interaction_date,
            method=method,
            direction=direction,
            summary=random.choice(summaries.get(method, ["General interaction"])),
            duration_minutes=random.randint(5, 60) if method != ContactMethod.EMAIL else None,
            next_action=random.choice([None, None, "Follow up next week", "Send information"])
        ))
    
    return sorted(interactions, key=lambda x: x.interaction_date, reverse=True)


def build_compliance(last_interaction_date: datetime) -> ComplianceRecord:
    """Build compliance record"""
    last_review = random_past_date(400) if random.random() > 0.2 else None
    
    if last_review:
        next_review = last_review + timedelta(days=365)
        if next_review < date.today():
            status = "overdue"
        elif (next_review - date.today()).days < 30:
            status = "due_soon"
        else:
            status = "completed"
    else:
        next_review = date.today() + timedelta(days=random.randint(-60, 180))
        status = "overdue" if next_review < date.today() else "pending"
    
    return ComplianceRecord(
        last_annual_review=last_review,
        next_review_due=next_review,
        review_status=status,
        suitability_confirmed=random.random() > 0.3,
        suitability_date=last_review,
        value_delivered=[
            random.choice([
                "Consolidated 3 pensions saving £450/year in fees",
                "Optimised tax efficiency of withdrawals",
                "Reviewed and updated protection cover",
                "Rebalanced portfolio to match risk profile",
            ])
        ] if random.random() > 0.4 else []
    )


# ============== MAIN GENERATOR ==============

def generate_client(index: int) -> Client:
    """Generate a single realistic client"""
    
    # Basic demographics
    is_male = random.random() > 0.5
    first_name = random.choice(UK_FIRST_NAMES_MALE if is_male else UK_FIRST_NAMES_FEMALE)
    last_name = random.choice(UK_SURNAMES)
    title = random.choice(["Mr"] if is_male else ["Mrs", "Ms", "Dr"])
    
    # Age distribution weighted towards pre-retirees and retirees (IFA typical clients)
    age = random.choices(
        [random.randint(30, 40), random.randint(45, 55), random.randint(55, 65), random.randint(65, 80)],
        weights=[0.1, 0.25, 0.35, 0.3]
    )[0]
    dob = date.today() - timedelta(days=age * 365 + random.randint(0, 364))
    
    # Occupation and income
    occupation_data = random.choice(OCCUPATIONS)
    if age >= 65 and random.random() > 0.3:
        occupation_data = ("Retired", None, random.randint(25000, 60000))
    
    occupation, employer, income = occupation_data
    
    # Marital status
    marital_status = random.choices(
        ["married", "single", "divorced", "widowed"],
        weights=[0.6, 0.15, 0.15, 0.1]
    )[0]
    
    # Build sub-components
    contact_info = build_contact_info(first_name, last_name)
    family_members = build_family_members(marital_status, age)
    policies = build_policies(age, income)
    concerns = build_concerns(age)
    life_events = build_life_events(family_members, age)
    meeting_notes = build_meeting_notes(f"{title} {last_name}", concerns)
    follow_ups = build_follow_ups()
    interactions = build_interactions()
    
    # Risk profile
    risk_profile = RiskProfile(
        attitude_to_risk=random.choice(list(RiskAttitude)),
        capacity_for_loss=random.choice(list(RiskAttitude)),
        investment_experience=random.choice(["none", "limited", "moderate", "extensive"]),
        time_horizon_years=random.randint(5, 30),
        last_assessed=random_past_date(365)
    )
    
    # Calculate portfolio value
    total_value = sum(p.current_value or 0 for p in policies)
    
    # Compliance
    last_interaction = interactions[0].interaction_date if interactions else datetime.now()
    compliance = build_compliance(last_interaction)
    
    return Client(
        id=generate_client_id(index),
        title=title,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=dob,
        occupation=occupation,
        employer=employer,
        annual_income=income,
        contact_info=contact_info,
        marital_status=marital_status,
        family_members=family_members,
        life_events=life_events,
        concerns=concerns,
        policies=policies,
        total_portfolio_value=total_value,
        risk_profile=risk_profile,
        meeting_notes=meeting_notes,
        follow_ups=follow_ups,
        interactions=interactions,
        compliance=compliance,
        client_since=random_date(2015, 2024),
        tags=random.sample(["high-value", "retiree", "pre-retiree", "protection-focus", "pension-focus", "regular-saver"], 
                          k=random.randint(0, 2))
    )


def generate_all_clients(num_clients: int = 20) -> ClientDatabase:
    """Generate full client database"""
    print(f"Generating {num_clients} mock clients...")
    
    clients = []
    for i in range(num_clients):
        client = generate_client(i + 1)
        clients.append(client)
        print(f"  Created: {client.full_name} (Age {client.age}, {len(client.policies)} policies)")
    
    return ClientDatabase(
        clients=clients,
        last_updated=datetime.now(),
        version="1.0.0"
    )


def save_to_json(db: ClientDatabase, filepath: str = "clients.json"):
    """Save client database to JSON"""
    with open(filepath, "w") as f:
        json.dump(db.model_dump(mode="json"), f, indent=2, default=str)
    print(f"\nSaved {len(db.clients)} clients to {filepath}")


if __name__ == "__main__":
    # Set seed for reproducibility during development
    random.seed(42)
    
    # Generate clients
    client_db = generate_all_clients(20)
    
    # Save to JSON
    save_to_json(client_db)
    
    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total clients: {len(client_db.clients)}")
    print(f"Clients with overdue reviews: {sum(1 for c in client_db.clients if c.has_overdue_review)}")
    print(f"Clients with active concerns: {sum(1 for c in client_db.clients if c.active_concerns)}")
    print(f"Clients with pending follow-ups: {sum(1 for c in client_db.clients if c.pending_follow_ups)}")
