"""Research agent: gathers source-cited web evidence for a parsed profile."""

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "researcher.md"
_MAX_EVIDENCE_CHARS = 4000


def run_researcher(state: dict) -> dict:
    """
    Enrich a Parser profile with research_evidence text and source metadata.
    """
    profile = state.get("profile")
    if not profile or not profile.get("name"):
        return {
            "research_evidence": "No profile available for research.",
            "sources": [],
        }

    name = profile.get("name", "")
    current_firm = profile.get("current_firm", "")
    current_role = profile.get("current_role", "")
    firm_tier = profile.get("firm_tier", "")

    queries = [
        f"{name} {current_firm}".strip(),
        f"{name} {current_role} {current_firm}".strip(),
    ]
    if firm_tier != "Other":
        queries.append(f"{current_firm} consulting news".strip())

    results_by_url = {}
    search = TavilySearch(max_results=3)
    for query in queries:
        response = search.invoke({"query": query})
        for result in response.get("results", []):
            url = result.get("url")
            if url and url not in results_by_url:
                results_by_url[url] = result.get("content", "")

    evidence_parts = [f"{snippet}\n(source: {url})" for url, snippet in results_by_url.items() if snippet]
    evidence = "\n\n".join(evidence_parts)[:_MAX_EVIDENCE_CHARS]

    prompt_text = _PROMPT_PATH.read_text()
    profile_summary = json.dumps(profile, indent=2)
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
    response = llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(
            content=(
                f"Parser profile:\n{profile_summary}\n\n"
                f"Web search evidence:\n{evidence}"
            )
        ),
    ])

    return {
        "research_evidence": response.content,
        "sources": [{"url": url, "used_for": "research"} for url in results_by_url],
    }
