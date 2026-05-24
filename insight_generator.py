"""Insight Generator agent: synthesises upstream context into commercial intelligence."""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from utils import parse_json_response

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "insight_generator.md"


def run_insight_generator(state: dict) -> dict:
    """
    Generate commercial priorities and pain points from upstream graph state.
    """
    profile = state.get("profile")
    if not profile:
        return {"commercial_priorities": [], "pain_points": []}

    prompt_text = _PROMPT_PATH.read_text()
    human_message = (
        f"## Profile\n{json.dumps(profile, indent=2)}\n\n"
        f"## Research evidence\n{state.get('research_evidence')}\n\n"
        f"## Domain context\n{state.get('domain_context')}\n\n"
        f"## Recent signals\n{json.dumps(state.get('recent_signals'), indent=2)}"
    )

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        max_tokens=6000,
    )
    response = llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(content=human_message),
    ])

    try:
        parsed = parse_json_response(response.content)
    except (json.JSONDecodeError, ValueError):
        parsed = {}

    return {
        "commercial_priorities": parsed.get("commercial_priorities", []),
        "pain_points": parsed.get("pain_points", []),
    }
