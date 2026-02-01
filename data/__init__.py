"""
Data module for Jarvis
Contains schemas and mock data
"""

from .schema import (
    Client,
    ClientDatabase,
    ContactMethod,
    RiskAttitude,
    PolicyType,
    ConcernSeverity,
    ConcernStatus,
    FollowUpStatus,
    LifeEventType,
    FamilyMember,
    LifeEvent,
    Concern,
    Policy,
    RiskProfile,
    MeetingNote,
    FollowUp,
    Interaction,
    ComplianceRecord,
    Address,
    ContactInfo,
)

__all__ = [
    "Client",
    "ClientDatabase",
    "ContactMethod",
    "RiskAttitude",
    "PolicyType",
    "ConcernSeverity",
    "ConcernStatus",
    "FollowUpStatus",
    "LifeEventType",
    "FamilyMember",
    "LifeEvent",
    "Concern",
    "Policy",
    "RiskProfile",
    "MeetingNote",
    "FollowUp",
    "Interaction",
    "ComplianceRecord",
    "Address",
    "ContactInfo",
]
