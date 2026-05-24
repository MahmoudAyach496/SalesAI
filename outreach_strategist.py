"""Outreach Strategist agent: creates recruiter-ready angles and messages."""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from utils import parse_json_response

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "outreach_strategist.md"

_EMPTY_DRAFTS = {
    "warm_referral": "",
    "cold_value_first": "",
    "event_trigger": "",
}


def run_outreach_strategist(state: dict) -> dict:
    """
    Generate conversation angles, outreach drafts, and a confidence note.
    """
    profile = state.get("profile")
    if not profile:
        return {
            "conversation_angles": [],
            "outreach_drafts": _EMPTY_DRAFTS,
            "confidence_note": "No profile available.",
        }

    prompt_text = _PROMPT_PATH.read_text()
    human_message = (
        f"## Profile\n{json.dumps(profile, indent=2)}\n\n"
        f"## Research evidence\n{state.get('research_evidence')}\n\n"
        f"## Domain context\n{state.get('domain_context')}\n\n"
        f"## Recent signals\n{json.dumps(state.get('recent_signals'), indent=2)}\n\n"
        f"## Commercial priorities\n{json.dumps(state.get('commercial_priorities'), indent=2)}\n\n"
        f"## Pain points\n{json.dumps(state.get('pain_points'), indent=2)}"
    )

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.3)
    response = llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(content=human_message),
    ])

    try:
        parsed = parse_json_response(response.content)
    except (json.JSONDecodeError, ValueError):
        parsed = {}

    return {
        "conversation_angles": parsed.get("conversation_angles", []),
        "outreach_drafts": parsed.get("outreach_drafts", _EMPTY_DRAFTS),
        "confidence_note": parsed.get("confidence_note", ""),
    }
