"""
Shared state for the LangGraph pipeline described in SCOPE.md.

Every agent reads from and writes back to this state as the graph progresses.
"""

from typing import Optional, TypedDict


class GraphState(TypedDict):
    user_input: str
    input_type: str
    profile: Optional[dict]
    research_evidence: Optional[str]
    domain_context: Optional[str]
    recent_signals: Optional[list]
    commercial_priorities: Optional[list]
    pain_points: Optional[list]
    conversation_angles: Optional[list]
    outreach_drafts: Optional[dict]
    sources: Optional[list]
    confidence_note: Optional[str]
    error: Optional[str]
