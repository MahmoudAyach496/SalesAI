"""
LangGraph orchestrator for the pipeline in SCOPE.md section 4.

Wires the architecture diagram from README.md: Parser, enrichment agents,
Insight Generator, and Outreach Strategist.
"""

# Imports
import json

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph as CompiledGraph

from agents.parser import run_parser
from state import GraphState


# Node wrappers
def parser_node(state: GraphState) -> GraphState:
    user_input = state["user_input"]
    profile = run_parser(user_input)
    return {"profile": profile.model_dump()}


def research_node(state: GraphState) -> GraphState:
    from agents.researcher import run_researcher

    updates = run_researcher(state)
    return {k: v for k, v in updates.items() if k != "user_input"}


def domain_node(state: GraphState) -> GraphState:
    from agents.domain_expert import run_domain_expert

    updates = run_domain_expert(state)
    return {k: v for k, v in updates.items() if k != "user_input"}


def signals_node(state: GraphState) -> GraphState:
    from agents.signals import run_signals

    updates = run_signals(state)
    return {k: v for k, v in updates.items() if k != "user_input"}


def insight_node(state: GraphState) -> GraphState:
    from agents.insight_generator import run_insight_generator

    updates = run_insight_generator(state)
    return {k: v for k, v in updates.items() if k != "user_input"}


def outreach_node(state: GraphState) -> GraphState:
    from agents.outreach_strategist import run_outreach_strategist

    updates = run_outreach_strategist(state)
    return {k: v for k, v in updates.items() if k != "user_input"}


# Graph construction
def build_graph() -> CompiledGraph:
    graph = StateGraph(GraphState)

    graph.add_node("parser_node", parser_node)
    graph.add_node("research_node", research_node)
    graph.add_node("domain_node", domain_node)
    graph.add_node("signals_node", signals_node)
    graph.add_node("insight_node", insight_node)
    graph.add_node("outreach_node", outreach_node)

    graph.set_entry_point("parser_node")
    graph.add_edge("parser_node", "research_node")
    # TODO: convert to parallel execution with LangGraph fan-out when all three agents are implemented
    graph.add_edge("research_node", "domain_node")
    graph.add_edge("domain_node", "signals_node")
    graph.add_edge("signals_node", "insight_node")
    graph.add_edge("insight_node", "outreach_node")
    graph.add_edge("outreach_node", END)

    return graph.compile()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    graph = build_graph()
    print("Running full pipeline (6 agents)...\n")
    result = graph.invoke({
        "user_input": "https://www.linkedin.com/in/benwhalley/"
    })

    print("=" * 60)
    print("PROFILE")
    print("=" * 60)
    print(json.dumps(result.get("profile", {}), indent=2))

    print("\n" + "=" * 60)
    print("RESEARCH EVIDENCE (first 500 chars)")
    print("=" * 60)
    ev = result.get("research_evidence", "MISSING")
    print(str(ev)[:500])

    print("\n" + "=" * 60)
    print("DOMAIN CONTEXT (first 500 chars)")
    print("=" * 60)
    dc = result.get("domain_context", "MISSING")
    print(str(dc)[:500])

    print("\n" + "=" * 60)
    print("RECENT SIGNALS")
    print("=" * 60)
    print(json.dumps(result.get("recent_signals", "MISSING"), indent=2))

    print("\n" + "=" * 60)
    print("COMMERCIAL PRIORITIES")
    print("=" * 60)
    print(json.dumps(result.get("commercial_priorities", "MISSING"), indent=2))

    print("\n" + "=" * 60)
    print("PAIN POINTS")
    print("=" * 60)
    print(json.dumps(result.get("pain_points", "MISSING"), indent=2))

    print("\n" + "=" * 60)
    print("CONVERSATION ANGLES")
    print("=" * 60)
    print(json.dumps(result.get("conversation_angles", "MISSING"), indent=2))

    print("\n" + "=" * 60)
    print("OUTREACH DRAFTS")
    print("=" * 60)
    print(json.dumps(result.get("outreach_drafts", "MISSING"), indent=2))

    print("\n" + "=" * 60)
    print("CONFIDENCE NOTE")
    print("=" * 60)
    print(result.get("confidence_note", "MISSING"))

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)
    print(json.dumps(result.get("sources", []), indent=2))
