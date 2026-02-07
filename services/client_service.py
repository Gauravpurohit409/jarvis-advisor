"""
Client Service
CRUD operations and client data access for Jarvis
"""

import json
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from data.schema import Client, ClientDatabase, ConcernStatus, FollowUpStatus


class ClientService:
    """
    Service for managing client data
    Provides search, filtering, and retrieval operations
    """
    
    def __init__(self, data_file: Optional[Path] = None):
        """Initialize with path to clients.json"""
        if data_file is None:
            data_file = Path(__file__).parent.parent / "data" / "clients.json"
        
        self.data_file = data_file
        self._clients: List[Client] = []
        self._load_clients()
    
    def _load_clients(self):
        """Load clients from JSON file"""
        if not self.data_file.exists():
            print(f"Warning: {self.data_file} not found. Run mock_generator.py first.")
            self._clients = []
            return
        
        with open(self.data_file, "r") as f:
            data = json.load(f)
        
        db = ClientDatabase(**data)
        self._clients = db.clients
        print(f"Loaded {len(self._clients)} clients")
    
    def _save_clients(self):
        """Save clients to JSON file"""
        db = ClientDatabase(clients=self._clients)
        with open(self.data_file, "w") as f:
            json.dump(db.model_dump(mode='json'), f, indent=2, default=str)
    
    def reload(self):
        """Reload clients from file"""
        self._load_clients()
    
    def add_client(self, client: Client) -> bool:
        """Add a new client and save to file"""
        # Check for duplicate ID
        if self.get_client_by_id(client.id):
            return False
        
        self._clients.append(client)
        self._save_clients()
        return True
    
    def add_client_from_dict(self, client_data: dict) -> tuple[bool, str, Optional[Client]]:
        """
        Add a new client from dictionary data.
        Returns (success, message, client)
        """
        try:
            client = Client(**client_data)
            if self.get_client_by_id(client.id):
                return False, f"Client with ID {client.id} already exists", None
            
            self._clients.append(client)
            self._save_clients()
            return True, f"Successfully added client: {client.full_name}", client
        except Exception as e:
            return False, f"Error parsing client data: {str(e)}", None
    
    # ============== BASIC CRUD ==============
    
    def get_all_clients(self) -> List[Client]:
        """Get all clients"""
        return self._clients
    
    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        """Get a specific client by ID"""
        for client in self._clients:
            if client.id == client_id:
                return client
        return None
    
    def search_by_name(self, query: str) -> List[Client]:
        """Search clients by name (case-insensitive)"""
        query = query.lower()
        return [
            c for c in self._clients 
            if query in c.first_name.lower() 
            or query in c.last_name.lower()
            or query in c.full_name.lower()
        ]
    
    def get_client_count(self) -> int:
        """Get total number of clients"""
        return len(self._clients)
    
    # ============== INTERACTION TRACKING ==============
    
    def get_clients_by_last_contact(self, days: int, older_than: bool = True) -> List[Client]:
        """
        Get clients based on last contact date
        
        Args:
            days: Number of days threshold
            older_than: If True, return clients NOT contacted in 'days'. 
                       If False, return clients contacted within 'days'.
        """
        results = []
        for client in self._clients:
            days_since = client.days_since_last_contact
            
            if days_since is None:
                if older_than:
                    results.append(client)  # Never contacted = definitely older
                continue
            
            if older_than and days_since > days:
                results.append(client)
            elif not older_than and days_since <= days:
                results.append(client)
        
        return sorted(results, key=lambda c: c.days_since_last_contact or 999, reverse=True)
    
    def get_dormant_clients(self, days: int = 90) -> List[Client]:
        """Get clients not contacted in specified days"""
        return self.get_clients_by_last_contact(days, older_than=True)
    
    def get_recently_contacted(self, days: int = 30) -> List[Client]:
        """Get clients contacted within specified days"""
        return self.get_clients_by_last_contact(days, older_than=False)
    
    # ============== COMPLIANCE ==============
    
    def get_clients_review_overdue(self) -> List[Client]:
        """Get clients with overdue annual reviews"""
        return [c for c in self._clients if c.has_overdue_review]
    
    def get_clients_review_due_soon(self, days: int = 30) -> List[Client]:
        """Get clients with reviews due within specified days"""
        today = date.today()
        results = []
        
        for client in self._clients:
            if client.compliance.next_review_due:
                days_until = (client.compliance.next_review_due - today).days
                if 0 <= days_until <= days:
                    results.append(client)
        
        return sorted(results, key=lambda c: c.compliance.next_review_due)
    
    # ============== CONCERNS ==============
    
    def get_clients_with_active_concerns(self) -> List[Client]:
        """Get clients with active concerns"""
        return [c for c in self._clients if c.active_concerns]
    
    def search_by_concern(self, topic: str) -> List[Client]:
        """Search clients by concern topic"""
        topic = topic.lower()
        return [
            c for c in self._clients
            if any(topic in concern.topic.lower() for concern in c.concerns)
        ]
    
    # ============== FOLLOW-UPS ==============
    
    def get_clients_with_pending_follow_ups(self) -> List[Client]:
        """Get clients with pending follow-ups"""
        return [c for c in self._clients if c.pending_follow_ups]
    
    def get_clients_with_overdue_follow_ups(self) -> List[Client]:
        """Get clients with overdue follow-ups"""
        return [c for c in self._clients if c.overdue_follow_ups]
    
    # ============== LIFE EVENTS ==============
    
    def get_upcoming_life_events(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get all upcoming life events within specified days"""
        today = date.today()
        events = []
        
        for client in self._clients:
            for event in client.life_events:
                days_until = (event.event_date - today).days
                if 0 <= days_until <= days:
                    events.append({
                        "client": client,
                        "event": event,
                        "days_until": days_until
                    })
        
        return sorted(events, key=lambda x: x["days_until"])
    
    def get_upcoming_birthdays(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get clients with birthdays in next N days"""
        today = date.today()
        birthdays = []
        
        for client in self._clients:
            # Client's own birthday
            this_year_bday = client.date_of_birth.replace(year=today.year)
            if this_year_bday < today:
                this_year_bday = this_year_bday.replace(year=today.year + 1)
            
            days_until = (this_year_bday - today).days
            if 0 <= days_until <= days:
                turning_age = today.year - client.date_of_birth.year
                if this_year_bday.year > today.year:
                    turning_age += 1
                
                birthdays.append({
                    "client": client,
                    "date": this_year_bday,
                    "days_until": days_until,
                    "turning_age": turning_age,
                    "is_milestone": turning_age in [55, 60, 65, 70, 75]
                })
        
        return sorted(birthdays, key=lambda x: x["days_until"])
    
    # ============== POLICIES ==============
    
    def get_policies_expiring_soon(self, days: int = 60) -> List[Dict[str, Any]]:
        """Get policies with upcoming renewal/expiry dates"""
        today = date.today()
        expiring = []
        
        for client in self._clients:
            for policy in client.policies:
                if policy.renewal_date:
                    days_until = (policy.renewal_date - today).days
                    if 0 <= days_until <= days:
                        expiring.append({
                            "client": client,
                            "policy": policy,
                            "days_until": days_until
                        })
        
        return sorted(expiring, key=lambda x: x["days_until"])
    
    def get_high_value_clients(self, threshold: float = 250000) -> List[Client]:
        """Get clients with portfolio value above threshold"""
        return [
            c for c in self._clients 
            if c.total_portfolio_value and c.total_portfolio_value >= threshold
        ]
    
    # ============== CLIENT CONTEXT ==============
    
    def get_client_summary(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive client summary for LLM context
        Returns structured data about the client
        """
        client = self.get_client_by_id(client_id)
        if not client:
            return None
        
        return {
            "basic_info": {
                "name": client.full_name,
                "age": client.age,
                "occupation": client.occupation,
                "marital_status": client.marital_status,
                "client_since": str(client.client_since),
            },
            "contact": {
                "email": client.contact_info.email,
                "phone": client.contact_info.phone,
                "preferred_method": client.contact_info.preferred_contact_method.value,
                "days_since_contact": client.days_since_last_contact,
            },
            "family": [
                {"name": m.name, "relationship": m.relationship}
                for m in client.family_members
            ],
            "portfolio": {
                "total_value": client.total_portfolio_value,
                "num_policies": len(client.policies),
                "policy_types": list(set(p.policy_type.value for p in client.policies)),
            },
            "concerns": [
                {"topic": c.topic, "severity": c.severity.value, "status": c.status.value}
                for c in client.concerns
            ],
            "upcoming_events": [
                {"type": e.event_type.value, "date": str(e.event_date), "description": e.description}
                for e in client.life_events
                if e.event_date >= date.today()
            ],
            "pending_follow_ups": [
                {"commitment": f.commitment, "deadline": str(f.deadline)}
                for f in client.pending_follow_ups
            ],
            "compliance": {
                "last_review": str(client.compliance.last_annual_review) if client.compliance.last_annual_review else None,
                "next_review_due": str(client.compliance.next_review_due) if client.compliance.next_review_due else None,
                "status": client.compliance.review_status,
                "is_overdue": client.has_overdue_review,
            },
            "recent_meetings": [
                {"date": str(n.meeting_date), "summary": n.summary}
                for n in client.meeting_notes[:3]
            ],
            "risk_profile": {
                "attitude": client.risk_profile.attitude_to_risk.value if client.risk_profile else None,
                "capacity": client.risk_profile.capacity_for_loss.value if client.risk_profile else None,
            }
        }
    
    # ============== DAILY BRIEFING ==============
    
    def get_daily_briefing_data(self) -> Dict[str, Any]:
        """
        Get all data needed for advisor's daily briefing
        """
        return {
            "total_clients": self.get_client_count(),
            "reviews_overdue": self.get_clients_review_overdue(),
            "reviews_due_soon": self.get_clients_review_due_soon(30),
            "dormant_90_days": self.get_dormant_clients(90),
            "dormant_180_days": self.get_dormant_clients(180),
            "upcoming_birthdays": self.get_upcoming_birthdays(14),
            "upcoming_events": self.get_upcoming_life_events(14),
            "pending_follow_ups": self.get_clients_with_pending_follow_ups(),
            "overdue_follow_ups": self.get_clients_with_overdue_follow_ups(),
            "active_concerns": self.get_clients_with_active_concerns(),
            "expiring_policies": self.get_policies_expiring_soon(30),
        }
