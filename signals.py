"""Signals agent: scans recent news for commercial trigger events."""

import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from utils import parse_json_response

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "signals.md"
_MAX_EVIDENCE_CHARS = 3000


def run_signals(state: dict) -> dict:
    """
    Find recent trigger events for the parsed profile's person or firm.
    """
    profile = state.get("profile")
    if not profile or not profile.get("name"):
        return {"recent_signals": []}

    name = profile.get("name", "")
    current_firm = profile.get("current_firm", "")
    current_year = datetime.now().year
    queries = [
        f"{current_firm} news {current_year}".strip(),
        f"{name} {current_firm} announcement".strip(),
    ]

    results_by_url = {}
    search = TavilySearch(max_results=5)
    for query in queries:
        response = search.invoke({"query": query})
        for result in response.get("results", []):
            url = result.get("url")
            if url and url not in results_by_url:
                results_by_url[url] = result.get("content", "")

    evidence_parts = [f"{snippet}\n(source: {url})" for url, snippet in results_by_url.items() if snippet]
    evidence = "\n\n".join(evidence_parts)[:_MAX_EVIDENCE_CHARS]

    prompt_text = _PROMPT_PATH.read_text()
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
    response = llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(
            content=(
                f"Profile name: {name}\n"
                f"Current firm: {current_firm}\n\n"
                f"Evidence:\n{evidence}"
            )
        ),
    ])

    try:
        recent_signals = parse_json_response(response.content)
    except (json.JSONDecodeError, ValueError):
        recent_signals = []

    return {"recent_signals": recent_signals}
