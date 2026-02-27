"""
Dismissal Service
Handles persistent storage for dismissed alerts and inactive clients.
Ensures proactive nudges respect user preferences across sessions.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any, Optional


class DismissalService:
    """
    Manages dismissed alerts and inactive clients.
    
    Two dismissal types:
    - Dismissed Alerts: Specific alerts user doesn't want to see
    - Inactive Clients: Clients marked as "not with us anymore" - excluded from ALL alerts
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.dismissals_file = self.data_dir / "dismissals.json"
        
        # In-memory cache
        self._dismissed_alerts: Set[str] = set()
        self._inactive_clients: Set[str] = set()
        self._inactive_client_names: Dict[str, str] = {}  # id -> name for recovery UI
        
        # Load from file
        self._load()
    
    def _load(self):
        """Load dismissals from persistent storage"""
        if self.dismissals_file.exists():
            try:
                with open(self.dismissals_file, 'r') as f:
                    data = json.load(f)
                    self._dismissed_alerts = set(data.get("dismissed_alerts", []))
                    self._inactive_clients = set(data.get("inactive_clients", []))
                    self._inactive_client_names = data.get("inactive_client_names", {})
            except (json.JSONDecodeError, IOError):
                # Start fresh if file is corrupted
                self._dismissed_alerts = set()
                self._inactive_clients = set()
                self._inactive_client_names = {}
    
    def _save(self):
        """Save dismissals to persistent storage"""
        data = {
            "dismissed_alerts": list(self._dismissed_alerts),
            "inactive_clients": list(self._inactive_clients),
            "inactive_client_names": self._inactive_client_names,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.dismissals_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save dismissals: {e}")
    
    # ========== Dismissed Alerts ==========
    
    def dismiss_alert(self, alert_id: str) -> None:
        """Dismiss a specific alert (won't be shown again)"""
        self._dismissed_alerts.add(alert_id)
        self._save()
    
    def undismiss_alert(self, alert_id: str) -> None:
        """Remove an alert from dismissed list"""
        self._dismissed_alerts.discard(alert_id)
        self._save()
    
    def is_alert_dismissed(self, alert_id: str) -> bool:
        """Check if an alert is dismissed"""
        return alert_id in self._dismissed_alerts
    
    def get_dismissed_alerts(self) -> Set[str]:
        """Get all dismissed alert IDs"""
        return self._dismissed_alerts.copy()
    
    def clear_dismissed_alerts(self) -> None:
        """Clear all dismissed alerts (reset)"""
        self._dismissed_alerts.clear()
        self._save()
    
    # ========== Inactive Clients ==========
    
    def mark_client_inactive(self, client_id: str, client_name: str = None) -> None:
        """
        Mark a client as inactive ("not with us anymore").
        They will be excluded from ALL future alerts and nudges.
        """
        self._inactive_clients.add(client_id)
        if client_name:
            self._inactive_client_names[client_id] = client_name
        self._save()
    
    def reactivate_client(self, client_id: str) -> None:
        """Reactivate a client (undo "not with us anymore")"""
        self._inactive_clients.discard(client_id)
        self._inactive_client_names.pop(client_id, None)
        self._save()
    
    def is_client_inactive(self, client_id: str) -> bool:
        """Check if a client is marked as inactive"""
        return client_id in self._inactive_clients
    
    def get_inactive_clients(self) -> Set[str]:
        """Get all inactive client IDs"""
        return self._inactive_clients.copy()
    
    def get_inactive_clients_with_names(self) -> Dict[str, str]:
        """Get inactive clients with their names (for recovery UI)"""
        return self._inactive_client_names.copy()
    
    # ========== Utility Methods ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dismissal statistics"""
        return {
            "dismissed_alerts_count": len(self._dismissed_alerts),
            "inactive_clients_count": len(self._inactive_clients),
            "inactive_client_names": list(self._inactive_client_names.values())
        }
    
    def reset_all(self) -> None:
        """Reset all dismissals (for testing/demo)"""
        self._dismissed_alerts.clear()
        self._inactive_clients.clear()
        self._inactive_client_names.clear()
        self._save()


# Singleton instance
dismissal_service = DismissalService()
