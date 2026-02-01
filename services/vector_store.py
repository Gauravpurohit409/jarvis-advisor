"""
Vector Store Service
ChromaDB-based semantic search for client data
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import date, datetime

# Import config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CHROMA_PERSIST_DIR


class VectorStoreService:
    """
    ChromaDB vector store for semantic search across client data.
    Enables natural language queries like:
    - "clients worried about retirement"
    - "who has inheritance tax concerns"
    - "clients with DB pensions"
    """
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or CHROMA_PERSIST_DIR
        self.client = None
        self.collection = None
        self._initialized = False
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persist directory if needed
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for client data
            self.collection = self.client.get_or_create_collection(
                name="client_data",
                metadata={"description": "Financial advisor client information"}
            )
            
            self._initialized = True
            print(f"Vector store initialized. Collection has {self.collection.count()} documents.")
            
        except ImportError:
            print("ChromaDB not installed. Run: pip install chromadb")
            self._initialized = False
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if vector store is available"""
        return self._initialized and self.collection is not None
    
    def index_client(self, client) -> bool:
        """
        Index a single client's data for semantic search.
        Creates multiple documents per client for different aspects.
        """
        if not self.is_available():
            return False
        
        try:
            documents = []
            metadatas = []
            ids = []
            
            # 1. Client Overview Document
            overview = self._create_overview_document(client)
            documents.append(overview)
            metadatas.append({
                "client_id": client.id,
                "doc_type": "overview",
                "client_name": client.full_name
            })
            ids.append(f"{client.id}_overview")
            
            # 2. Concerns Document (if any)
            if client.concerns:
                concerns_doc = self._create_concerns_document(client)
                documents.append(concerns_doc)
                metadatas.append({
                    "client_id": client.id,
                    "doc_type": "concerns",
                    "client_name": client.full_name
                })
                ids.append(f"{client.id}_concerns")
            
            # 3. Policies Document
            if client.policies:
                policies_doc = self._create_policies_document(client)
                documents.append(policies_doc)
                metadatas.append({
                    "client_id": client.id,
                    "doc_type": "policies",
                    "client_name": client.full_name
                })
                ids.append(f"{client.id}_policies")
            
            # 4. Family & Life Events Document
            if client.family_members or client.life_events:
                family_doc = self._create_family_document(client)
                documents.append(family_doc)
                metadatas.append({
                    "client_id": client.id,
                    "doc_type": "family",
                    "client_name": client.full_name
                })
                ids.append(f"{client.id}_family")
            
            # 5. Meeting Notes Document (if any)
            if client.meeting_notes:
                notes_doc = self._create_notes_document(client)
                documents.append(notes_doc)
                metadatas.append({
                    "client_id": client.id,
                    "doc_type": "notes",
                    "client_name": client.full_name
                })
                ids.append(f"{client.id}_notes")
            
            # 6. Follow-ups Document (if any)
            if client.follow_ups:
                followups_doc = self._create_followups_document(client)
                documents.append(followups_doc)
                metadatas.append({
                    "client_id": client.id,
                    "doc_type": "followups",
                    "client_name": client.full_name
                })
                ids.append(f"{client.id}_followups")
            
            # Upsert all documents for this client
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
            
        except Exception as e:
            print(f"Error indexing client {client.id}: {e}")
            return False
    
    def index_all_clients(self, clients: List) -> int:
        """Index all clients. Returns count of successfully indexed."""
        if not self.is_available():
            return 0
        
        success_count = 0
        for client in clients:
            if self.index_client(client):
                success_count += 1
        
        print(f"Indexed {success_count}/{len(clients)} clients. Total documents: {self.collection.count()}")
        return success_count
    
    def search(self, query: str, n_results: int = 5, doc_type: str = None) -> List[Dict[str, Any]]:
        """
        Semantic search across client data.
        
        Args:
            query: Natural language query
            n_results: Maximum results to return
            doc_type: Optional filter by document type (overview, concerns, policies, etc.)
        
        Returns:
            List of matching documents with metadata and distances
        """
        if not self.is_available():
            return []
        
        try:
            where_filter = None
            if doc_type:
                where_filter = {"doc_type": doc_type}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    formatted.append({
                        "id": doc_id,
                        "document": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_clients(self, query: str, n_results: int = 5) -> List[str]:
        """
        Search and return unique client IDs matching the query.
        """
        results = self.search(query, n_results=n_results * 2)  # Get more to dedupe
        
        seen_clients = set()
        client_ids = []
        
        for result in results:
            client_id = result.get('metadata', {}).get('client_id')
            if client_id and client_id not in seen_clients:
                seen_clients.add(client_id)
                client_ids.append(client_id)
                if len(client_ids) >= n_results:
                    break
        
        return client_ids
    
    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """
        Get relevant context for LLM based on query.
        Returns formatted string of relevant client information.
        """
        results = self.search(query, n_results=n_results)
        
        if not results:
            return ""
        
        context_parts = ["--- RELEVANT CLIENT INFORMATION ---"]
        
        for result in results:
            client_name = result.get('metadata', {}).get('client_name', 'Unknown')
            doc_type = result.get('metadata', {}).get('doc_type', 'info')
            document = result.get('document', '')
            
            context_parts.append(f"\n[{client_name} - {doc_type}]")
            context_parts.append(document)
        
        return "\n".join(context_parts)
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        if self.is_available():
            # Delete and recreate collection
            self.client.delete_collection("client_data")
            self.collection = self.client.create_collection(
                name="client_data",
                metadata={"description": "Financial advisor client information"}
            )
            print("Collection cleared.")
    
    # ============== Document Creation Helpers ==============
    
    def _create_overview_document(self, client) -> str:
        """Create searchable overview document for a client"""
        parts = [
            f"Client: {client.full_name}",
            f"Age: {client.age}" if client.age else "",
            f"Occupation: {client.occupation}" if client.occupation else "",
            f"Employer: {client.employer}" if client.employer else "",
            f"Annual Income: £{client.annual_income:,.0f}" if client.annual_income else "",
            f"Marital Status: {client.marital_status}" if client.marital_status else "",
            f"Location: {client.contact_info.address.city}, {client.contact_info.address.county}" if client.contact_info and client.contact_info.address else "",
            f"Portfolio Value: £{client.total_portfolio_value:,.0f}" if client.total_portfolio_value else "",
            f"Client Since: {client.client_since}" if client.client_since else "",
            f"Advisor: {client.assigned_advisor}" if client.assigned_advisor else "",
            f"Tags: {', '.join(client.tags)}" if client.tags else "",
            f"Notes: {client.notes}" if client.notes else ""
        ]
        
        if client.risk_profile:
            parts.append(f"Risk Attitude: {client.risk_profile.attitude_to_risk.value}")
            if client.risk_profile.notes:
                parts.append(f"Risk Notes: {client.risk_profile.notes}")
        
        return "\n".join([p for p in parts if p])
    
    def _create_concerns_document(self, client) -> str:
        """Create searchable concerns document"""
        parts = [f"Concerns for {client.full_name}:"]
        
        for concern in client.concerns:
            concern_text = f"- {concern.topic}"
            if concern.details:
                concern_text += f": {concern.details}"
            concern_text += f" (Severity: {concern.severity.value}, Status: {concern.status.value})"
            parts.append(concern_text)
        
        # Add keywords for common concern themes
        concern_topics = [c.topic.lower() for c in client.concerns]
        keywords = []
        
        if any('retire' in t for t in concern_topics):
            keywords.extend(['retirement', 'pension', 'stopping work'])
        if any('tax' in t or 'iht' in t for t in concern_topics):
            keywords.extend(['inheritance tax', 'IHT', 'estate planning', 'death duties'])
        if any('care' in t for t in concern_topics):
            keywords.extend(['care home', 'long term care', 'elderly care', 'care costs'])
        if any('protection' in t or 'insurance' in t for t in concern_topics):
            keywords.extend(['life insurance', 'critical illness', 'income protection', 'protection gap'])
        if any('income' in t or 'money' in t for t in concern_topics):
            keywords.extend(['running out of money', 'income sustainability', 'financial security'])
        
        if keywords:
            parts.append(f"Related topics: {', '.join(set(keywords))}")
        
        return "\n".join(parts)
    
    def _create_policies_document(self, client) -> str:
        """Create searchable policies document"""
        parts = [f"Policies and investments for {client.full_name}:"]
        
        pension_total = 0
        isa_total = 0
        
        for policy in client.policies:
            policy_text = f"- {policy.policy_type.value}: {policy.provider}"
            if policy.current_value:
                policy_text += f" (£{policy.current_value:,.0f})"
                if policy.policy_type.value == 'pension':
                    pension_total += policy.current_value
                elif policy.policy_type.value == 'isa':
                    isa_total += policy.current_value
            if policy.notes:
                policy_text += f" - {policy.notes}"
            parts.append(policy_text)
        
        # Add summary keywords
        policy_types = [p.policy_type.value for p in client.policies]
        keywords = []
        
        if 'pension' in policy_types:
            keywords.extend(['pension', 'retirement savings', 'SIPP', 'workplace pension'])
            # Check for DB pension
            for p in client.policies:
                if p.notes and ('DB' in p.notes or 'Defined Benefit' in p.notes or 'Final Salary' in p.notes):
                    keywords.extend(['defined benefit', 'DB pension', 'final salary'])
                    break
        if 'isa' in policy_types:
            keywords.extend(['ISA', 'tax-free savings', 'stocks and shares ISA'])
        if 'life_insurance' in policy_types:
            keywords.extend(['life insurance', 'life cover', 'protection'])
        
        parts.append(f"Total pension: £{pension_total:,.0f}")
        parts.append(f"Total ISA: £{isa_total:,.0f}")
        
        if keywords:
            parts.append(f"Related topics: {', '.join(set(keywords))}")
        
        return "\n".join(parts)
    
    def _create_family_document(self, client) -> str:
        """Create searchable family and life events document"""
        parts = [f"Family and life events for {client.full_name}:"]
        
        # Family members
        if client.family_members:
            parts.append("Family:")
            for member in client.family_members:
                member_text = f"- {member.name} ({member.relationship})"
                if member.notes:
                    member_text += f": {member.notes}"
                parts.append(member_text)
        
        # Life events
        if client.life_events:
            parts.append("Upcoming life events:")
            for event in client.life_events:
                event_text = f"- {event.event_date}: {event.description}"
                if event.related_person:
                    event_text += f" (related to {event.related_person})"
                parts.append(event_text)
        
        # Add keywords
        keywords = []
        if any(m.relationship == 'child' for m in client.family_members):
            keywords.extend(['children', 'kids', 'family'])
        if any(m.relationship == 'grandchild' for m in client.family_members):
            keywords.extend(['grandchildren', 'grandkids'])
        if any(m.relationship == 'spouse' for m in client.family_members):
            keywords.extend(['married', 'spouse', 'partner', 'couple'])
        
        # Check life events for keywords
        for event in client.life_events:
            desc_lower = event.description.lower()
            if 'university' in desc_lower or 'school' in desc_lower:
                keywords.extend(['education', 'university', 'school fees'])
            if 'wedding' in desc_lower:
                keywords.extend(['wedding', 'marriage'])
            if 'retire' in desc_lower:
                keywords.extend(['retirement'])
            if 'birthday' in desc_lower:
                keywords.extend(['birthday', 'milestone'])
        
        if keywords:
            parts.append(f"Related topics: {', '.join(set(keywords))}")
        
        return "\n".join(parts)
    
    def _create_notes_document(self, client) -> str:
        """Create searchable meeting notes document"""
        parts = [f"Meeting notes for {client.full_name}:"]
        
        for note in client.meeting_notes[:3]:  # Last 3 meetings
            parts.append(f"\nMeeting on {note.meeting_date}:")
            if note.summary:
                parts.append(f"Summary: {note.summary}")
            if note.key_points:
                parts.append("Key points: " + "; ".join(note.key_points[:5]))
            if note.concerns_raised:
                parts.append("Concerns discussed: " + ", ".join(note.concerns_raised))
        
        return "\n".join(parts)
    
    def _create_followups_document(self, client) -> str:
        """Create searchable follow-ups document"""
        parts = [f"Follow-up commitments for {client.full_name}:"]
        
        for followup in client.follow_ups:
            status_emoji = "✅" if followup.status.value == "completed" else "⏰" if followup.status.value == "overdue" else "📋"
            parts.append(f"{status_emoji} {followup.commitment}")
            parts.append(f"   Deadline: {followup.deadline} | Status: {followup.status.value}")
        
        # Add keywords for follow-up types
        all_commitments = " ".join([f.commitment.lower() for f in client.follow_ups])
        keywords = []
        
        if 'insurance' in all_commitments or 'protection' in all_commitments or 'cover' in all_commitments:
            keywords.append('protection review')
        if 'pension' in all_commitments:
            keywords.append('pension planning')
        if 'tax' in all_commitments:
            keywords.append('tax planning')
        if 'will' in all_commitments or 'lpa' in all_commitments or 'estate' in all_commitments:
            keywords.append('estate planning')
        
        if keywords:
            parts.append(f"Related topics: {', '.join(set(keywords))}")
        
        return "\n".join(parts)


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStoreService:
    """Get or create singleton vector store instance"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    return _vector_store_instance
