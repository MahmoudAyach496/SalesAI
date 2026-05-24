# AI Sales Intelligence Assistant

A lightweight internal tool that takes a LinkedIn URL, bio, or company
description and returns structured commercial intelligence — profile summary,
likely commercial priorities, pain points, conversation angles, and draft
outreach messages.

Built as a 72-hour practical assessment for Consulting Point
(AI & Systems Analyst role, Challenge 4).

---

## What it does

A recruiter at Consulting Point spends 20-30 minutes researching a candidate
or client before a call: reading LinkedIn, inferring seniority, guessing what
the person cares about commercially, drafting an opening message.

This tool collapses that to ~30 seconds. Paste a LinkedIn URL, get back a
structured intelligence card you can read on the way to the meeting.

---

## Architecture

A multi-agent LangGraph pipeline. Each agent has one job.

```
User input (LinkedIn URL / bio / company)
            │
            ▼
      Parser agent              (normalise input → profile object)
            │
            ▼
   ┌────────┼────────┐
   ▼        ▼        ▼
Research   Domain    Signals     (enrich in parallel)
agent      expert    agent
   │        │        │
   └────────┼────────┘
            ▼
     Insight generator           (priorities + pain points)
            │
            ▼
   Outreach strategist           (angles + draft messages)
            │
            ▼
   Structured intelligence card  (validated JSON + cited sources)
```

Why multi-agent and not one big prompt:

- Separation of concerns — each agent has a narrow, testable job
- Easier to swap or upgrade any single node
- Cleaner evaluation (we can grade Parser output independently of Insight Generator output)
- Structured handoffs reduce hallucination — each agent sees only the upstream state it needs

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| Orchestration | LangGraph + LangChain | Multi-agent state graphs, structured outputs, easy to visualise |
| LLM | Anthropic Claude (Sonnet 4.5) | Strong structured output, lower hallucination rate |
| Web search | Tavily | LLM-friendly search results with source URLs |
| UI | Streamlit | Fastest path to a working demo in 72 hours |
| Validation | Pydantic | Enforces output schema, catches malformed agent output |
| Language | Python 3.11 | LangGraph native |

---

## Running locally

```bash
# 1. Clone and enter
git clone <repo>
cd SalesAI

# 2. Create virtual env
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add API keys
cp .env.example .env
# Open .env and fill in:
#   ANTHROPIC_API_KEY=sk-ant-...
#   TAVILY_API_KEY=tvly-...

# 5. Run
streamlit run app.py
```

---

## File structure

```
SalesAI/
├── SCOPE.md            ← project scope, schema, decisions
├── README.md           ← this file
├── app.py              ← Streamlit UI
├── graph.py            ← LangGraph orchestrator
├── schema.py           ← Pydantic output models
├── state.py            ← shared graph state
├── agents/             ← one file per agent
├── prompts/            ← prompts as separate .md files (versionable, swappable)
└── tests/              ← persona smoke tests
```

---

## Design decisions

(Filled in as the build progresses — these are the "why" answers for the Teams call.)

- **Why LangGraph over a single chain?** Multi-agent allows independent evaluation, parallel execution of Research / Domain / Signals nodes, and a cleaner failure story.
- **Why prompts in separate `.md` files?** Easier to iterate, diff, and present to non-technical reviewers. Ben can read them without opening Python.
- **Why Pydantic on every output?** A schema-validated card is the contract — if any agent returns malformed JSON, the graph catches it instead of silently passing garbage downstream.
- **Why source citations on every claim?** Hallucination control. If a "commercial priority" can't be traced to a search snippet or domain rule, the system marks it low-confidence.

---

## Limitations and honest caveats

- No real LinkedIn scraping — uses public web search only. If a profile has no public footprint, results will be thin.
- Outputs are *suggested intelligence*, not verified facts. Every claim is marked with a confidence level.
- Tested on 5 personas — not stress-tested at scale.
- Built in 72 hours as an assessment piece, not production software.

---

## What I'd build next

(For the "next 4 weeks" question Ben will almost certainly ask.)

- CRM integration (Salesforce / HubSpot hook so this runs automatically when a new contact is added)
- Slack bot wrapper — paste a URL in Slack, get the card back as a thread
- Feedback loop — recruiters mark which outreach drafts actually got replies, used to fine-tune the Outreach Strategist
- Multi-language support (French / Arabic for international markets)
- Confidence calibration — measure how often the tool's "high confidence" claims are actually correct
