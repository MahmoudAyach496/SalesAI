# AI Sales Intelligence Assistant — Scope

Practical assessment for Consulting Point (AI & Systems Analyst role).
Challenge 4 — submitted to Ben Whalley.

---

## 1. Problem statement

An internal tool for Consulting Point's recruiters that turns a LinkedIn URL,
bio, or company description into a structured commercial intelligence brief —
covering profile summary, likely commercial priorities, pain points,
conversation angles, and draft outreach messages — to accelerate pre-call
research from 30 minutes to 30 seconds.

---

## 2. Test personas

Five real LinkedIn profiles used to demo and stress-test the system.
Each persona tests a different dimension of the tool.

| # | Persona type | Why this persona | Real LinkedIn URL |
|---|---|---|---|
| 1 | Ben Whalley — Partner & Group Sales Director, Consulting Point | Meta-demo on the assessor himself. Tests recruitment-industry context and sales-leader profile. | https://www.linkedin.com/in/benwhalley/ |
| 2 | Big 4 consulting Partner (Deloitte / EY / PwC / KPMG, London) | Tests large-firm seniority — Consulting Point's bread and butter. | _TBD — fill in by end of day 1_ |
| 3 | MBB Engagement Manager or Principal (McKinsey / BCG / Bain, London) | Tests elite-tier consulting and the mid-senior ladder where most placements happen. | _TBD — fill in by end of day 1_ |
| 4 | Boutique consulting founder / Partner (e.g. strategy or digital boutique) | Tests founder mindset and very different pain points (scaling, BD, talent). | _TBD — fill in by end of day 1_ |
| 5 | Non-consultant decision-maker (PE talent partner or Chief of Staff) | Tests that the tool generalises beyond consultants — Consulting Point's clients aren't all consultants themselves. | _TBD — fill in by end of day 1_ |

---

## 3. Output schema

The exact JSON shape returned by the system. Every agent's output rolls up
into this single structured "intelligence card."

```json
{
  "profile": {
    "name": "string",
    "current_role": "string",
    "current_firm": "string",
    "firm_tier": "MBB | Big 4 | Tier 2 | Boutique | In-house | Other",
    "seniority": "Analyst | Consultant | Manager | Senior Manager | Director | Principal | Partner | C-level",
    "years_in_role_estimate": "string",
    "career_summary": "2-3 sentence narrative"
  },
  "commercial_priorities": [
    {
      "priority": "string",
      "rationale": "string",
      "confidence": "high | medium | low"
    }
  ],
  "pain_points": [
    {
      "pain_point": "string",
      "rationale": "string",
      "confidence": "high | medium | low"
    }
  ],
  "conversation_angles": [
    {
      "angle": "string",
      "why_it_works": "string"
    }
  ],
  "outreach_drafts": {
    "warm_referral": "string (max 80 words)",
    "cold_value_first": "string (max 80 words)",
    "event_trigger": "string (max 80 words)"
  },
  "recent_signals": [
    {
      "signal": "string",
      "date": "YYYY-MM-DD or approx",
      "source_url": "string",
      "implication": "string"
    }
  ],
  "sources": [
    {
      "url": "string",
      "used_for": "string"
    }
  ],
  "confidence_note": "string — overall caveats on data quality"
}
```

---

## 4. Architecture and agents

LangGraph multi-agent pipeline. Each agent has a narrow responsibility,
reads from shared state, writes back into shared state.

| Agent | Input | Output | Why it exists |
|---|---|---|---|
| Parser | raw user input (URL, bio, or company description) | structured `profile` block | Normalise messy input into a clean profile object. |
| Research | `profile` | enriched profile + raw evidence snippets | Web search (Tavily / Serper) to enrich public context. |
| Domain expert | enriched profile | consulting-industry context (tier norms, ladder, what this seniority typically owns) | Encodes Consulting Point's domain — the bit you can't get from a generic LLM. |
| Signals | `profile` + firm name | `recent_signals` array | Bonus node: scans for news, leadership moves, funding, hires. |
| Insight generator | everything above | `commercial_priorities` + `pain_points` | The "so what" — turns raw context into commercial intelligence. |
| Outreach strategist | full state | `conversation_angles` + `outreach_drafts` | The deliverable a recruiter would actually use tomorrow morning. |

Project file structure:

```
SalesAI/
├── SCOPE.md
├── README.md
├── requirements.txt
├── .env.example
├── app.py                  # Streamlit entry point
├── graph.py                # LangGraph wiring — the orchestrator
├── schema.py               # Pydantic models for the output JSON
├── state.py                # Shared LangGraph state object
├── agents/
│   ├── __init__.py
│   ├── parser.py
│   ├── researcher.py
│   ├── domain_expert.py
│   ├── signals.py
│   ├── insight_generator.py
│   └── outreach_strategist.py
├── prompts/
│   ├── parser.md
│   ├── researcher.md
│   ├── domain_expert.md
│   ├── signals.md
│   ├── insight_generator.md
│   └── outreach_strategist.md
└── tests/
    └── test_personas.py    # Lightweight: runs all 5 personas, prints output
```

---

## 5. v1 / stretch / out of scope

### v1 — must ship in 72 hours

- All 6 agents wired in LangGraph
- Streamlit UI: paste a LinkedIn URL → see structured intelligence card
- Web search via Tavily or Serper for the Research and Signals agents
- Output validated against the Pydantic schema
- Source citations on every claim where evidence was used
- 5 working test personas
- README explaining architecture, decisions, how to run

### Stretch — only if v1 is locked by hour 50

- Voice input (paste a URL by speaking — Antler hackathon callback)
- Export the intelligence card as a PDF brief
- Side-by-side comparison of two profiles
- Caching layer so repeated lookups are instant
- Better UI (move from Streamlit to React)

### Out of scope — explicitly not building

- LinkedIn scraping (use public web snippets only, no ToS issues)
- User authentication or multi-user support
- A real database — in-memory state is fine for the demo
- Production deployment — local Streamlit is enough
- Async / queuing infrastructure
- Tests beyond the persona smoke test
- Fine-tuning or training any model

---

## 6. Evaluation — how I'll know it's working

- All 5 personas produce a complete, valid JSON card (no missing fields)
- Every claim has at least one cited source URL
- The Loom walkthrough runs end-to-end on Ben's profile without errors
- I can explain every architectural decision in the Teams call
- Total cost per run is under $0.20
- End-to-end latency is under 60 seconds per profile
