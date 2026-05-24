"""Domain Expert agent: adds consulting-industry context to a parsed profile."""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "domain_expert.md"


def run_domain_expert(state: dict) -> dict:
    """
    Analyse a Parser profile and return consulting-specific domain context.
    """
    profile = state.get("profile")
    if not profile or not profile.get("name"):
        return {"domain_context": "No profile available for domain analysis."}

    prompt_text = _PROMPT_PATH.read_text()
    profile_json = json.dumps(profile, indent=2)
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
    response = llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(content=f"Parsed profile:\n{profile_json}"),
    ])

    return {"domain_context": response.content}
