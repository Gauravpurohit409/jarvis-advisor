"""
Proactive Alerts Service
Detects important events and generates alerts for advisor action
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict
import uuid

from data.schema import (
    Client, Alert, AlertType, AlertPriority,
    FollowUpStatus, ConcernStatus, LifeEventType
)


class AlertsService:
    """
    Scans client data and generates proactive alerts.
    The heart of Jarvis - helping advisors stay ahead of client needs.
    """
    
    def __init__(self):
        self.today = date.today()
        
        # Configuration: How many days ahead to look for various events
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
    
    def generate_all_alerts(self, clients: List[Client]) -> List[Alert]:
        """Generate all alerts for all clients"""
        alerts = []
        
        for client in clients:
            alerts.extend(self._check_birthday(client))
            alerts.extend(self._check_policy_renewals(client))
            alerts.extend(self._check_policy_maturities(client))
            alerts.extend(self._check_follow_ups(client))
            alerts.extend(self._check_annual_review(client))
            alerts.extend(self._check_no_contact(client))
            alerts.extend(self._check_life_events(client))
            alerts.extend(self._check_risk_profile(client))
            alerts.extend(self._check_concerns(client))
            alerts.extend(self._check_retirement(client))
        
        # Sort by priority then by due date
        alerts.sort(key=lambda a: (a.priority_order, a.due_date or date.max))
        
        return alerts
    
    def get_alerts_by_type(self, alerts: List[Alert], alert_type: AlertType) -> List[Alert]:
        """Filter alerts by type"""
        return [a for a in alerts if a.alert_type == alert_type]
    
    def get_alerts_by_priority(self, alerts: List[Alert], priority: AlertPriority) -> List[Alert]:
        """Filter alerts by priority"""
        return [a for a in alerts if a.priority == priority]
    
    def get_alerts_for_client(self, alerts: List[Alert], client_id: str) -> List[Alert]:
        """Get all alerts for a specific client"""
        return [a for a in alerts if a.client_id == client_id]
    
    def get_urgent_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """Get only urgent and high priority alerts"""
        return [a for a in alerts if a.priority in [AlertPriority.URGENT, AlertPriority.HIGH]]
    
    def get_today_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """Get alerts due today"""
        return [a for a in alerts if a.due_date == self.today]
    
    # ========== Alert Detection Methods ==========
    
    def _check_birthday(self, client: Client) -> List[Alert]:
        """Check for upcoming client birthdays"""
        alerts = []
        
        # Client's birthday
        birthday_this_year = client.date_of_birth.replace(year=self.today.year)
        if birthday_this_year < self.today:
            birthday_this_year = birthday_this_year.replace(year=self.today.year + 1)
        
        days_until = (birthday_this_year - self.today).days
        
        if 0 <= days_until <= self.config["birthday_days_ahead"]:
            age = self.today.year - client.date_of_birth.year
            if birthday_this_year.year > self.today.year:
                age += 1
            
            priority = AlertPriority.HIGH if days_until <= 3 else AlertPriority.MEDIUM
            
            alerts.append(Alert(
                id=f"bday-{client.id}-{birthday_this_year.year}",
                client_id=client.id,
                client_name=client.full_name,
                alert_type=AlertType.BIRTHDAY,
                priority=priority,
                title=f"🎂 {client.first_name}'s Birthday" + (" Today!" if days_until == 0 else f" in {days_until} days"),
                description=f"{client.full_name} turns {age} on {birthday_this_year.strftime('%d %B')}. Consider sending a birthday message.",
                due_date=birthday_this_year,
                days_until_due=days_until,
                related_data={
                    "age": age,
                    "email": client.contact_info.email,
                    "phone": client.contact_info.phone
                }
            ))
        
        # Family member birthdays
        for member in client.family_members:
            if member.date_of_birth:
                member_bday = member.date_of_birth.replace(year=self.today.year)
                if member_bday < self.today:
                    member_bday = member_bday.replace(year=self.today.year + 1)
                
                days_until = (member_bday - self.today).days
                
                if 0 <= days_until <= 7:  # Shorter window for family
                    alerts.append(Alert(
                        id=f"fam-bday-{client.id}-{member.name}-{member_bday.year}",
                        client_id=client.id,
                        client_name=client.full_name,
                        alert_type=AlertType.BIRTHDAY,
                        priority=AlertPriority.LOW,
                        title=f"👨‍👩‍👧 {member.name}'s Birthday ({member.relationship})",
                        description=f"{member.name}, {client.first_name}'s {member.relationship}, has a birthday on {member_bday.strftime('%d %B')}.",
                        due_date=member_bday,
                        days_until_due=days_until,
                        related_data={
                            "family_member": member.name,
                            "relationship": member.relationship
                        }
                    ))
        
        return alerts
    
    def _check_policy_renewals(self, client: Client) -> List[Alert]:
        """Check for upcoming policy renewals"""
        alerts = []
        
        for policy in client.policies:
            if policy.renewal_date:
                days_until = (policy.renewal_date - self.today).days
                
                if days_until < 0:
                    # Overdue renewal
                    alerts.append(Alert(
                        id=f"renewal-overdue-{client.id}-{policy.policy_number or policy.policy_type.value}",
                        client_id=client.id,
                        client_name=client.full_name,
                        alert_type=AlertType.POLICY_RENEWAL,
                        priority=AlertPriority.URGENT,
                        title=f"⚠️ Overdue: {policy.policy_type.value.replace('_', ' ').title()} Renewal",
                        description=f"{client.first_name}'s {policy.provider} {policy.policy_type.value.replace('_', ' ')} was due for renewal {abs(days_until)} days ago.",
                        due_date=policy.renewal_date,
                        days_until_due=days_until,
                        related_data={
                            "policy_type": policy.policy_type.value,
                            "provider": policy.provider,
                            "policy_number": policy.policy_number,
                            "current_value": policy.current_value
                        }
                    ))
                elif 0 <= days_until <= self.config["policy_renewal_days_ahead"]:
                    priority = AlertPriority.HIGH if days_until <= 7 else AlertPriority.MEDIUM
                    
                    alerts.append(Alert(
                        id=f"renewal-{client.id}-{policy.policy_number or policy.policy_type.value}",
                        client_id=client.id,
                        client_name=client.full_name,
                        alert_type=AlertType.POLICY_RENEWAL,
                        priority=priority,
                        title=f"📋 {policy.policy_type.value.replace('_', ' ').title()} Renewal in {days_until} days",
                        description=f"{client.first_name}'s {policy.provider} {policy.policy_type.value.replace('_', ' ')} renews on {policy.renewal_date.strftime('%d %B %Y')}.",
                        due_date=policy.renewal_date,
                        days_until_due=days_until,
                        related_data={
                            "policy_type": policy.policy_type.value,
                            "provider": policy.provider,
                            "policy_number": policy.policy_number,
                            "current_value": policy.current_value
                        }
                    ))
        
        return alerts
    
    def _check_policy_maturities(self, client: Client) -> List[Alert]:
        """Check for upcoming policy maturities"""
        alerts = []
        
        for policy in client.policies:
            if policy.maturity_date:
                days_until = (policy.maturity_date - self.today).days
                
                if 0 <= days_until <= self.config["policy_maturity_days_ahead"]:
                    priority = AlertPriority.HIGH if days_until <= 14 else AlertPriority.MEDIUM
                    
                    alerts.append(Alert(
                        id=f"maturity-{client.id}-{policy.policy_number or policy.policy_type.value}",
                        client_id=client.id,
                        client_name=client.full_name,
                        alert_type=AlertType.POLICY_MATURITY,
                        priority=priority,
                        title=f"💰 {policy.policy_type.value.replace('_', ' ').title()} Maturing",
                        description=f"{client.first_name}'s {policy.provider} {policy.policy_type.value.replace('_', ' ')} matures on {policy.maturity_date.strftime('%d %B %Y')}. Current value: £{policy.current_value:,.0f}" if policy.current_value else f"matures on {policy.maturity_date.strftime('%d %B %Y')}.",
                        due_date=policy.maturity_date,
                        days_until_due=days_until,
                        related_data={
                            "policy_type": policy.policy_type.value,
                            "provider": policy.provider,
                            "policy_number": policy.policy_number,
                            "current_value": policy.current_value
                        }
                    ))
        
        return alerts
    
    def _check_follow_ups(self, client: Client) -> List[Alert]:
        """Check for pending and overdue follow-ups"""
        alerts = []
        
        for follow_up in client.follow_ups:
            if follow_up.status != FollowUpStatus.PENDING:
                continue
            
            days_until = (follow_up.deadline - self.today).days
            
            if days_until < 0:
                # Overdue
                alerts.append(Alert(
                    id=f"followup-overdue-{client.id}-{follow_up.commitment[:20]}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.FOLLOW_UP_OVERDUE,
                    priority=AlertPriority.URGENT,
                    title=f"⚠️ Overdue Follow-up: {follow_up.commitment[:40]}...",
                    description=f"You promised {client.first_name}: \"{follow_up.commitment}\" - was due {abs(days_until)} days ago.",
                    due_date=follow_up.deadline,
                    days_until_due=days_until,
                    related_data={
                        "commitment": follow_up.commitment,
                        "notes": follow_up.notes
                    }
                ))
            elif 0 <= days_until <= self.config["follow_up_warning_days"]:
                priority = AlertPriority.HIGH if days_until == 0 else AlertPriority.MEDIUM
                
                alerts.append(Alert(
                    id=f"followup-{client.id}-{follow_up.commitment[:20]}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.FOLLOW_UP_DUE,
                    priority=priority,
                    title=f"📌 Follow-up Due" + (" Today" if days_until == 0 else f" in {days_until} days"),
                    description=f"You promised {client.first_name}: \"{follow_up.commitment}\"",
                    due_date=follow_up.deadline,
                    days_until_due=days_until,
                    related_data={
                        "commitment": follow_up.commitment,
                        "notes": follow_up.notes
                    }
                ))
        
        return alerts
    
    def _check_annual_review(self, client: Client) -> List[Alert]:
        """Check for annual review requirements (FCA Consumer Duty)"""
        alerts = []
        
        if client.compliance.next_review_due:
            days_until = (client.compliance.next_review_due - self.today).days
            
            if days_until < 0:
                # Overdue - compliance issue!
                alerts.append(Alert(
                    id=f"review-overdue-{client.id}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.ANNUAL_REVIEW_OVERDUE,
                    priority=AlertPriority.URGENT,
                    title=f"🚨 Annual Review OVERDUE",
                    description=f"{client.full_name}'s annual review is {abs(days_until)} days overdue. FCA Consumer Duty requires regular reviews.",
                    due_date=client.compliance.next_review_due,
                    days_until_due=days_until,
                    related_data={
                        "last_review": str(client.compliance.last_annual_review) if client.compliance.last_annual_review else None,
                        "portfolio_value": client.total_portfolio_value
                    }
                ))
            elif 0 <= days_until <= self.config["annual_review_warning_days"]:
                priority = AlertPriority.HIGH if days_until <= 7 else AlertPriority.MEDIUM
                
                alerts.append(Alert(
                    id=f"review-{client.id}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.ANNUAL_REVIEW_DUE,
                    priority=priority,
                    title=f"📊 Annual Review Due in {days_until} days",
                    description=f"{client.full_name}'s annual review is coming up on {client.compliance.next_review_due.strftime('%d %B %Y')}.",
                    due_date=client.compliance.next_review_due,
                    days_until_due=days_until,
                    related_data={
                        "last_review": str(client.compliance.last_annual_review) if client.compliance.last_annual_review else None,
                        "portfolio_value": client.total_portfolio_value
                    }
                ))
        
        return alerts
    
    def _check_no_contact(self, client: Client) -> List[Alert]:
        """Check for clients with no recent contact"""
        alerts = []
        
        days_since = client.days_since_last_contact
        
        if days_since and days_since >= self.config["no_contact_days"]:
            priority = AlertPriority.HIGH if days_since >= 180 else AlertPriority.MEDIUM
            
            alerts.append(Alert(
                id=f"no-contact-{client.id}",
                client_id=client.id,
                client_name=client.full_name,
                alert_type=AlertType.NO_CONTACT,
                priority=priority,
                title=f"📞 No Contact for {days_since} days",
                description=f"It's been {days_since} days since last contact with {client.first_name}. Consider reaching out.",
                due_date=self.today,
                days_until_due=0,
                related_data={
                    "days_since_contact": days_since,
                    "email": client.contact_info.email,
                    "phone": client.contact_info.phone,
                    "preferred_method": client.contact_info.preferred_contact_method.value
                }
            ))
        
        return alerts
    
    def _check_life_events(self, client: Client) -> List[Alert]:
        """Check for upcoming life events"""
        alerts = []
        
        for event in client.life_events:
            days_until = (event.event_date - self.today).days
            
            # Upcoming events within 30 days
            if 0 <= days_until <= 30:
                priority = AlertPriority.HIGH if days_until <= 7 else AlertPriority.MEDIUM
                
                event_emoji = {
                    LifeEventType.RETIREMENT: "🎉",
                    LifeEventType.WEDDING: "💒",
                    LifeEventType.BIRTH: "👶",
                    LifeEventType.GRADUATION: "🎓",
                    LifeEventType.HOUSE_PURCHASE: "🏠",
                    LifeEventType.NEW_JOB: "💼",
                    LifeEventType.ANNIVERSARY: "💍",
                }.get(event.event_type, "📅")
                
                alerts.append(Alert(
                    id=f"event-{client.id}-{event.event_type.value}-{event.event_date}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.LIFE_EVENT,
                    priority=priority,
                    title=f"{event_emoji} {event.event_type.value.replace('_', ' ').title()}" + (" Today!" if days_until == 0 else f" in {days_until} days"),
                    description=f"{event.description}",
                    due_date=event.event_date,
                    days_until_due=days_until,
                    related_data={
                        "event_type": event.event_type.value,
                        "related_person": event.related_person
                    }
                ))
        
        return alerts
    
    def _check_risk_profile(self, client: Client) -> List[Alert]:
        """Check if risk profile is stale"""
        alerts = []
        
        if client.risk_profile and client.risk_profile.last_assessed:
            years_since = (self.today - client.risk_profile.last_assessed).days / 365
            
            if years_since >= self.config["risk_profile_stale_years"]:
                alerts.append(Alert(
                    id=f"risk-stale-{client.id}",
                    client_id=client.id,
                    client_name=client.full_name,
                    alert_type=AlertType.RISK_PROFILE_STALE,
                    priority=AlertPriority.MEDIUM,
                    title=f"📈 Risk Profile Needs Update",
                    description=f"{client.first_name}'s risk profile was last assessed {int(years_since * 12)} months ago. Consider reassessing.",
                    due_date=self.today,
                    days_until_due=0,
                    related_data={
                        "last_assessed": str(client.risk_profile.last_assessed),
                        "current_attitude": client.risk_profile.attitude_to_risk.value
                    }
                ))
        
        return alerts
    
    def _check_concerns(self, client: Client) -> List[Alert]:
        """Check for high-priority active concerns"""
        alerts = []
        
        for concern in client.concerns:
            if concern.status == ConcernStatus.ACTIVE and concern.severity.value == "high":
                # Check if concern hasn't been discussed recently
                days_since_discussed = None
                if concern.last_discussed:
                    days_since_discussed = (self.today - concern.last_discussed).days
                
                if not concern.last_discussed or days_since_discussed > 30:
                    alerts.append(Alert(
                        id=f"concern-{client.id}-{concern.topic[:20]}",
                        client_id=client.id,
                        client_name=client.full_name,
                        alert_type=AlertType.CONCERN_NEEDS_ATTENTION,
                        priority=AlertPriority.HIGH,
                        title=f"😟 High Concern: {concern.topic}",
                        description=f"{client.first_name} has an active concern about {concern.topic}: {concern.details[:100]}...",
                        due_date=self.today,
                        days_until_due=0,
                        related_data={
                            "topic": concern.topic,
                            "details": concern.details,
                            "date_raised": str(concern.date_raised),
                            "last_discussed": str(concern.last_discussed) if concern.last_discussed else None
                        }
                    ))
        
        return alerts
    
    def _check_retirement(self, client: Client) -> List[Alert]:
        """Check for clients approaching retirement"""
        alerts = []
        
        # Assume retirement age of 67 (UK state pension age)
        retirement_age = 67
        years_to_retirement = retirement_age - client.age
        
        if 0 < years_to_retirement <= self.config["retirement_warning_years"]:
            alerts.append(Alert(
                id=f"retirement-{client.id}",
                client_id=client.id,
                client_name=client.full_name,
                alert_type=AlertType.RETIREMENT_APPROACHING,
                priority=AlertPriority.HIGH,
                title=f"🎯 Retirement Approaching ({years_to_retirement} years)",
                description=f"{client.first_name} will reach state pension age ({retirement_age}) in {years_to_retirement} years. Review retirement planning.",
                due_date=client.date_of_birth.replace(year=client.date_of_birth.year + retirement_age),
                days_until_due=years_to_retirement * 365,
                related_data={
                    "current_age": client.age,
                    "retirement_age": retirement_age,
                    "years_remaining": years_to_retirement,
                    "portfolio_value": client.total_portfolio_value
                }
            ))
        
        return alerts
    
    # ========== Summary Methods ==========
    
    def get_alert_summary(self, alerts: List[Alert]) -> Dict:
        """Get a summary of all alerts for dashboard display"""
        return {
            "total": len(alerts),
            "urgent": len([a for a in alerts if a.priority == AlertPriority.URGENT]),
            "high": len([a for a in alerts if a.priority == AlertPriority.HIGH]),
            "medium": len([a for a in alerts if a.priority == AlertPriority.MEDIUM]),
            "low": len([a for a in alerts if a.priority == AlertPriority.LOW]),
            "by_type": self._count_by_type(alerts),
            "due_today": len([a for a in alerts if a.due_date == self.today]),
            "overdue": len([a for a in alerts if a.due_date and a.due_date < self.today])
        }
    
    def _count_by_type(self, alerts: List[Alert]) -> Dict[str, int]:
        """Count alerts by type"""
        counts = {}
        for alert in alerts:
            type_name = alert.alert_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def generate_daily_briefing(self, alerts: List[Alert]) -> str:
        """Generate a text summary for the daily briefing"""
        summary = self.get_alert_summary(alerts)
        
        briefing = f"""
## 📊 Daily Briefing - {self.today.strftime('%A, %d %B %Y')}

### Overview
- **Total Alerts:** {summary['total']}
- **Urgent:** {summary['urgent']} | **High:** {summary['high']} | **Medium:** {summary['medium']} | **Low:** {summary['low']}
- **Due Today:** {summary['due_today']} | **Overdue:** {summary['overdue']}

"""
        
        # Urgent items
        urgent = [a for a in alerts if a.priority == AlertPriority.URGENT]
        if urgent:
            briefing += "### 🚨 Urgent Action Required\n"
            for alert in urgent[:5]:
                briefing += f"- **{alert.client_name}**: {alert.title}\n"
            briefing += "\n"
        
        # Today's items
        today_alerts = [a for a in alerts if a.due_date == self.today]
        if today_alerts:
            briefing += "### 📅 Due Today\n"
            for alert in today_alerts[:5]:
                briefing += f"- **{alert.client_name}**: {alert.title}\n"
            briefing += "\n"
        
        # Upcoming this week
        week_alerts = [a for a in alerts if a.due_date and 0 < (a.due_date - self.today).days <= 7]
        if week_alerts:
            briefing += "### 📆 This Week\n"
            for alert in week_alerts[:5]:
                briefing += f"- **{alert.client_name}**: {alert.title}\n"
        
        return briefing


# Singleton instance
alerts_service = AlertsService()
