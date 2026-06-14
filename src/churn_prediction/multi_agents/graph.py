# graph.py — 2 pipeline độc lập + 1 pipeline tổng hợp
import sys
from pathlib import Path

from langgraph.graph import StateGraph, END
from state import SentimentState, ChurnState, ReportState
from agents import SentimentAgent, ChurnAgent, ReportAgent, ActionAgent
from churn_prediction.paths import SENTIMENT_MODEL_PATH, CHURN_MODEL_PATH

# ── Khởi tạo agents ────────────────────────────────────────────────────────────
sentiment_agent = SentimentAgent(str(SENTIMENT_MODEL_PATH))
churn_agent     = ChurnAgent(str(CHURN_MODEL_PATH))
report_agent    = ReportAgent()
action_agent    = ActionAgent()


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE 1 — Sentiment (Olist)
# ══════════════════════════════════════════════════════════════════════════════
def node_sentiment(state: SentimentState) -> SentimentState:
    try:
        result = sentiment_agent.analyze(state["review_text"] or "")
        return {**state, "sentiment_result": result}
    except Exception as e:
        return {**state, "error": f"SentimentAgent: {e}"}


def build_sentiment_pipeline():
    graph = StateGraph(SentimentState)
    graph.add_node("sentiment", node_sentiment)
    graph.set_entry_point("sentiment")
    graph.add_edge("sentiment", END)
    return graph.compile()


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE 2 — Churn (Online Retail II)
# ══════════════════════════════════════════════════════════════════════════════
def node_churn(state: ChurnState) -> ChurnState:
    try:
        result = churn_agent.predict(state["features"] or {})
        return {**state, "churn_result": result}
    except Exception as e:
        return {**state, "error": f"ChurnAgent: {e}"}


def build_churn_pipeline():
    graph = StateGraph(ChurnState)
    graph.add_node("churn", node_churn)
    graph.set_entry_point("churn")
    graph.add_edge("churn", END)
    return graph.compile()


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE 3 — Report + Action (tổng hợp 2 kết quả trên)
# ══════════════════════════════════════════════════════════════════════════════
def node_report(state: ReportState) -> ReportState:
    try:
        report = report_agent.generate(
            sentiment_summary = state["sentiment_summary"],
            churn_summary     = state["churn_summary"],
        )
        return {**state, "report": report}
    except Exception as e:
        return {**state, "error": f"ReportAgent: {e}"}


def node_action(state: ReportState) -> ReportState:
    try:
        action_plan = action_agent.recommend(
            sentiment_summary = state["sentiment_summary"],
            churn_summary     = state["churn_summary"],
            report            = state["report"],
        )
        return {**state, "action_plan": action_plan}
    except Exception as e:
        return {**state, "error": f"ActionAgent: {e}"}


def should_continue(state: ReportState) -> str:
    return END if state.get("error") else "continue"


def build_report_pipeline():
    graph = StateGraph(ReportState)
    graph.add_node("report", node_report)
    graph.add_node("action", node_action)
    graph.set_entry_point("report")
    graph.add_conditional_edges(
        "report",
        should_continue,
        {"continue": "action", END: END}
    )
    graph.add_edge("action", END)
    return graph.compile()


# ── Compile sẵn để import ──────────────────────────────────────────────────────
sentiment_pipeline = build_sentiment_pipeline()
churn_pipeline     = build_churn_pipeline()
report_pipeline    = build_report_pipeline()