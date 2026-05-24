"""
Parser agent for the AI Sales Intelligence Assistant.
Converts raw user input (LinkedIn URL, pasted bio, or company description)
into a validated Profile object using Claude structured output.
"""

import re
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from schema import Profile

load_dotenv()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "parser.md"
_LINKEDIN_RE = re.compile(r"linkedin\.com/(in|company)/")
_MAX_EVIDENCE_CHARS = 3000


def run_parser(user_input: str) -> Profile:
    """
    Parse raw user input into a validated Profile object.

    Args:
        user_input: One of three formats:
            - LinkedIn URL (containing 'linkedin.com/in/' or
              'linkedin.com/company/')
            - Pasted bio text
            - Company description text

    Behaviour:
        - LinkedIn URLs trigger a Tavily web search (max 5 results,
          ~3000 char evidence cap) to gather public snippets, since direct
          LinkedIn scraping is out of scope.
        - Pasted text is used as evidence directly.
        - Claude (Sonnet 4.5) is called with the Parser prompt and
          structured-output binding to the Profile Pydantic model.
        - Fields that cannot be inferred return "Unknown" — the prompt
          forbids fabrication.

    Returns:
        A validated Profile object.

    Raises:
        Any underlying API or validation error bubbles up — we want loud
        failures during development.
    """
    prompt_text = _PROMPT_PATH.read_text()

    if _LINKEDIN_RE.search(user_input):
        input_type = "LinkedIn URL"
        search = TavilySearch(max_results=5)

        # Search 1: the URL itself
        suffix = "LinkedIn profile" if "/in/" in user_input else "company"
        r1 = search.invoke({"query": f"{user_input} {suffix}"})
        snippets_1 = [r.get("content", "") for r in r1.get("results", [])]

        # Search 2: extract name/company slug from URL for a name-based search
        # e.g. "linkedin.com/in/benwhalley/" -> "benwhalley"
        slug = user_input.rstrip("/").split("/")[-1]
        name_query = slug.replace("-", " ")
        r2 = search.invoke({"query": f"{name_query} LinkedIn"})
        snippets_2 = [r.get("content", "") for r in r2.get("results", [])]

        # Combine and deduplicate snippets
        all_snippets = snippets_1 + snippets_2
        evidence = "\n\n".join(s for s in all_snippets if s)[:_MAX_EVIDENCE_CHARS]
        if not evidence.strip():
            evidence = user_input
    else:
        input_type = "Pasted text"
        evidence = user_input

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)
    structured_llm = llm.with_structured_output(Profile)
    return structured_llm.invoke([
        SystemMessage(content=prompt_text),
        HumanMessage(content=f"Input type: {input_type}\nEvidence:\n{evidence}"),
    ])
