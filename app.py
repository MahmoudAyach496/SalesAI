"""Streamlit UI for the SalesAI intelligence card."""

from collections import Counter
from html import escape
import time

from dotenv import load_dotenv
import streamlit as st
from agents.domain_expert import run_domain_expert
from agents.insight_generator import run_insight_generator
from agents.outreach_strategist import run_outreach_strategist
from agents.parser import run_parser
from agents.researcher import run_researcher
from agents.signals import run_signals
from pdf_export import generate_pdf_brief

load_dotenv()

st.set_page_config(
    page_title="SalesAI · Consulting Point", page_icon="🎯", layout="wide"
)

st.markdown(
    """
<style>
    .block-container { padding-top: 3.2rem; max-width: 1120px; }
    .main-header { font-size: 2.5rem; font-weight: 800; margin-bottom: 0; letter-spacing: -0.03em; }
    .sub-header { font-size: 1rem; color: #666; margin-top: -8px; }
    .hero-copy { color: #4b5563; font-size: 1.02rem; line-height: 1.6; margin: 18px 0 22px; max-width: 760px; }
    .input-card { background: #ffffff; border: 1px solid #eceff3; border-radius: 16px; padding: 22px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05); }
    .profile-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px; padding: 24px; margin: 16px 0; }
    .metric-card { background: white; border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 20px; margin: 8px 0; min-height: 120px; }
    .priority-item, .pain-item, .angle-item, .signal-item {
        background: white; border-left: 4px solid #4CAF50; border-radius: 0 8px 8px 0;
        padding: 14px 18px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .pain-item { border-left-color: #f44336; }
    .angle-item { border-left-color: #2196F3; }
    .signal-item { border-left-color: #FF9800; }
    .confidence-high { color: #2e7d32; font-weight: 600; }
    .confidence-medium { color: #f57f17; font-weight: 600; }
    .confidence-low { color: #c62828; font-weight: 600; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 500; margin-right: 8px; }
    .badge-tier { background: #e3f2fd; color: #1565c0; }
    .badge-seniority { background: #f3e5f5; color: #7b1fa2; }
    .draft-box { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 16px; font-size: 0.95rem; line-height: 1.6; }
    .source-link { font-size: 0.85rem; color: #1976d2; }
    .pipeline-step { padding: 8px 12px; border-radius: 6px; margin: 4px 0; font-size: 0.85rem; }
    .step-done { background: #e8f5e9; color: #2e7d32; }
    .step-running { background: #fff3e0; color: #e65100; }
    .sidebar-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px;
        margin: 12px 0 18px; box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04); }
    .arch-step { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #eef2f7; }
    .arch-step:last-child { border-bottom: 0; }
    .arch-number { background: #fee2e2; color: #dc2626; border-radius: 999px; min-width: 24px; height: 24px;
        display: inline-flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 700; }
    .arch-title { font-weight: 700; color: #111827; font-size: 0.9rem; }
    .arch-copy { color: #6b7280; font-size: 0.82rem; line-height: 1.35; margin-top: 2px; }
    .sidebar-note { color: #4b5563; font-size: 0.88rem; line-height: 1.5; }
    [data-testid="stSidebar"] { background: #f8fafc; }
    div[data-testid="stTextArea"] textarea { border-radius: 12px; border-color: #d9dee7; font-size: 1rem; }
    div[data-testid="stButton"] button { border-radius: 10px; padding: 0.65rem 1.1rem; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)


def html(text: object) -> str:
    return escape(str(text or "")).replace("\n", "<br>")


def confidence_span(confidence: str) -> str:
    level = (confidence or "").lower()
    css_class = f"confidence-{level}" if level in {"high", "medium", "low"} else ""
    return f'<span class="{css_class}">{html(confidence or "unknown")}</span>'


def profile_line(profile: dict) -> str:
    role = profile.get("current_role", "Unknown")
    firm = profile.get("current_firm", "Unknown")
    role_known = role and role != "Unknown"
    firm_known = firm and firm != "Unknown"
    if role_known and firm_known:
        return f"{html(role)} at {html(firm)}"
    if firm_known:
        return f"at {html(firm)}"
    if role_known:
        return html(role)
    return "Role and firm not confidently identified"


def render_profile(profile: dict) -> None:
    name = profile.get("name", "Unknown")
    tier = profile.get("firm_tier", "Unknown")
    seniority = profile.get("seniority", "Unknown")
    summary = profile.get("career_summary", "")
    years = profile.get("years_in_role_estimate", "Unknown")

    st.markdown(f"""
<div class="profile-card">
    <h2>{html(name)}</h2>
    <p style="font-size:1.05rem; margin-bottom:12px;">{profile_line(profile)}</p>
    <span class="badge badge-tier">{html(tier)}</span>
    <span class="badge badge-seniority">{html(seniority)}</span>
    <p style="margin-top:18px;">{html(summary)}</p>
</div>
""", unsafe_allow_html=True)
    if "Unknown" in {name, tier, seniority} or profile.get("current_role") == "Unknown":
        st.warning(
            "Some profile fields could not be confidently identified from public "
            "LinkedIn search snippets. Review the intelligence as directional."
        )
    if years and years != "Unknown":
        st.caption(f"Estimated years in role: {years}")


def render_items(items: list, item_class: str, title_key: str, body_key: str) -> None:
    for item in items:
        st.markdown(f"""
<div class="{item_class}">
    <strong>{html(item.get(title_key, "Untitled"))}</strong>
    <div style="color:#666; margin-top:6px;">{html(item.get(body_key, ""))}</div>
    <div style="margin-top:8px;">Confidence: {confidence_span(item.get("confidence", ""))}</div>
</div>
""", unsafe_allow_html=True)


def render_angles(angles: list) -> None:
    for angle in angles:
        st.markdown(f"""
<div class="angle-item">
    <strong>{html(angle.get("angle", "Untitled angle"))}</strong>
    <div style="color:#666; margin-top:6px;">{html(angle.get("why_it_works", ""))}</div>
</div>
""", unsafe_allow_html=True)


def render_signals(signals: list) -> None:
    for signal in signals:
        st.markdown(f"""
<div class="signal-item">
    <strong>{html(signal.get("signal", "Untitled signal"))}</strong>
    <div style="color:#666; margin-top:6px;">Date: {html(signal.get("date", "Unknown"))}</div>
    <div style="color:#666; margin-top:6px;">{html(signal.get("implication", ""))}</div>
</div>
""", unsafe_allow_html=True)


def render_drafts(drafts: dict) -> None:
    tabs = st.tabs(["Warm Referral", "Cold (Value First)", "Event Trigger"])
    for tab, key in zip(tabs, ["warm_referral", "cold_value_first", "event_trigger"]):
        with tab:
            st.caption("📋 Copy")
            st.markdown(
                f'<div class="draft-box">{html(drafts.get(key, ""))}</div>',
                unsafe_allow_html=True,
            )


def render_sources(sources: list) -> None:
    with st.expander("Sources"):
        if not sources:
            st.caption("No sources available.")
            return
        for source in sources:
            url = source.get("url", "")
            if url:
                st.markdown(
                    f'<div class="source-link"><a href="{html(url)}" target="_blank">'
                    f'{html(url)}</a> — {html(source.get("used_for", "research"))}</div>',
                    unsafe_allow_html=True,
                )


def render_pipeline_trace(result: dict, trace: dict) -> None:
    profile = result.get("profile") or {}
    timings = trace.get("timings", {})
    priorities = result.get("commercial_priorities", [])
    pain_points = result.get("pain_points", [])
    confidence_counts = Counter(
        item.get("confidence", "unknown") for item in priorities + pain_points
    )
    signals = result.get("recent_signals", [])
    angles = result.get("conversation_angles", [])
    drafts = result.get("outreach_drafts", {})

    with st.expander("🔍 Pipeline Trace — How this intelligence was generated"):
        st.markdown(f"**1. Parser** (took {timings.get('parser', 0):.1f}s)")
        st.markdown(f"- Input type: {trace.get('input_type', 'Unknown')}")
        st.markdown(
            f"- Extracted: {profile.get('name', 'Unknown')}, "
            f"{profile.get('current_role', 'Unknown')} at {profile.get('current_firm', 'Unknown')}"
        )
        st.markdown(
            f"- Firm tier: {profile.get('firm_tier', 'Unknown')}, "
            f"Seniority: {profile.get('seniority', 'Unknown')}"
        )

        st.markdown(f"**2. Research Agent** (took {timings.get('researcher', 0):.1f}s)")
        st.markdown(f"- Ran {trace.get('research_searches', 0)} web searches")
        st.markdown(f"- Found {len(result.get('sources', []))} unique sources")
        with st.expander("Research evidence", expanded=False):
            st.code((result.get("research_evidence") or "")[:300])

        st.markdown(f"**3. Domain Expert** (took {timings.get('domain_expert', 0):.1f}s)")
        with st.expander("Domain context", expanded=False):
            st.code((result.get("domain_context") or "")[:300])

        st.markdown(f"**4. Signals Agent** (took {timings.get('signals', 0):.1f}s)")
        st.markdown(f"- Found {len(signals)} trigger events")
        for signal in signals:
            st.markdown(f"- {signal.get('signal', 'Untitled signal')}")

        st.markdown(f"**5. Insight Generator** (took {timings.get('insight_generator', 0):.1f}s)")
        st.markdown(
            f"- Generated {len(priorities)} priorities, {len(pain_points)} pain points"
        )
        st.markdown(
            "- Confidence levels: "
            f"{confidence_counts.get('high', 0)} high, "
            f"{confidence_counts.get('medium', 0)} medium, "
            f"{confidence_counts.get('low', 0)} low"
        )

        st.markdown(f"**6. Outreach Strategist** (took {timings.get('outreach_strategist', 0):.1f}s)")
        st.markdown(f"- Generated {len(angles)} conversation angles")
        st.markdown(f"- Generated {sum(1 for draft in drafts.values() if draft)} outreach drafts")
        st.markdown(f"- Overall confidence: {result.get('confidence_note', 'No confidence note available.')}")
        st.markdown(f"**Total pipeline time: {trace.get('total_time', 0):.1f}s**")


def run_pipeline(user_input: str) -> tuple[dict, dict]:
    state = {"user_input": user_input}
    timings = {}
    started_at = time.time()
    input_type = "LinkedIn URL" if "linkedin.com/" in user_input.lower() else "Pasted text"

    with st.status("Running intelligence pipeline...", expanded=True) as status:
        st.write("🔍 Parsing input...")
        step_started = time.time()
        profile = run_parser(user_input)
        timings["parser"] = time.time() - step_started
        state["profile"] = profile.model_dump()

        st.write("🌐 Researching profile...")
        step_started = time.time()
        state.update(run_researcher(state))
        timings["researcher"] = time.time() - step_started

        st.write("🏢 Analyzing industry context...")
        step_started = time.time()
        state.update(run_domain_expert(state))
        timings["domain_expert"] = time.time() - step_started

        st.write("📡 Scanning for signals...")
        step_started = time.time()
        state.update(run_signals(state))
        timings["signals"] = time.time() - step_started

        st.write("💡 Generating insights...")
        step_started = time.time()
        state.update(run_insight_generator(state))
        timings["insight_generator"] = time.time() - step_started

        st.write("✉️ Crafting outreach...")
        step_started = time.time()
        state.update(run_outreach_strategist(state))
        timings["outreach_strategist"] = time.time() - step_started
        status.update(label="Intelligence complete", state="complete")

    profile_state = state.get("profile") or {}
    research_searches = 0
    if profile_state.get("name"):
        research_searches = 2
        if profile_state.get("firm_tier") != "Other":
            research_searches += 1

    trace = {
        "input_type": input_type,
        "timings": timings,
        "research_searches": research_searches,
        "total_time": time.time() - started_at,
    }
    return state, trace


with st.sidebar:
    st.markdown("### About this tool")
    st.markdown(
        '<div class="sidebar-note">A 6-agent LangGraph pipeline that turns a LinkedIn URL, bio, or company note into recruiter-ready commercial intelligence.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Architecture")
    st.markdown(
        """
<div class="sidebar-card">
    <div class="arch-step">
        <span class="arch-number">1</span>
        <div><div class="arch-title">Input</div><div class="arch-copy">LinkedIn URL, bio, or company description.</div></div>
    </div>
    <div class="arch-step">
        <span class="arch-number">2</span>
        <div><div class="arch-title">Parser</div><div class="arch-copy">Normalises messy text into a structured profile.</div></div>
    </div>
    <div class="arch-step">
        <span class="arch-number">3</span>
        <div><div class="arch-title">Research + Domain + Signals</div><div class="arch-copy">Enriches the profile with public evidence, consulting context, and trigger events.</div></div>
    </div>
    <div class="arch-step">
        <span class="arch-number">4</span>
        <div><div class="arch-title">Insights</div><div class="arch-copy">Synthesises priorities, pain points, and conversation angles.</div></div>
    </div>
    <div class="arch-step">
        <span class="arch-number">5</span>
        <div><div class="arch-title">Outreach Card</div><div class="arch-copy">Returns cited intelligence and ready-to-use message drafts.</div></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("### How it works")
    st.markdown(
        """
<div class="sidebar-note">
Each agent owns one narrow step, which keeps the output structured, sourced, and easy to review before outreach.
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("Built by [Mahmoud Ayach](https://github.com/mahmoudayach)")


left, right = st.columns([2, 1])
with left:
    st.markdown('<div class="main-header">🎯 SalesAI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Commercial Intelligence for Consulting Point</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-copy">Paste a public profile, LinkedIn URL, or short company note. SalesAI researches the person, identifies commercial priorities, and drafts recruiter-ready outreach in one pass.</div>',
        unsafe_allow_html=True,
    )
with right:
    st.empty()

st.divider()

st.markdown('<div class="input-card">', unsafe_allow_html=True)
user_input = st.text_area(
    label="Profile or company input",
    placeholder="Paste a LinkedIn URL, profile bio, or company description...",
    height=150,
)

if st.button("Generate Intelligence", type="primary"):
    if not user_input.strip():
        st.error("Please paste a LinkedIn URL, bio, or company description.")
    else:
        try:
            result, trace = run_pipeline(user_input.strip())
            st.session_state["result"] = result
            st.session_state["pipeline_trace"] = trace
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
st.markdown("</div>", unsafe_allow_html=True)

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    render_profile(result.get("profile") or {})
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("### 📊 Commercial Priorities")
        priorities = result.get("commercial_priorities", [])
        if priorities:
            render_items(priorities, "priority-item", "priority", "rationale")
        else:
            st.info(
                "No specific priorities identified — limited public evidence for this profile."
            )
    with right:
        st.markdown("### ⚠️ Pain Points")
        pain_points = result.get("pain_points", [])
        if pain_points:
            render_items(pain_points, "pain-item", "pain_point", "rationale")
        else:
            st.info(
                "No specific pain points identified — limited public evidence for this profile."
            )
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("### 💬 Conversation Angles")
        angles = result.get("conversation_angles", [])
        if angles:
            render_angles(angles)
        else:
            st.info("No conversation angles generated.")
    with right:
        st.markdown("### 📡 Recent Signals")
        signals = result.get("recent_signals", [])
        if signals:
            render_signals(signals)
        else:
            st.info("No recent trigger events detected.")

    st.divider()
    st.markdown("### Outreach Drafts")
    render_drafts(result.get("outreach_drafts", {}))

    st.divider()
    st.info(result.get("confidence_note", "No confidence note available."))
    render_sources(result.get("sources", []))

    render_pipeline_trace(result, st.session_state.get("pipeline_trace", {}))

    st.divider()
    profile = result.get("profile") or {}
    pdf_bytes = generate_pdf_brief(st.session_state.result)
    st.download_button(
        label="📄 Download PDF Brief",
        data=pdf_bytes,
        file_name=f"intelligence_brief_{profile.get('name', 'unknown').lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
    )
