# state.py — Shared state cho 2 pipeline độc lập
from typing import TypedDict, Optional, List


class SentimentState(TypedDict):
    """State cho Agent 1 — chạy trên Olist dataset"""
    # Input
    customer_id  : str
    review_text  : str

    # Output Agent 1
    sentiment_result: Optional[dict]  # {label, confidence, proba}
    error            : Optional[str]


class ChurnState(TypedDict):
    """State cho Agent 2 — chạy trên Online Retail II dataset"""
    # Input
    customer_id: str
    features   : dict                 # numeric features từ feature_engineering

    # Output Agent 2
    churn_result: Optional[dict]      # {churn_probability, risk_level, ...}
    error       : Optional[str]


class ReportState(TypedDict):
    """State cho Agent 3 + 4 — nhận kết quả từ cả 2 pipeline"""
    # Tổng hợp từ 2 pipeline
    sentiment_summary: Optional[dict]  # thống kê từ Agent 1
    churn_summary    : Optional[dict]  # thống kê từ Agent 2

    # Output Agent 3
    report     : Optional[str]

    # Output Agent 4
    action_plan: Optional[dict]

    error: Optional[str]