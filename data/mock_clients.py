"""
Mock Client Data Generator for Jarvis
Generates realistic UK financial advisor client data for testing and demo purposes.
Ensures proper distribution of all scenarios: dormant clients, overdue reviews,
upcoming birthdays, anniversaries, follow-ups, etc.

Usage:
    cd jarvis/data
    python mock_clients.py
"""

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# ============== CONFIGURATION ==============

NUM_CLIENTS = 100  # Number of clients to generate
TODAY = date(2026, 2, 7)  # Current date for the simulation

# Distribution settings for realistic data
DORMANT_PERCENTAGE = 0.15  # 15% dormant (no contact 90+ days)
REVIEW_OVERDUE_PERCENTAGE = 0.20  # 20% have overdue reviews
REVIEW_DUE_SOON_COUNT = 12  # Reviews due in next 30 days
BIRTHDAY_SOON_COUNT = 8  # Clients with birthdays in next 14 days
ANNIVERSARY_SOON_COUNT = 6  # Clients with anniversaries in next 30 days
FOLLOW_UP_OVERDUE_PERCENTAGE = 0.12  # 12% have overdue follow-ups
FOLLOW_UP_DUE_SOON_COUNT = 15  # Follow-ups due in next 30 days
POLICY_RENEWAL_SOON_COUNT = 10  # Policies renewing in next 60 days

# ============== REFERENCE DATA ==============

UK_FIRST_NAMES_MALE = [
    "James", "Oliver", "William", "George", "Harry", "Jack", "Charlie", "Thomas",
    "Oscar", "Henry", "Arthur", "Leo", "Noah", "Muhammad", "Alfie", "Jacob",
    "Ethan", "Edward", "Alexander", "Joseph", "Samuel", "Daniel", "Max", "David",
    "Benjamin", "Lucas", "Archie", "Isaac", "Sebastian", "Adam", "Ryan", "Matthew",
    "Robert", "Michael", "Christopher", "Andrew", "Jonathan", "Richard", "Peter", "Paul",
    "Simon", "Stephen", "Mark", "Alan", "Kevin", "Brian", "Philip", "Anthony", "Graham", "Neil"
]

UK_FIRST_NAMES_FEMALE = [
    "Olivia", "Emma", "Charlotte", "Amelia", "Sophia", "Isabella", "Mia", "Ava",
    "Emily", "Grace", "Freya", "Florence", "Ella", "Lily", "Evie", "Ivy",
    "Poppy", "Rosie", "Sophie", "Alice", "Daisy", "Isabelle", "Sienna", "Harper",
    "Jessica", "Sarah", "Hannah", "Lucy", "Rebecca", "Lauren", "Victoria", "Elizabeth",
    "Catherine", "Margaret", "Patricia", "Jennifer", "Linda", "Barbara", "Susan", "Karen",
    "Nancy", "Helen", "Sandra", "Dorothy", "Deborah", "Carol", "Ruth", "Sharon", "Michelle", "Laura"
]

UK_LAST_NAMES = [
    "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans", "Wilson",
    "Thomas", "Johnson", "Roberts", "Robinson", "Thompson", "Wright", "Walker", "White",
    "Edwards", "Hughes", "Green", "Hall", "Lewis", "Harris", "Clarke", "Patel",
    "Jackson", "Wood", "Turner", "Martin", "Cooper", "Hill", "Ward", "Morris",
    "Moore", "Clark", "Lee", "King", "Baker", "Harrison", "Morgan", "Allen",
    "James", "Scott", "Ellis", "Bennett", "Gray", "Cox", "Russell", "Watson", "Palmer", "Lloyd",
    "Mitchell", "Simpson", "Murray", "Graham", "Stewart", "Kennedy", "Foster", "Reynolds",
    "Hamilton", "Marshall", "Collins", "Bell", "Murphy", "Bailey", "Hunt", "Richardson",
    "Fisher", "Andrews", "Carter", "Price", "Shaw", "Mason", "Gordon", "Hudson",
    "Spencer", "Knight", "Webb", "Grant", "Ferguson", "Pearson", "Stephens", "Stone"
]

UK_CITIES = [
    ("London", "Greater London", "SW1A"),
    ("London", "Greater London", "W1"),
    ("London", "Greater London", "EC2"),
    ("London", "Greater London", "NW3"),
    ("Manchester", "Greater Manchester", "M1"),
    ("Manchester", "Greater Manchester", "M20"),
    ("Birmingham", "West Midlands", "B1"),
    ("Birmingham", "West Midlands", "B15"),
    ("Leeds", "West Yorkshire", "LS1"),
    ("Leeds", "West Yorkshire", "LS8"),
    ("Liverpool", "Merseyside", "L1"),
    ("Bristol", "Somerset", "BS1"),
    ("Bristol", "Somerset", "BS8"),
    ("Sheffield", "South Yorkshire", "S1"),
    ("Newcastle upon Tyne", "Tyne and Wear", "NE1"),
    ("Nottingham", "Nottinghamshire", "NG1"),
    ("Southampton", "Hampshire", "SO14"),
    ("Brighton", "East Sussex", "BN1"),
    ("Brighton", "East Sussex", "BN2"),
    ("Cambridge", "Cambridgeshire", "CB1"),
    ("Cambridge", "Cambridgeshire", "CB2"),
    ("Oxford", "Oxfordshire", "OX1"),
    ("Oxford", "Oxfordshire", "OX2"),
    ("Reading", "Berkshire", "RG1"),
    ("Reading", "Berkshire", "RG4"),
    ("Edinburgh", "Scotland", "EH1"),
    ("Edinburgh", "Scotland", "EH4"),
    ("Glasgow", "Scotland", "G1"),
    ("Glasgow", "Scotland", "G12"),
    ("Cardiff", "Wales", "CF10"),
    ("Belfast", "Northern Ireland", "BT1"),
    ("Guildford", "Surrey", "GU1"),
    ("Guildford", "Surrey", "GU2"),
    ("Weybridge", "Surrey", "KT13"),
    ("Windsor", "Berkshire", "SL4"),
    ("Bath", "Somerset", "BA1"),
    ("Bath", "Somerset", "BA2"),
    ("York", "North Yorkshire", "YO1"),
    ("Cheltenham", "Gloucestershire", "GL50"),
    ("Cheltenham", "Gloucestershire", "GL51"),
    ("Harrogate", "North Yorkshire", "HG1"),
    ("Richmond", "Surrey", "TW9"),
    ("Richmond", "Surrey", "TW10"),
    ("St Albans", "Hertfordshire", "AL1"),
    ("St Albans", "Hertfordshire", "AL3"),
    ("Tunbridge Wells", "Kent", "TN1"),
    ("Chichester", "West Sussex", "PO19"),
    ("Winchester", "Hampshire", "SO23"),
    ("Sevenoaks", "Kent", "TN13"),
    ("Henley-on-Thames", "Oxfordshire", "RG9")
]

STREET_NAMES = [
    "High Street", "Church Lane", "Mill Road", "Station Road", "Park Avenue",
    "Victoria Road", "Green Lane", "Manor Way", "Oak Drive", "Cedar Close",
    "Willow Crescent", "Meadow Lane", "Kings Road", "Queens Avenue", "Albert Street",
    "George Street", "New Road", "London Road", "Hill View", "The Grove",
    "Chapel Lane", "School Road", "Farm Close", "Brook Street", "Garden Way",
    "Orchard Road", "Elm Avenue", "Ash Close", "Beech Drive", "Pine Road",
    "Maple Grove", "Birch Lane", "Hawthorn Close", "Cherry Tree Lane", "Chestnut Avenue",
    "Riverside Walk", "The Crescent", "Woodland Drive", "Lakeside View", "Hillcrest Road"
]

OCCUPATIONS = [
    ("Software Engineer", "Technology", 45000, 120000),
    ("Senior Software Developer", "Technology", 60000, 140000),
    ("Data Scientist", "Technology", 55000, 130000),
    ("Doctor", "Healthcare", 60000, 150000),
    ("GP Partner", "Healthcare", 80000, 150000),
    ("Consultant Surgeon", "Healthcare", 100000, 200000),
    ("Dentist", "Healthcare", 50000, 130000),
    ("Pharmacist", "Healthcare", 35000, 55000),
    ("Nurse Manager", "Healthcare", 40000, 60000),
    ("Solicitor", "Legal", 50000, 180000),
    ("Partner (Law)", "Legal", 100000, 300000),
    ("Barrister", "Legal", 60000, 250000),
    ("Accountant", "Finance", 35000, 95000),
    ("Chartered Accountant", "Finance", 50000, 120000),
    ("Financial Analyst", "Finance", 50000, 130000),
    ("Investment Manager", "Finance", 70000, 200000),
    ("Fund Manager", "Finance", 80000, 250000),
    ("Teacher", "Education", 28000, 55000),
    ("Head Teacher", "Education", 60000, 120000),
    ("University Lecturer", "Education", 40000, 75000),
    ("Professor", "Education", 70000, 130000),
    ("Marketing Manager", "Marketing", 40000, 85000),
    ("Marketing Director", "Marketing", 70000, 140000),
    ("Architect", "Construction", 35000, 90000),
    ("Senior Architect", "Construction", 55000, 120000),
    ("Civil Engineer", "Engineering", 35000, 80000),
    ("Chartered Engineer", "Engineering", 50000, 100000),
    ("Consultant", "Consulting", 55000, 150000),
    ("Management Consultant", "Consulting", 60000, 180000),
    ("Project Manager", "Management", 45000, 95000),
    ("Programme Director", "Management", 80000, 150000),
    ("HR Director", "Human Resources", 55000, 110000),
    ("Sales Director", "Sales", 60000, 140000),
    ("Business Owner", "Business", 40000, 200000),
    ("Company Director", "Business", 80000, 300000),
    ("Entrepreneur", "Business", 50000, 250000),
    ("Journalist", "Media", 30000, 70000),
    ("TV Producer", "Media", 45000, 100000),
    ("Police Inspector", "Public Sector", 50000, 70000),
    ("Civil Servant (Senior)", "Public Sector", 50000, 90000),
    ("Pilot", "Aviation", 65000, 150000),
    ("Retired", None, 20000, 60000),
    ("Retired (Professional)", None, 30000, 80000)
]

EMPLOYERS = [
    # Banks
    "Barclays", "HSBC", "Lloyds Banking Group", "NatWest Group", "Santander UK",
    "Metro Bank", "Virgin Money", "TSB", "Nationwide Building Society",
    # Insurance/Asset Management
    "Aviva", "Legal & General", "Prudential", "Standard Life", "Abrdn", "Schroders",
    "M&G", "BlackRock UK", "Fidelity International", "Jupiter Asset Management",
    # Professional Services
    "Deloitte UK", "PwC", "KPMG", "EY", "Grant Thornton", "BDO",
    "McKinsey & Company", "BCG", "Bain & Company", "Accenture",
    # Investment Banks
    "Goldman Sachs", "JP Morgan", "Morgan Stanley", "UBS", "Credit Suisse", "Citi",
    # Corporates
    "Unilever UK", "GSK", "AstraZeneca", "Diageo", "Reckitt", "BP", "Shell UK",
    "BT Group", "Vodafone", "Sky UK", "BBC", "ITV",
    # Tech
    "Microsoft UK", "Google UK", "Amazon UK", "Meta UK", "Apple UK", "Salesforce UK",
    # Healthcare
    "NHS Trust", "Bupa", "Nuffield Health",
    # Other
    "Civil Service", "British Airways", "Rolls-Royce", "BAE Systems", "JLR"
]

PENSION_PROVIDERS = [
    "Aviva", "Scottish Widows", "Legal & General", "Standard Life", "Royal London",
    "Fidelity", "Aegon", "Prudential", "Nest", "Hargreaves Lansdown",
    "AJ Bell", "Interactive Investor", "Vanguard", "Nutmeg", "PensionBee"
]

ISA_PROVIDERS = [
    "Hargreaves Lansdown", "AJ Bell", "Interactive Investor", "Vanguard", "Fidelity",
    "Charles Stanley", "Bestinvest", "Nutmeg", "Wealthify", "Moneybox", "Freetrade"
]

INSURANCE_PROVIDERS = [
    "Aviva", "Legal & General", "Zurich", "Royal London", "Scottish Widows",
    "AIG", "Vitality", "LV=", "Guardian", "Canada Life", "Aegon"
]

MORTGAGE_PROVIDERS = [
    "Halifax", "Nationwide", "Barclays", "NatWest", "Santander",
    "HSBC", "Lloyds", "TSB", "Virgin Money", "Metro Bank", "Yorkshire Building Society"
]

CONCERN_TOPICS = [
    ("retirement savings adequacy", "Worried about having enough for retirement. Wants to ensure comfortable lifestyle without running out of money.", "high"),
    ("inheritance tax liability", "Concerned about potential IHT exposure. Estate value approaching nil-rate band threshold. Wants to protect wealth for beneficiaries.", "medium"),
    ("market volatility impact", "Anxious about market fluctuations affecting portfolio value. Struggled during recent market corrections.", "medium"),
    ("protection gap - life insurance", "Insufficient life insurance cover for family needs. Current cover may not meet mortgage and income replacement needs.", "high"),
    ("protection gap - critical illness", "No critical illness cover in place. Family history of serious illness causing concern.", "high"),
    ("children's education funding", "Need to plan for private school fees and/or university costs. Concerned about rising education costs.", "high"),
    ("care costs in later life", "Worried about potential care home costs for self or parents. Wants to protect assets while ensuring quality care.", "medium"),
    ("mortgage strategy", "Fixed rate mortgage expiring soon. Concerned about higher interest rates on renewal.", "medium"),
    ("job security concerns", "Uncertainty about employment stability. Industry undergoing changes that may affect role.", "high"),
    ("supporting elderly parents", "May need to provide financial support to aging parents. Balancing own needs with family obligations.", "medium"),
    ("divorce settlement impact", "Financial recovery after divorce. Need to rebuild retirement savings and adjust plans.", "high"),
    ("business succession", "Planning exit strategy from business. Wants to maximize value and minimize tax on sale.", "medium"),
    ("pension drawdown strategy", "Unsure about sustainable withdrawal rate in retirement. Worried about sequence of returns risk.", "high"),
    ("estate planning complexity", "Multiple beneficiaries and complex family situation. Wants fair distribution while minimizing tax.", "medium"),
    ("tax efficiency", "Wants to minimize tax liability legally. Looking for ways to optimize ISAs, pensions, and other allowances.", "low"),
    ("inflation eroding savings", "Concerned about real value of savings being eroded. Cash savings losing purchasing power.", "medium"),
    ("pension consolidation", "Multiple old pensions from previous employers. Wants to simplify and potentially reduce fees.", "low"),
    ("income protection need", "No income protection in place. Concerned about ability to maintain lifestyle if unable to work.", "high"),
    ("healthcare costs", "Concerned about potential private healthcare costs. NHS waiting times causing anxiety.", "medium"),
    ("school fees planning", "Children approaching private school age. Need to plan funding without impacting retirement.", "high")
]

TAGS = [
    "high_net_worth", "ultra_high_net_worth", "retirement_planning", "young_professional",
    "family_planning", "business_owner", "expat_returning", "pre_retirement", "in_retirement",
    "newly_married", "divorced", "widowed", "first_time_buyer", "property_investor",
    "pension_consolidation", "protection_review", "tax_planning", "estate_planning",
    "school_fees", "university_planning", "career_change", "self_employed", "contractor",
    "nhs_pension", "db_pension", "final_salary", "annual_allowance", "lifetime_allowance",
    "iht_planning", "trust_planning", "charitable_giving"
]


# ============== HELPER FUNCTIONS ==============

def generate_ni_number() -> str:
    """Generate a realistic UK National Insurance number"""
    prefix = random.choice(["AB", "CD", "EF", "GH", "JK", "LM", "NP", "RS", "TW", "YZ"])
    numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    suffix = random.choice(["A", "B", "C", "D"])
    return f"{prefix}{numbers}{suffix}"


def generate_phone() -> str:
    """Generate a UK landline number"""
    area_codes = ["01234", "01onalonal621", "01onal onal823", "01onal onalonalonalonalonal onal93", "01onal onal534", "01onal onal onal onalonal onal onal onal onal onal onal onal onal onal71", "01onal onal onal onal onal onal58", "01onal onal onal onal onal onalonal onal94", "01452", "01onal onal onal onal onal onal onal onal onal onal onalonal onal onalonal onal73", "020"]
    area = random.choice(["01onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal42", "01onal onal onal onal onal onal onal onal onal onal onal onal onal83", "01onalonal onal onal onalonal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onalonalonal onal onal onal onal71", "01962", "01onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal92", "01onal onal onal onal onal onal onalonal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onalonal onal onal65", "01onalonal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onalonal34", "01onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onalonal onal onal onal onal onalonalonal25", "01onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onal onalonal onal56"])
    # Simplified
    return f"0{random.randint(1200, 1999)} {random.randint(100000, 999999)}"


def generate_mobile() -> str:
    """Generate a UK mobile number"""
    prefix = random.choice(["07700", "07711", "07722", "07733", "07744", "07755", "07766", "07777", "07788", "07799",
                           "07800", "07811", "07822", "07833", "07844", "07855", "07866", "07877", "07888", "07899"])
    return f"{prefix} {random.randint(100000, 999999)}"


def generate_email(first_name: str, last_name: str) -> str:
    """Generate a realistic email address"""
    domain = random.choice(["gmail.com", "outlook.com", "yahoo.co.uk", "hotmail.co.uk", "icloud.com", 
                           "btinternet.com", "sky.com", "virginmedia.com", "talktalk.net"])
    separator = random.choice([".", "_", ""])
    number = random.choice(["", str(random.randint(1, 99)), str(random.randint(1970, 1995))])
    return f"{first_name.lower()}{separator}{last_name.lower()}{number}@{domain}"


def generate_postcode(base: str) -> str:
    """Generate a full UK postcode from a base"""
    number = random.randint(1, 9)
    letters = ''.join(random.choices("ABDEFGHJLNPQRSTUWXYZ", k=2))
    return f"{base} {number}{letters}"


def generate_address() -> Dict[str, Any]:
    """Generate a UK address"""
    city, county, postcode_base = random.choice(UK_CITIES)
    house_num = random.randint(1, 150)
    street = random.choice(STREET_NAMES)
    
    line2_options = [None, None, None, f"Flat {random.randint(1, 20)}", f"Apartment {random.randint(1, 50)}"]
    
    return {
        "line1": f"{house_num} {street}",
        "line2": random.choice(line2_options),
        "city": city,
        "county": county,
        "postcode": generate_postcode(postcode_base),
        "country": "United Kingdom"
    }


def random_date_in_range(start: date, end: date) -> date:
    """Generate a random date between start and end"""
    delta = (end - start).days
    if delta <= 0:
        return start
    random_days = random.randint(0, delta)
    return start + timedelta(days=random_days)


def random_past_date(years_ago_min: int, years_ago_max: int) -> date:
    """Generate a random date in the past within a year range"""
    days_min = years_ago_min * 365
    days_max = years_ago_max * 365
    return TODAY - timedelta(days=random.randint(days_min, days_max))


def generate_dob_for_age(min_age: int, max_age: int) -> date:
    """Generate a DOB for someone of a given age range"""
    age = random.randint(min_age, max_age)
    year = TODAY.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe for all months
    return date(year, month, day)


def generate_birthday_soon(days_ahead: int = 14) -> date:
    """Generate a birthday coming up in the next N days"""
    days_until = random.randint(1, days_ahead)
    future_date = TODAY + timedelta(days=days_until)
    # Generate a birth year that makes them 28-72 years old
    birth_year = TODAY.year - random.randint(28, 72)
    return date(birth_year, future_date.month, future_date.day)


def generate_policy_number(prefix: str) -> str:
    """Generate a policy number"""
    return f"{prefix}-{random.randint(100000, 999999)}"


def ordinal(n: int) -> str:
    """Return ordinal string for a number (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return f"{n}{suffix}"


# ============== CLIENT GENERATION ==============

def generate_family_members(marital_status: str, client_age: int, client_gender: str) -> List[Dict]:
    """Generate family members based on marital status"""
    members = []
    
    if marital_status in ["married", "civil_partnership"]:
        # Spouse - opposite gender for married, same for civil partnership typically
        if marital_status == "civil_partnership":
            spouse_gender = client_gender
        else:
            spouse_gender = "female" if client_gender == "male" else "male"
        
        spouse_first = random.choice(UK_FIRST_NAMES_MALE if spouse_gender == "male" else UK_FIRST_NAMES_FEMALE)
        spouse_age = client_age + random.randint(-8, 8)
        spouse_occupation = random.choice(OCCUPATIONS)
        
        spouse_notes = []
        if spouse_occupation[0] not in ["Retired", "Retired (Professional)"]:
            salary = random.randint(int(spouse_occupation[2]/1000), int(spouse_occupation[3]/1000))
            spouse_notes.append(f"{spouse_occupation[0]}")
            spouse_notes.append(f"£{salary}k salary")
        else:
            spouse_notes.append("Retired")
        
        members.append({
            "name": spouse_first,
            "relationship": "spouse",
            "date_of_birth": (TODAY - timedelta(days=spouse_age*365 + random.randint(0, 364))).isoformat(),
            "notes": ", ".join(spouse_notes)
        })
        
        # Children (more likely if married and age 32-58)
        if 32 <= client_age <= 58 and random.random() < 0.75:
            num_children = random.choices([1, 2, 3, 4], weights=[0.25, 0.50, 0.20, 0.05])[0]
            for i in range(num_children):
                child_age = random.randint(1, min(client_age - 25, 30))
                child_gender = random.choice(["male", "female"])
                child_first = random.choice(UK_FIRST_NAMES_MALE if child_gender == "male" else UK_FIRST_NAMES_FEMALE)
                
                if child_age < 5:
                    notes = f"Age {child_age}, at nursery/home"
                elif child_age < 11:
                    notes = f"Age {child_age}, at primary school"
                elif child_age < 18:
                    school_type = random.choice(["state school", "private school", "grammar school"])
                    notes = f"Age {child_age}, at {school_type}"
                elif child_age < 23:
                    if random.random() < 0.55:
                        uni = random.choice(["Oxford", "Cambridge", "Imperial", "UCL", "Edinburgh", "Manchester", "Bristol", "LSE", "Warwick", "Durham"])
                        notes = f"Age {child_age}, studying at {uni}"
                    else:
                        notes = f"Age {child_age}, working"
                else:
                    notes = f"Age {child_age}, independent"
                
                members.append({
                    "name": child_first,
                    "relationship": "child",
                    "date_of_birth": (TODAY - timedelta(days=child_age*365 + random.randint(0, 364))).isoformat(),
                    "notes": notes
                })
        
        # Grandchildren for older clients
        if client_age >= 55 and random.random() < 0.4:
            num_grandchildren = random.randint(1, 4)
            for i in range(num_grandchildren):
                gc_age = random.randint(0, 15)
                gc_gender = random.choice(["male", "female"])
                gc_first = random.choice(UK_FIRST_NAMES_MALE if gc_gender == "male" else UK_FIRST_NAMES_FEMALE)
                
                members.append({
                    "name": gc_first,
                    "relationship": "grandchild",
                    "date_of_birth": (TODAY - timedelta(days=gc_age*365 + random.randint(0, 364))).isoformat(),
                    "notes": f"Age {gc_age}"
                })
    
    # Parents (more likely to be mentioned if client is 45+)
    if client_age >= 45 and random.random() < 0.35:
        parent_age = client_age + random.randint(22, 32)
        parent_status = random.choice([
            "Retired, living independently",
            "In care home, dementia care",
            "Requires daily support, lives nearby",
            "Living in sheltered housing",
            "Recently widowed, needs support",
            "Good health, very active"
        ])
        members.append({
            "name": random.choice(UK_FIRST_NAMES_FEMALE),
            "relationship": "mother",
            "date_of_birth": (TODAY - timedelta(days=parent_age*365)).isoformat() if random.random() < 0.6 else None,
            "notes": parent_status
        })
    
    return members


def generate_life_events(
    marital_status: str, 
    family_members: List[Dict], 
    force_anniversary_soon: bool = False
) -> List[Dict]:
    """Generate life events - past and upcoming"""
    events = []
    
    # Wedding anniversary if married
    if marital_status in ["married", "civil_partnership"]:
        years_married = random.randint(1, 40)
        
        if force_anniversary_soon:
            # Anniversary in next 30 days
            days_until = random.randint(1, 30)
            anniversary_date = TODAY + timedelta(days=days_until)
        else:
            anniversary_date = date(TODAY.year, random.randint(1, 12), random.randint(1, 28))
        
        spouse_name = next((m["name"] for m in family_members if m["relationship"] == "spouse"), None)
        
        events.append({
            "event_type": "anniversary",
            "event_date": anniversary_date.isoformat(),
            "description": f"{ordinal(years_married)} wedding anniversary",
            "related_person": spouse_name,
            "source": "client_mentioned",
            "created_at": datetime.now().isoformat()
        })
    
    # Children's milestones
    for member in family_members:
        if member["relationship"] == "child" and member.get("date_of_birth"):
            try:
                child_dob = date.fromisoformat(member["date_of_birth"])
                child_age = (TODAY - child_dob).days // 365
                
                # University start
                if 16 <= child_age <= 17:
                    uni_date = date(TODAY.year + (18 - child_age), 9, 1)
                    events.append({
                        "event_type": "other",
                        "event_date": uni_date.isoformat(),
                        "description": f"{member['name']} starting university - estimated £45k funding needed over 3 years",
                        "related_person": member["name"],
                        "source": "fact_find",
                        "created_at": datetime.now().isoformat()
                    })
                
                # Starting secondary school
                if child_age == 10:
                    events.append({
                        "event_type": "other",
                        "event_date": date(TODAY.year + 1, 9, 1).isoformat(),
                        "description": f"{member['name']} starting secondary school",
                        "related_person": member["name"],
                        "source": "client_mentioned",
                        "created_at": datetime.now().isoformat()
                    })
                    
                # Graduation
                if 20 <= child_age <= 22 and random.random() < 0.3:
                    events.append({
                        "event_type": "graduation",
                        "event_date": date(TODAY.year, 7, random.randint(1, 15)).isoformat(),
                        "description": f"{member['name']} graduating from university",
                        "related_person": member["name"],
                        "source": "client_mentioned",
                        "created_at": datetime.now().isoformat()
                    })
            except:
                pass
    
    # Random life events
    if random.random() < 0.4:
        random_events = [
            ("other", "Planning major home renovation - budget £75k", random.randint(60, 300)),
            ("other", "Considering buy-to-let investment property", random.randint(90, 365)),
            ("other", "Planning extended sabbatical travel - 6 months, budget £30k", random.randint(120, 400)),
            ("other", "Looking to help child with house deposit - £50k", random.randint(30, 180)),
            ("other", "Considering early retirement options", random.randint(180, 730)),
            ("house_purchase", "Planning to downsize main residence", random.randint(180, 365)),
            ("other", "Planning to gift to grandchildren for education", random.randint(30, 180)),
            ("new_job", "Potential career change to consultancy", random.randint(90, 270)),
            ("retirement", "Target retirement date approaching", random.randint(365, 1095))
        ]
        event_type, description, days_ahead = random.choice(random_events)
        events.append({
            "event_type": event_type,
            "event_date": (TODAY + timedelta(days=days_ahead)).isoformat(),
            "description": description,
            "related_person": None,
            "source": "meeting_notes",
            "created_at": datetime.now().isoformat()
        })
    
    return events


def generate_concerns(client_age: int, portfolio_value: float, has_children: bool) -> List[Dict]:
    """Generate client concerns based on age and wealth"""
    concerns = []
    num_concerns = random.randint(1, 4)
    
    # Filter concerns by relevance
    relevant_concerns = []
    for topic, details, severity in CONCERN_TOPICS:
        # Age-based filtering
        if "retirement" in topic.lower() and client_age < 40:
            continue
        if "education" in topic.lower() and (client_age > 60 or not has_children):
            continue
        if "school fees" in topic.lower() and (client_age > 55 or not has_children):
            continue
        if "inheritance tax" in topic.lower() and portfolio_value < 300000:
            continue
        if "care costs" in topic.lower() and client_age < 50:
            continue
        if "drawdown" in topic.lower() and client_age < 55:
            continue
        relevant_concerns.append((topic, details, severity))
    
    if not relevant_concerns:
        relevant_concerns = CONCERN_TOPICS[:5]
    
    selected = random.sample(relevant_concerns, min(num_concerns, len(relevant_concerns)))
    
    for topic, details, severity in selected:
        status = random.choices(["active", "monitoring", "addressed"], weights=[0.6, 0.25, 0.15])[0]
        
        concerns.append({
            "topic": topic,
            "details": details,
            "severity": severity,
            "date_raised": random_past_date(0, 2).isoformat(),
            "status": status,
            "last_discussed": random_past_date(0, 1).isoformat() if random.random() < 0.7 else None,
            "notes": None
        })
    
    return concerns


def generate_policies(
    client_age: int, 
    income: float, 
    is_high_earner: bool,
    force_renewal_soon: bool = False
) -> Tuple[List[Dict], float]:
    """Generate financial policies based on client profile"""
    policies = []
    total_value = 0
    
    # Workplace pension (most people have one)
    if random.random() < 0.90 and client_age < 68:
        if client_age > 45:
            pension_value = random.randint(80000, 800000)
        elif client_age > 35:
            pension_value = random.randint(30000, 300000)
        else:
            pension_value = random.randint(5000, 80000)
        
        total_value += pension_value
        monthly_contrib = round(income * random.uniform(0.05, 0.12) / 12, 2) if client_age < 68 else 0
        
        pension_type = random.choices(
            ["Workplace DC pension", "Group Personal Pension", "Stakeholder Pension"],
            weights=[0.6, 0.3, 0.1]
        )[0]
        
        policies.append({
            "policy_type": "pension",
            "provider": random.choice(PENSION_PROVIDERS),
            "policy_number": generate_policy_number("WPP"),
            "current_value": float(pension_value),
            "monthly_contribution": monthly_contrib,
            "start_date": random_past_date(2, 20).isoformat(),
            "renewal_date": None,
            "maturity_date": None,
            "notes": f"{pension_type} - employer contributes {random.randint(3, 10)}%"
        })
    
    # Old workplace pension(s) from previous employers
    if client_age > 35 and random.random() < 0.6:
        num_old_pensions = random.randint(1, 3)
        for _ in range(num_old_pensions):
            old_value = random.randint(10000, 100000)
            total_value += old_value
            policies.append({
                "policy_type": "pension",
                "provider": random.choice(PENSION_PROVIDERS),
                "policy_number": generate_policy_number("OLD"),
                "current_value": float(old_value),
                "monthly_contribution": 0.0,
                "start_date": random_past_date(5, 20).isoformat(),
                "renewal_date": None,
                "maturity_date": None,
                "notes": "Deferred pension from previous employer - consider consolidation"
            })
    
    # SIPP for higher earners
    if is_high_earner and random.random() < 0.55:
        sipp_value = random.randint(50000, 500000)
        total_value += sipp_value
        policies.append({
            "policy_type": "pension",
            "provider": random.choice(["Hargreaves Lansdown", "AJ Bell", "Interactive Investor", "Fidelity", "Charles Stanley"]),
            "policy_number": generate_policy_number("SIPP"),
            "current_value": float(sipp_value),
            "monthly_contribution": round(random.uniform(500, 3333), 2),
            "start_date": random_past_date(1, 15).isoformat(),
            "renewal_date": None,
            "maturity_date": None,
            "notes": "Self-invested personal pension - actively managed"
        })
    
    # DB Pension (final salary) - less common but valuable
    if random.random() < 0.15 and client_age > 40:
        db_value = random.randint(200000, 1000000)  # Transfer value
        policies.append({
            "policy_type": "pension",
            "provider": random.choice(["NHS Pension Scheme", "Teachers' Pension", "Civil Service Pension", "USS", "LGPS"]),
            "policy_number": generate_policy_number("DB"),
            "current_value": float(db_value),
            "monthly_contribution": 0.0,
            "start_date": random_past_date(10, 30).isoformat(),
            "renewal_date": None,
            "maturity_date": None,
            "notes": f"Defined Benefit scheme - projected £{random.randint(15, 45)}k/year at retirement. DO NOT TRANSFER."
        })
    
    # ISA (very common)
    if random.random() < 0.75:
        isa_value = random.randint(15000, 300000) if is_high_earner else random.randint(5000, 80000)
        total_value += isa_value
        policies.append({
            "policy_type": "isa",
            "provider": random.choice(ISA_PROVIDERS),
            "policy_number": generate_policy_number("ISA"),
            "current_value": float(isa_value),
            "monthly_contribution": round(random.uniform(200, 1666), 2),
            "start_date": random_past_date(1, 10).isoformat(),
            "renewal_date": None,
            "maturity_date": None,
            "notes": "Stocks and Shares ISA - globally diversified portfolio"
        })
    
    # Life insurance
    if random.random() < 0.65:
        sum_assured = random.choice([100000, 200000, 300000, 400000, 500000, 750000, 1000000])
        term_years = random.choice([10, 15, 20, 25])
        
        # Renewal date - force soon if needed
        if force_renewal_soon:
            renewal_date = TODAY + timedelta(days=random.randint(14, 60))
        else:
            renewal_date = TODAY + timedelta(days=random.randint(90, 365*term_years))
        
        premium = round(sum_assured * 0.0002 * (client_age / 40) * random.uniform(0.8, 1.2), 2)
        
        policies.append({
            "policy_type": "life_insurance",
            "provider": random.choice(INSURANCE_PROVIDERS),
            "policy_number": generate_policy_number("LIFE"),
            "current_value": float(sum_assured),
            "monthly_contribution": premium,
            "start_date": random_past_date(1, 15).isoformat(),
            "renewal_date": renewal_date.isoformat(),
            "maturity_date": None,
            "notes": f"Level term - {term_years} year term, sum assured £{sum_assured:,}"
        })
    
    # Critical illness (less common)
    if random.random() < 0.40:
        sum_assured = random.choice([50000, 100000, 150000, 200000, 250000])
        premium = round(sum_assured * 0.0004 * (client_age / 40) * random.uniform(0.8, 1.3), 2)
        
        policies.append({
            "policy_type": "critical_illness",
            "provider": random.choice(INSURANCE_PROVIDERS),
            "policy_number": generate_policy_number("CI"),
            "current_value": float(sum_assured),
            "monthly_contribution": premium,
            "start_date": random_past_date(1, 10).isoformat(),
            "renewal_date": (TODAY + timedelta(days=random.randint(60, 365*3))).isoformat(),
            "maturity_date": None,
            "notes": "Stand-alone critical illness cover"
        })
    
    # Income protection
    if random.random() < 0.30 and client_age < 60:
        monthly_benefit = round(income * 0.6 / 12, 0)
        premium = round(monthly_benefit * 0.02 * (client_age / 45), 2)
        
        policies.append({
            "policy_type": "income_protection",
            "provider": random.choice(INSURANCE_PROVIDERS),
            "policy_number": generate_policy_number("IP"),
            "current_value": float(monthly_benefit * 12),
            "monthly_contribution": premium,
            "start_date": random_past_date(1, 8).isoformat(),
            "renewal_date": (TODAY + timedelta(days=random.randint(180, 365*2))).isoformat(),
            "maturity_date": None,
            "notes": f"Income protection - £{int(monthly_benefit):,}/month benefit, 4 week deferred period"
        })
    
    # Mortgage (common for homeowners)
    if random.random() < 0.60 and client_age < 62:
        mortgage_balance = random.randint(150000, 900000)
        rate = round(random.uniform(3.5, 6.0), 2)
        
        # Maturity/renewal - force soon if needed
        if force_renewal_soon and random.random() < 0.5:
            maturity_date = TODAY + timedelta(days=random.randint(14, 60))
            notes = f"Fixed rate @ {rate}% - EXPIRES SOON, needs urgent review"
        else:
            maturity_days = random.randint(180, 365*4)
            maturity_date = TODAY + timedelta(days=maturity_days)
            notes = f"Fixed rate @ {rate}% - renewal {maturity_date.strftime('%b %Y')}"
        
        monthly_payment = round(mortgage_balance * 0.005, 2)
        
        policies.append({
            "policy_type": "mortgage",
            "provider": random.choice(MORTGAGE_PROVIDERS),
            "policy_number": generate_policy_number("MTG"),
            "current_value": float(mortgage_balance),
            "monthly_contribution": monthly_payment,
            "start_date": random_past_date(1, 5).isoformat(),
            "renewal_date": maturity_date.isoformat(),
            "maturity_date": maturity_date.isoformat(),
            "notes": notes
        })
    
    # GIA for wealthier clients
    if is_high_earner and random.random() < 0.45:
        gia_value = random.randint(30000, 400000)
        total_value += gia_value
        policies.append({
            "policy_type": "gia",
            "provider": random.choice(ISA_PROVIDERS),
            "policy_number": generate_policy_number("GIA"),
            "current_value": float(gia_value),
            "monthly_contribution": round(random.uniform(0, 2000), 2),
            "start_date": random_past_date(1, 8).isoformat(),
            "renewal_date": None,
            "maturity_date": None,
            "notes": "General Investment Account - overflow from ISA allowance"
        })
    
    return policies, total_value


def generate_risk_profile(client_age: int) -> Dict:
    """Generate risk profile based on age"""
    if client_age < 35:
        attitude = random.choices(["medium", "high", "very_high"], weights=[0.35, 0.45, 0.20])[0]
        horizon = random.randint(20, 40)
        experience = random.choices(["limited", "moderate", "extensive"], weights=[0.4, 0.4, 0.2])[0]
    elif client_age < 50:
        attitude = random.choices(["low", "medium", "high"], weights=[0.20, 0.50, 0.30])[0]
        horizon = random.randint(10, 25)
        experience = random.choices(["limited", "moderate", "extensive"], weights=[0.25, 0.50, 0.25])[0]
    elif client_age < 65:
        attitude = random.choices(["very_low", "low", "medium"], weights=[0.20, 0.50, 0.30])[0]
        horizon = random.randint(5, 15)
        experience = random.choices(["limited", "moderate", "extensive"], weights=[0.2, 0.45, 0.35])[0]
    else:
        attitude = random.choices(["very_low", "low", "medium"], weights=[0.40, 0.40, 0.20])[0]
        horizon = random.randint(3, 12)
        experience = random.choices(["limited", "moderate", "extensive"], weights=[0.15, 0.40, 0.45])[0]
    
    capacity = random.choices(["low", "medium", "high"], weights=[0.25, 0.50, 0.25])[0]
    
    return {
        "attitude_to_risk": attitude,
        "capacity_for_loss": capacity,
        "investment_experience": experience,
        "time_horizon_years": horizon,
        "last_assessed": random_past_date(0, 2).isoformat(),
        "notes": None
    }


def generate_interactions(is_dormant: bool, client_since: date) -> List[Dict]:
    """Generate interaction history"""
    interactions = []
    
    if is_dormant:
        # Last interaction was 90+ days ago
        last_contact = TODAY - timedelta(days=random.randint(90, 200))
        num_interactions = random.randint(2, 6)
    else:
        # Recent contact
        last_contact = TODAY - timedelta(days=random.randint(3, 60))
        num_interactions = random.randint(4, 15)
    
    summaries = [
        "Annual review meeting - discussed portfolio performance, rebalancing, and updated goals",
        "Phone call to discuss recent market volatility and provide reassurance",
        "Email follow-up with documents requested - policy illustrations and projections",
        "Quick call to remind about ISA deadline and discuss contribution strategy",
        "Meeting to review protection needs following change in circumstances",
        "Response to client query about pension contribution limits",
        "Sent birthday wishes with personalised market commentary",
        "Detailed discussion about retirement planning timeline and income needs",
        "Reviewed life insurance renewal options and recommended changes",
        "Catch-up call about family changes - new grandchild, may affect estate plans",
        "Sent quarterly portfolio report with performance commentary",
        "Discussed potential property investment and impact on overall plan",
        "Provided update on ISA allowance usage and suggested top-up",
        "Meeting to discuss children's Junior ISA strategy",
        "Phone call to explain recent fund switch recommendation",
        "Sent information about new tax-efficient investment opportunity",
        "Review meeting following completion of pension consolidation"
    ]
    
    current_date = last_contact
    for i in range(num_interactions):
        method = random.choices(
            ["email", "phone", "video_call", "in_person"],
            weights=[0.35, 0.30, 0.20, 0.15]
        )[0]
        direction = random.choices(["outbound", "inbound"], weights=[0.65, 0.35])[0]
        
        interactions.append({
            "interaction_date": datetime.combine(current_date, datetime.min.time()).isoformat(),
            "method": method,
            "direction": direction,
            "summary": random.choice(summaries),
            "duration_minutes": random.randint(5, 60) if method != "email" else None,
            "next_action": random.choice([None, "Follow up in 2 weeks", "Send documents", "Schedule review", "Await client response"]) if i == 0 else None
        })
        
        # Go back in time for next interaction
        current_date = current_date - timedelta(days=random.randint(14, 75))
        if current_date < client_since:
            break
    
    return interactions


def generate_follow_ups(has_overdue: bool = False, has_due_soon: bool = False) -> List[Dict]:
    """Generate follow-up commitments"""
    follow_ups = []
    num_follow_ups = random.randint(1, 5) if (has_overdue or has_due_soon) else random.randint(0, 5)
    
    commitments = [
        "Send pension consolidation recommendation report with fee comparison",
        "Provide ISA investment options comparison document",
        "Follow up on life insurance application - chase underwriting",
        "Schedule meeting to discuss inheritance tax planning strategies",
        "Send information on sustainable/ESG investment options",
        "Provide mortgage renewal comparison with broker recommendations",
        "Follow up on critical illness cover quote from Vitality",
        "Send school fees planning illustration with assumptions",
        "Arrange meeting with tax specialist regarding CGT exposure",
        "Review and send updated retirement cashflow projection",
        "Provide information on VCT/EIS investment opportunities",
        "Send summary of annual review meeting with action points",
        "Chase pension provider for transfer value statement",
        "Arrange introduction meeting with estate planning solicitor",
        "Send comparison of drawdown vs annuity options"
    ]
    
    for i in range(num_follow_ups):
        if has_overdue and i == 0:
            # Make first one overdue
            deadline = TODAY - timedelta(days=random.randint(7, 45))
            status = "pending"  # Overdue but still pending
        elif has_due_soon and i == 0:
            # Make first one due in next 30 days
            deadline = TODAY + timedelta(days=random.randint(1, 30))
            status = "pending"
        elif random.random() < 0.25:
            # Completed
            deadline = random_past_date(0, 1)
            status = "completed"
        else:
            # Future pending
            deadline = TODAY + timedelta(days=random.randint(7, 75))
            status = "pending"
        
        follow_ups.append({
            "commitment": random.choice(commitments),
            "deadline": deadline.isoformat(),
            "status": status,
            "created_date": (deadline - timedelta(days=random.randint(7, 30))).isoformat(),
            "completed_date": deadline.isoformat() if status == "completed" else None,
            "notes": None
        })
    
    return follow_ups


def generate_compliance(has_overdue_review: bool = False, client_since: date = None, has_review_due_soon: bool = False) -> Dict:
    """Generate compliance record"""
    if client_since is None:
        client_since = TODAY - timedelta(days=365*3)
    
    if has_overdue_review:
        # Review is overdue
        last_review = TODAY - timedelta(days=random.randint(400, 550))
        next_review = TODAY - timedelta(days=random.randint(30, 180))
        review_status = "overdue"
    elif has_review_due_soon:
        # Review due in next 30 days
        last_review = TODAY - timedelta(days=random.randint(335, 360))
        next_review = TODAY + timedelta(days=random.randint(1, 30))
        review_status = "pending"
    else:
        # Review is up to date or upcoming
        last_review = TODAY - timedelta(days=random.randint(30, 300))
        next_review = last_review + timedelta(days=365)
        if next_review > TODAY:
            review_status = random.choice(["completed", "pending"])
        else:
            review_status = "pending"
    
    value_items = [
        "Consolidated 3 old pensions saving £450/year in fees",
        "Implemented tax-efficient drawdown strategy saving estimated £3k/year",
        "Reviewed and updated protection cover - closed £200k gap",
        "Identified £12k annual ISA allowance unutilized - now maximised",
        "Restructured investments reducing risk appropriately for life stage",
        "Recommended salary sacrifice increasing take-home pay by £150/month",
        "Identified pension carry-forward opportunity - £30k additional contribution",
        "Switched to lower-cost fund range saving 0.3% per annum",
        "Implemented bed and ISA strategy for CGT efficiency",
        "Reviewed mortgage and saved £200/month on renewal",
        "Set up Junior ISAs for children maximising allowances"
    ]
    
    return {
        "last_annual_review": last_review.isoformat(),
        "next_review_due": next_review.isoformat(),
        "review_status": review_status,
        "suitability_confirmed": review_status == "completed",
        "suitability_date": last_review.isoformat() if review_status == "completed" else None,
        "value_delivered": random.sample(value_items, random.randint(1, 4)),
        "notes": None
    }


def generate_meeting_notes(num_meetings: int = 2) -> List[Dict]:
    """Generate meeting notes"""
    notes = []
    
    meeting_data = [
        ("Annual review completed", 
         ["Reviewed portfolio performance - up 8% YTD", "Discussed retirement timeline - targeting age 62", "Updated risk profile questionnaire", "Agreed to increase pension contributions by £200/month"],
         ["Send updated cashflow projection", "Research sustainable fund options", "Schedule protection review"]),
        
        ("Protection review meeting", 
         ["Assessed life insurance needs - current cover adequate", "Discussed critical illness options - recommended £150k", "Reviewed income protection - 4 week deferred period agreed"],
         ["Obtain CI quotes from Vitality and Legal & General", "Send policy comparison document"]),
        
        ("Retirement planning session", 
         ["Ran cashflow projections to age 95", "Discussed drawdown vs annuity - flexible drawdown preferred", "Reviewed State Pension entitlement - £10,600/year from 2028"],
         ["Update projection with different scenarios", "Send PCLS options explanation"]),
        
        ("Initial fact find completed", 
         ["Gathered comprehensive financial information", "Discussed goals and priorities - education funding key", "Explained advisory process and fees", "Identified protection gap"],
         ["Prepare suitability report", "Obtain existing policy information", "Schedule follow-up meeting"]),
        
        ("Investment review", 
         ["Discussed market outlook - cautiously optimistic", "Reviewed fund performance - some underperformers identified", "Agreed to rebalance portfolio - reduce UK bias"],
         ["Implement fund switches", "Send updated portfolio breakdown"]),
        
        ("Tax planning meeting", 
         ["Reviewed ISA contributions - on track for full allowance", "Discussed pension carry-forward - £40k available", "Explored VCT/EIS options - decided not suitable"],
         ["Send pension contribution illustration", "Coordinate with accountant on timing"])
    ]
    
    for i in range(num_meetings):
        summary, key_points, actions = random.choice(meeting_data)
        meeting_date = random_past_date(0, 2)
        
        notes.append({
            "meeting_date": meeting_date.isoformat(),
            "meeting_type": random.choice(["video_call", "in_person", "phone"]),
            "duration_minutes": random.choice([30, 45, 60, 90]),
            "summary": summary,
            "transcript": None,
            "key_points": key_points,
            "action_items": actions,
            "concerns_raised": random.sample(["market volatility", "retirement income", "tax efficiency", "protection adequacy"], random.randint(0, 2)),
            "life_events_mentioned": []
        })
    
    return notes


def generate_single_client(
    client_id: str,
    force_birthday_soon: bool = False,
    force_anniversary_soon: bool = False,
    force_dormant: bool = False,
    force_review_overdue: bool = False,
    force_review_due_soon: bool = False,
    force_follow_up_overdue: bool = False,
    force_follow_up_due_soon: bool = False,
    force_policy_renewal_soon: bool = False
) -> Dict:
    """Generate a single client with all fields populated"""
    
    # Basic demographics
    gender = random.choice(["male", "female"])
    first_name = random.choice(UK_FIRST_NAMES_MALE if gender == "male" else UK_FIRST_NAMES_FEMALE)
    last_name = random.choice(UK_LAST_NAMES)
    
    if gender == "male":
        title = random.choices(["Mr", "Dr"], weights=[0.92, 0.08])[0]
    else:
        title = random.choices(["Mrs", "Ms", "Miss", "Dr"], weights=[0.50, 0.35, 0.07, 0.08])[0]
    
    # Age - mostly 30-72 for IFA clients
    if force_birthday_soon:
        dob = generate_birthday_soon(14)
    else:
        dob = generate_dob_for_age(28, 72)
    
    age = (TODAY - dob).days // 365
    
    # Marital status based on age
    if age < 30:
        marital_status = random.choices(
            ["single", "married", "civil_partnership"], 
            weights=[0.55, 0.40, 0.05]
        )[0]
    elif age < 45:
        marital_status = random.choices(
            ["single", "married", "divorced", "civil_partnership"], 
            weights=[0.12, 0.73, 0.10, 0.05]
        )[0]
    elif age < 60:
        marital_status = random.choices(
            ["single", "married", "divorced", "widowed"], 
            weights=[0.08, 0.70, 0.15, 0.07]
        )[0]
    else:
        marital_status = random.choices(
            ["single", "married", "divorced", "widowed"], 
            weights=[0.05, 0.60, 0.15, 0.20]
        )[0]
    
    # Occupation and income
    occupation_data = random.choice(OCCUPATIONS)
    occupation = occupation_data[0]
    
    if occupation_data[1]:  # Has an industry
        employer = random.choice(EMPLOYERS)
    else:
        employer = None
    
    if "Retired" in occupation:
        employer = None
        income = random.randint(occupation_data[2], occupation_data[3])
    else:
        income = random.randint(occupation_data[2], occupation_data[3])
    
    is_high_earner = income > 80000
    
    # Contact info
    address = generate_address()
    contact_info = {
        "email": generate_email(first_name, last_name),
        "phone": generate_phone(),
        "mobile": generate_mobile(),
        "address": address,
        "preferred_contact_method": random.choices(
            ["email", "phone", "video_call"], 
            weights=[0.60, 0.25, 0.15]
        )[0],
        "best_time_to_call": random.choice(["Morning", "Afternoon", "Evening", "Anytime", None])
    }
    
    # Family
    family_members = generate_family_members(marital_status, age, gender)
    has_children = any(m["relationship"] == "child" for m in family_members)
    
    # Life events
    life_events = generate_life_events(marital_status, family_members, force_anniversary_soon)
    
    # Concerns
    portfolio_estimate = income * random.uniform(3, 8)  # Rough estimate
    concerns = generate_concerns(age, portfolio_estimate, has_children)
    
    # Policies
    policies, total_value = generate_policies(age, income, is_high_earner, force_policy_renewal_soon)
    
    # Risk profile
    risk_profile = generate_risk_profile(age)
    
    # Client since date
    client_since = random_past_date(1, 12)
    
    # Interactions (dormancy)
    interactions = generate_interactions(force_dormant, client_since)
    
    # Follow-ups
    follow_ups = generate_follow_ups(force_follow_up_overdue, force_follow_up_due_soon)
    
    # Compliance
    compliance = generate_compliance(force_review_overdue, client_since, force_review_due_soon)
    
    # Meeting notes
    meeting_notes = generate_meeting_notes(random.randint(1, 4))
    
    # Tags
    client_tags = []
    if total_value >= 500000:
        client_tags.append("high_net_worth")
    if total_value >= 1000000:
        client_tags.append("ultra_high_net_worth")
    if 55 <= age < 65:
        client_tags.append("pre_retirement")
    if age >= 65:
        client_tags.append("in_retirement")
    if has_children:
        client_tags.append("family_planning")
    if occupation == "Business Owner" or occupation == "Company Director":
        client_tags.append("business_owner")
    if "Retired" in occupation:
        client_tags.append("retirement_planning")
    
    # Add some random relevant tags
    extra_tags = random.sample([t for t in TAGS if t not in client_tags], random.randint(0, 3))
    client_tags.extend(extra_tags)
    client_tags = list(set(client_tags))[:6]  # Max 6 tags
    
    return {
        "id": client_id,
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob.isoformat(),
        "national_insurance": generate_ni_number(),
        "occupation": occupation,
        "employer": employer,
        "annual_income": float(income),
        "contact_info": contact_info,
        "marital_status": marital_status,
        "family_members": family_members,
        "life_events": life_events,
        "concerns": concerns,
        "policies": policies,
        "total_portfolio_value": float(total_value) if total_value > 0 else None,
        "risk_profile": risk_profile,
        "meeting_notes": meeting_notes,
        "follow_ups": follow_ups,
        "interactions": interactions,
        "compliance": compliance,
        "client_since": client_since.isoformat(),
        "assigned_advisor": "default",
        "tags": client_tags,
        "notes": None
    }


def generate_all_clients(num_clients: int = NUM_CLIENTS) -> List[Dict]:
    """Generate all clients with proper distribution of scenarios"""
    clients = []
    
    # Calculate target counts
    num_dormant = int(num_clients * DORMANT_PERCENTAGE)
    num_review_overdue = int(num_clients * REVIEW_OVERDUE_PERCENTAGE)
    num_follow_up_overdue = int(num_clients * FOLLOW_UP_OVERDUE_PERCENTAGE)
    
    # Track assignments
    dormant_count = 0
    review_overdue_count = 0
    review_due_soon_count = 0
    follow_up_overdue_count = 0
    follow_up_due_soon_count = 0
    birthday_count = 0
    anniversary_count = 0
    renewal_count = 0
    
    for i in range(num_clients):
        client_id = f"CLT-2024{str(i + 1).zfill(3)}"
        
        # Determine flags
        force_birthday_soon = birthday_count < BIRTHDAY_SOON_COUNT
        force_anniversary_soon = anniversary_count < ANNIVERSARY_SOON_COUNT and not force_birthday_soon
        force_dormant = dormant_count < num_dormant and random.random() < 0.25
        force_review_overdue = review_overdue_count < num_review_overdue and random.random() < 0.35
        force_review_due_soon = not force_review_overdue and review_due_soon_count < REVIEW_DUE_SOON_COUNT and random.random() < 0.20
        force_follow_up_overdue = follow_up_overdue_count < num_follow_up_overdue and random.random() < 0.20
        force_follow_up_due_soon = not force_follow_up_overdue and follow_up_due_soon_count < FOLLOW_UP_DUE_SOON_COUNT and random.random() < 0.25
        force_policy_renewal = renewal_count < POLICY_RENEWAL_SOON_COUNT and random.random() < 0.15
        
        client = generate_single_client(
            client_id=client_id,
            force_birthday_soon=force_birthday_soon,
            force_anniversary_soon=force_anniversary_soon,
            force_dormant=force_dormant,
            force_review_overdue=force_review_overdue,
            force_review_due_soon=force_review_due_soon,
            force_follow_up_overdue=force_follow_up_overdue,
            force_follow_up_due_soon=force_follow_up_due_soon,
            force_policy_renewal_soon=force_policy_renewal
        )
        
        # Update counters
        if force_birthday_soon:
            birthday_count += 1
        if force_anniversary_soon:
            anniversary_count += 1
        if force_dormant:
            dormant_count += 1
        if force_review_overdue:
            review_overdue_count += 1
        if force_review_due_soon:
            review_due_soon_count += 1
        if force_follow_up_overdue:
            follow_up_overdue_count += 1
        if force_follow_up_due_soon:
            follow_up_due_soon_count += 1
        if force_policy_renewal:
            renewal_count += 1
        
        clients.append(client)
    
    return clients


# ============== ANALYSIS HELPERS ==============

def is_birthday_soon(client: Dict, days: int = 14) -> bool:
    """Check if client has birthday in next N days"""
    try:
        dob = date.fromisoformat(client["date_of_birth"])
        this_year_birthday = date(TODAY.year, dob.month, dob.day)
        days_until = (this_year_birthday - TODAY).days
        if days_until < 0:  # Birthday passed this year
            next_year_birthday = date(TODAY.year + 1, dob.month, dob.day)
            days_until = (next_year_birthday - TODAY).days
        return 0 <= days_until <= days
    except:
        return False


def has_anniversary_soon(client: Dict, days: int = 30) -> bool:
    """Check if client has anniversary in next N days"""
    for event in client.get("life_events", []):
        if event.get("event_type") == "anniversary":
            try:
                event_date = date.fromisoformat(event["event_date"])
                # Check this year's date
                this_year = date(TODAY.year, event_date.month, event_date.day)
                days_until = (this_year - TODAY).days
                if 0 <= days_until <= days:
                    return True
            except:
                pass
    return False


def is_dormant(client: Dict, days: int = 90) -> bool:
    """Check if client is dormant (no contact in N days)"""
    if not client.get("interactions"):
        return True
    try:
        last_interaction = max(client["interactions"], key=lambda x: x["interaction_date"])
        last_date = datetime.fromisoformat(last_interaction["interaction_date"]).date()
        return (TODAY - last_date).days >= days
    except:
        return True


def has_overdue_follow_up(client: Dict) -> bool:
    """Check if client has any overdue follow-ups"""
    for fu in client.get("follow_ups", []):
        if fu["status"] == "pending":
            try:
                deadline = date.fromisoformat(fu["deadline"])
                if deadline < TODAY:
                    return True
            except:
                pass
    return False


def has_follow_up_due_soon(client: Dict, days: int = 30) -> bool:
    """Check if client has follow-ups due in next N days"""
    for fu in client.get("follow_ups", []):
        if fu["status"] == "pending":
            try:
                deadline = date.fromisoformat(fu["deadline"])
                days_until = (deadline - TODAY).days
                if 0 <= days_until <= days:
                    return True
            except:
                pass
    return False


def has_review_due_soon(client: Dict, days: int = 30) -> bool:
    """Check if client has review due in next N days (but not overdue)"""
    try:
        next_review = date.fromisoformat(client['compliance']['next_review_due'])
        days_until = (next_review - TODAY).days
        return 0 <= days_until <= days
    except:
        return False


def has_policy_renewal_soon(client: Dict, days: int = 60) -> bool:
    """Check if client has policy renewal in next N days"""
    for policy in client.get("policies", []):
        renewal = policy.get("renewal_date") or policy.get("maturity_date")
        if renewal:
            try:
                renewal_date = date.fromisoformat(renewal)
                days_until = (renewal_date - TODAY).days
                if 0 <= days_until <= days:
                    return True
            except:
                pass
    return False


def print_statistics(clients: List[Dict]):
    """Print summary statistics about generated clients"""
    print("\n📊 Generated Client Statistics:")
    print("=" * 50)
    
    # Basic counts
    print(f"\n👥 Total clients: {len(clients)}")
    
    # Demographics
    married = sum(1 for c in clients if c['marital_status'] in ['married', 'civil_partnership'])
    single = sum(1 for c in clients if c['marital_status'] == 'single')
    divorced = sum(1 for c in clients if c['marital_status'] == 'divorced')
    widowed = sum(1 for c in clients if c['marital_status'] == 'widowed')
    print(f"\n💑 Marital Status:")
    print(f"   Married/Civil Partnership: {married}")
    print(f"   Single: {single}")
    print(f"   Divorced: {divorced}")
    print(f"   Widowed: {widowed}")
    
    # Age distribution
    ages = [(TODAY - date.fromisoformat(c['date_of_birth'])).days // 365 for c in clients]
    age_brackets = {
        "Under 35": sum(1 for a in ages if a < 35),
        "35-44": sum(1 for a in ages if 35 <= a < 45),
        "45-54": sum(1 for a in ages if 45 <= a < 55),
        "55-64": sum(1 for a in ages if 55 <= a < 65),
        "65+": sum(1 for a in ages if a >= 65)
    }
    print(f"\n🎂 Age Distribution:")
    for bracket, count in age_brackets.items():
        print(f"   {bracket}: {count}")
    
    # Alerts and actions needed
    birthdays_soon = sum(1 for c in clients if is_birthday_soon(c, 14))
    anniversaries_soon = sum(1 for c in clients if has_anniversary_soon(c, 30))
    dormant = sum(1 for c in clients if is_dormant(c, 90))
    review_overdue = sum(1 for c in clients if c['compliance']['review_status'] == 'overdue')
    review_due_soon = sum(1 for c in clients if has_review_due_soon(c, 30))
    follow_ups_overdue = sum(1 for c in clients if has_overdue_follow_up(c))
    follow_ups_due_soon = sum(1 for c in clients if has_follow_up_due_soon(c, 30))
    renewals_soon = sum(1 for c in clients if has_policy_renewal_soon(c, 60))
    
    print(f"\n🔔 Action Items:")
    print(f"   Birthdays in next 14 days: {birthdays_soon}")
    print(f"   Anniversaries in next 30 days: {anniversaries_soon}")
    print(f"   Dormant clients (90+ days): {dormant}")
    print(f"   Annual reviews overdue: {review_overdue}")
    print(f"   Annual reviews due in 30 days: {review_due_soon}")
    print(f"   Follow-ups overdue: {follow_ups_overdue}")
    print(f"   Follow-ups due in 30 days: {follow_ups_due_soon}")
    print(f"   Policy renewals in 60 days: {renewals_soon}")
    
    # Portfolio values
    portfolios = [c.get('total_portfolio_value', 0) or 0 for c in clients]
    high_net_worth = sum(1 for p in portfolios if p >= 100000)
    ultra_hnw = sum(1 for p in portfolios if p >= 500000)
    print(f"\n💰 Portfolio Values:")
    print(f"   High Net Worth (£100k+): {high_net_worth}")
    print(f"   Ultra HNW (£500k+): {ultra_hnw}")
    print(f"   Average portfolio: £{sum(portfolios)/len(portfolios):,.0f}")
    print(f"   Highest portfolio: £{max(portfolios):,.0f}")


def save_clients(clients: List[Dict], output_path: str = None):
    """Save clients to JSON file"""
    if output_path is None:
        output_path = Path(__file__).parent / "clients.json"
    
    data = {
        "clients": clients,
        "last_updated": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\n✅ Generated {len(clients)} clients")
    print(f"📁 Saved to: {output_path}")


# ============== MAIN ==============

if __name__ == "__main__":
    print("🤖 Jarvis Mock Client Generator")
    print("=" * 50)
    print(f"📅 Simulation date: {TODAY}")
    print(f"🎯 Generating {NUM_CLIENTS} clients...")
    
    # Generate clients
    clients = generate_all_clients(NUM_CLIENTS)
    
    # Save to file
    save_clients(clients)
    
    # Print statistics
    print_statistics(clients)
    
    print("\n" + "=" * 50)
    print("✨ Done! Restart the Jarvis app to load the new data.")
    print("=" * 50)
