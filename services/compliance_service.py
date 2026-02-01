"""
FCA Consumer Duty Compliance Service
Tracks regulatory requirements and helps advisors demonstrate value
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum

from data.schema import Client, ComplianceRecord


class ComplianceStatus(str, Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    NON_COMPLIANT = "non_compliant"


class ConsumerDutyPillar(str, Enum):
    """FCA Consumer Duty four outcomes"""
    PRODUCTS_SERVICES = "products_services"  # Products and services
    PRICE_VALUE = "price_value"              # Price and value
    CONSUMER_UNDERSTANDING = "consumer_understanding"  # Consumer understanding
    CONSUMER_SUPPORT = "consumer_support"    # Consumer support


class ComplianceService:
    """
    FCA Consumer Duty Compliance Tracking
    
    The Consumer Duty requires firms to:
    1. Act in good faith towards retail customers
    2. Avoid causing foreseeable harm
    3. Enable and support customers to pursue their financial objectives
    
    Four Outcomes:
    - Products and Services: Designed for target market needs
    - Price and Value: Fair value for products/services
    - Consumer Understanding: Clear communications
    - Consumer Support: Accessible, responsive support
    """
    
    def __init__(self):
        self.today = date.today()
        
        # Compliance thresholds
        self.config = {
            "annual_review_max_months": 12,
            "risk_profile_max_months": 12,
            "suitability_max_months": 24,
            "contact_min_frequency_days": 180,
        }
    
    def get_client_compliance_score(self, client: Client) -> Dict:
        """
        Calculate comprehensive compliance score for a client
        Returns score out of 100 with breakdown
        """
        scores = {
            "annual_review": self._score_annual_review(client),
            "risk_profile": self._score_risk_profile(client),
            "suitability": self._score_suitability(client),
            "contact_frequency": self._score_contact_frequency(client),
            "documentation": self._score_documentation(client),
            "value_demonstrated": self._score_value_demonstrated(client),
        }
        
        # Weighted average
        weights = {
            "annual_review": 25,
            "risk_profile": 20,
            "suitability": 20,
            "contact_frequency": 15,
            "documentation": 10,
            "value_demonstrated": 10,
        }
        
        total_score = sum(scores[k] * weights[k] / 100 for k in scores)
        
        # Determine overall status
        if total_score >= 80:
            status = ComplianceStatus.COMPLIANT
        elif total_score >= 60:
            status = ComplianceStatus.AT_RISK
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        return {
            "overall_score": round(total_score, 1),
            "status": status,
            "breakdown": scores,
            "weights": weights,
            "issues": self._identify_issues(client, scores),
            "recommendations": self._generate_recommendations(client, scores)
        }
    
    def _score_annual_review(self, client: Client) -> int:
        """Score annual review compliance (0-100)"""
        if not client.compliance.last_annual_review:
            return 0
        
        months_since = (self.today - client.compliance.last_annual_review).days / 30
        
        if months_since <= 10:
            return 100
        elif months_since <= 12:
            return 80
        elif months_since <= 14:
            return 50
        else:
            return 20
    
    def _score_risk_profile(self, client: Client) -> int:
        """Score risk profile currency (0-100)"""
        if not client.risk_profile or not client.risk_profile.last_assessed:
            return 0
        
        months_since = (self.today - client.risk_profile.last_assessed).days / 30
        
        if months_since <= 10:
            return 100
        elif months_since <= 12:
            return 80
        elif months_since <= 18:
            return 50
        else:
            return 20
    
    def _score_suitability(self, client: Client) -> int:
        """Score suitability confirmation (0-100)"""
        if not client.compliance.suitability_confirmed:
            return 30  # Base score if never confirmed
        
        if not client.compliance.suitability_date:
            return 50
        
        months_since = (self.today - client.compliance.suitability_date).days / 30
        
        if months_since <= 12:
            return 100
        elif months_since <= 24:
            return 70
        else:
            return 40
    
    def _score_contact_frequency(self, client: Client) -> int:
        """Score client contact frequency (0-100)"""
        days_since = client.days_since_last_contact
        
        if days_since is None:
            return 30
        
        if days_since <= 60:
            return 100
        elif days_since <= 90:
            return 80
        elif days_since <= 180:
            return 60
        else:
            return 30
    
    def _score_documentation(self, client: Client) -> int:
        """Score documentation completeness (0-100)"""
        score = 0
        
        # Has meeting notes
        if client.meeting_notes:
            score += 30
            # Recent meeting notes
            latest = max(n.meeting_date for n in client.meeting_notes)
            if (self.today - latest).days <= 180:
                score += 20
        
        # Has policies documented
        if client.policies:
            score += 25
        
        # Has family info
        if client.family_members:
            score += 15
        
        # Has concerns documented
        if client.concerns:
            score += 10
        
        return min(score, 100)
    
    def _score_value_demonstrated(self, client: Client) -> int:
        """Score value demonstration (0-100)"""
        if not client.compliance.value_delivered:
            return 20
        
        # Score based on number of value items documented
        count = len(client.compliance.value_delivered)
        
        if count >= 5:
            return 100
        elif count >= 3:
            return 80
        elif count >= 1:
            return 60
        else:
            return 20
    
    def _identify_issues(self, client: Client, scores: Dict) -> List[str]:
        """Identify specific compliance issues"""
        issues = []
        
        if scores["annual_review"] < 50:
            issues.append("Annual review overdue or never completed")
        
        if scores["risk_profile"] < 50:
            issues.append("Risk profile needs updating")
        
        if scores["suitability"] < 50:
            issues.append("Suitability confirmation required")
        
        if scores["contact_frequency"] < 60:
            issues.append("Insufficient client contact")
        
        if scores["documentation"] < 50:
            issues.append("Documentation incomplete")
        
        if scores["value_demonstrated"] < 50:
            issues.append("Need to document value delivered")
        
        return issues
    
    def _generate_recommendations(self, client: Client, scores: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if scores["annual_review"] < 80:
            recommendations.append(f"Schedule annual review with {client.first_name}")
        
        if scores["risk_profile"] < 80:
            recommendations.append("Reassess risk profile and attitude to risk")
        
        if scores["suitability"] < 80:
            recommendations.append("Review and confirm suitability of current arrangements")
        
        if scores["contact_frequency"] < 80:
            recommendations.append("Reach out to maintain regular contact")
        
        if scores["value_demonstrated"] < 80:
            recommendations.append("Document specific value delivered to client")
        
        return recommendations
    
    def get_portfolio_compliance_summary(self, clients: List[Client]) -> Dict:
        """Get compliance summary across all clients"""
        if not clients:
            return {"error": "No clients"}
        
        scores = [self.get_client_compliance_score(c) for c in clients]
        
        compliant = sum(1 for s in scores if s["status"] == ComplianceStatus.COMPLIANT)
        at_risk = sum(1 for s in scores if s["status"] == ComplianceStatus.AT_RISK)
        non_compliant = sum(1 for s in scores if s["status"] == ComplianceStatus.NON_COMPLIANT)
        
        avg_score = sum(s["overall_score"] for s in scores) / len(scores)
        
        # Find lowest scoring clients
        client_scores = [(c, self.get_client_compliance_score(c)) for c in clients]
        client_scores.sort(key=lambda x: x[1]["overall_score"])
        
        return {
            "total_clients": len(clients),
            "average_score": round(avg_score, 1),
            "compliant": compliant,
            "at_risk": at_risk,
            "non_compliant": non_compliant,
            "compliance_rate": round(compliant / len(clients) * 100, 1),
            "lowest_scoring": client_scores[:5],  # Bottom 5
            "common_issues": self._get_common_issues(scores),
        }
    
    def _get_common_issues(self, scores: List[Dict]) -> Dict[str, int]:
        """Count frequency of each issue type"""
        issue_counts = {}
        for score in scores:
            for issue in score["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        return dict(sorted(issue_counts.items(), key=lambda x: -x[1]))
    
    def get_consumer_duty_report(self, clients: List[Client]) -> str:
        """Generate a Consumer Duty compliance report"""
        summary = self.get_portfolio_compliance_summary(clients)
        
        report = f"""
# FCA Consumer Duty Compliance Report
**Generated:** {self.today.strftime('%d %B %Y')}

## Executive Summary
- **Overall Compliance Rate:** {summary['compliance_rate']}%
- **Average Compliance Score:** {summary['average_score']}/100
- **Total Clients:** {summary['total_clients']}

## Client Status Breakdown
| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Compliant | {summary['compliant']} | {round(summary['compliant']/summary['total_clients']*100, 1)}% |
| ⚠️ At Risk | {summary['at_risk']} | {round(summary['at_risk']/summary['total_clients']*100, 1)}% |
| ❌ Non-Compliant | {summary['non_compliant']} | {round(summary['non_compliant']/summary['total_clients']*100, 1)}% |

## Common Issues
"""
        for issue, count in summary['common_issues'].items():
            report += f"- {issue}: {count} clients\n"
        
        report += "\n## Priority Actions\n"
        for client, score in summary['lowest_scoring'][:5]:
            report += f"- **{client.full_name}** (Score: {score['overall_score']}): {', '.join(score['issues'][:2])}\n"
        
        return report
    
    def log_value_delivered(self, client: Client, value_description: str) -> Client:
        """Log a value item delivered to client"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        entry = f"[{timestamp}] {value_description}"
        client.compliance.value_delivered.append(entry)
        return client
    
    def generate_value_evidence(self, client: Client) -> List[str]:
        """Generate evidence of value delivered for a client"""
        evidence = []
        
        # Meeting frequency
        if client.meeting_notes:
            meetings_last_year = [
                m for m in client.meeting_notes 
                if (self.today - m.meeting_date).days <= 365
            ]
            if meetings_last_year:
                evidence.append(f"Conducted {len(meetings_last_year)} review meeting(s) in the past year")
        
        # Risk management
        if client.risk_profile:
            evidence.append(f"Risk profile maintained and last assessed {client.risk_profile.last_assessed}")
        
        # Concern handling
        addressed_concerns = [c for c in client.concerns if c.status.value == "addressed"]
        if addressed_concerns:
            evidence.append(f"Addressed {len(addressed_concerns)} client concern(s)")
        
        # Follow-up completion
        completed_followups = [f for f in client.follow_ups if f.status.value == "completed"]
        if completed_followups:
            evidence.append(f"Completed {len(completed_followups)} follow-up commitment(s)")
        
        # Policy reviews
        if client.policies:
            evidence.append(f"Managing {len(client.policies)} financial product(s)")
        
        # Logged value items
        if client.compliance.value_delivered:
            for item in client.compliance.value_delivered[-3:]:
                evidence.append(item)
        
        return evidence


# Singleton instance
compliance_service = ComplianceService()
