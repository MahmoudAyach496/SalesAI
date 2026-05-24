"""
Pydantic schema for the AI Sales Intelligence Assistant output.
This is the contract every agent contributes to.
See SCOPE.md section 3 for the source-of-truth definition.
"""

from typing import Literal, List
from pydantic import BaseModel, Field


class Profile(BaseModel):
    name: str = Field(..., description="Full name of the person.")
    current_role: str = Field(..., description="Current job title.")
    current_firm: str = Field(..., description="Current employer or firm name.")
    firm_tier: Literal["MBB", "Big 4", "Tier 2", "Boutique", "In-house", "Other"] = Field(
        ..., description="Tier classification of the firm."
    )
    seniority: Literal[
        "Analyst", "Consultant", "Manager", "Senior Manager",
        "Director", "Principal", "Partner", "C-level", "Unknown"
    ] = Field(..., description="Seniority level on the consulting career ladder.")
    years_in_role_estimate: str = Field(
        ..., description="Rough estimate of time in current role (e.g. '~2 years', '6 months')."
    )
    career_summary: str = Field(
        ..., description="2-3 sentence narrative covering career arc and key context."
    )


class CommercialPriority(BaseModel):
    priority: str = Field(..., description="A likely commercial priority for this person.")
    rationale: str = Field(..., description="Why this priority was inferred — cite signals or domain norms.")
    confidence: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence level based on evidence quality."
    )


class PainPoint(BaseModel):
    pain_point: str = Field(..., description="A likely professional pain point for this person.")
    rationale: str = Field(..., description="Why this pain point was inferred — cite signals or domain norms.")
    confidence: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence level based on evidence quality."
    )


class ConversationAngle(BaseModel):
    angle: str = Field(..., description="A specific angle or hook to open a conversation with this person.")
    why_it_works: str = Field(..., description="Why this angle is likely to resonate given their role and context.")


class OutreachDrafts(BaseModel):
    warm_referral: str = Field(
        ..., description="Draft outreach message assuming a mutual connection. Max 80 words."
    )
    cold_value_first: str = Field(
        ..., description="Cold outreach leading with a relevant insight or value proposition. Max 80 words."
    )
    event_trigger: str = Field(
        ..., description="Outreach triggered by a recent signal (news, move, post). Max 80 words."
    )


class RecentSignal(BaseModel):
    signal: str = Field(..., description="Description of the signal (news item, post, leadership move, etc.).")
    date: str = Field(..., description="Date of the signal in YYYY-MM-DD format, or an approximation.")
    source_url: str = Field(..., description="URL where the signal was found.")
    implication: str = Field(..., description="What this signal implies commercially for the outreach.")


class Source(BaseModel):
    url: str = Field(..., description="URL of the source used.")
    used_for: str = Field(..., description="Which part of the intelligence card this source supports.")


class IntelligenceCard(BaseModel):
    profile: Profile = Field(..., description="Structured profile of the person.")
    commercial_priorities: List[CommercialPriority] = Field(
        ..., description="Likely commercial priorities inferred from profile and context."
    )
    pain_points: List[PainPoint] = Field(
        ..., description="Likely professional pain points inferred from profile and context."
    )
    conversation_angles: List[ConversationAngle] = Field(
        ..., description="Specific angles a recruiter can use to open a relevant conversation."
    )
    outreach_drafts: OutreachDrafts = Field(
        ..., description="Three ready-to-send outreach message drafts tailored to this person."
    )
    recent_signals: List[RecentSignal] = Field(
        ..., description="Recent public signals about this person or their firm."
    )
    sources: List[Source] = Field(
        ..., description="All sources used to build this intelligence card."
    )
    confidence_note: str = Field(
        ..., description="Overall caveat on data quality — e.g. limited public footprint, unverified claims."
    )
