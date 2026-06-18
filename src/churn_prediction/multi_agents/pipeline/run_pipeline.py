# run_pipeline.py — Chạy 2 pipeline độc lập rồi tổng hợp
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
import pandas as pd
from graph import customer_data_pipeline,sentiment_pipeline, churn_pipeline, report_pipeline

def run_customer_data_pipeline(order_input: dict) -> dict:
    """
    Chạy Agent 0 để xử lý dữ liệu đầu vào (nếu cần).
    Trả về customer_profile và sentiment_result để đưa vào 2 pipeline chính.
    """
    state = customer_data_pipeline.invoke({
        "order_input": order_input,
        "customer_profile": None,
        "sentiment_result": None,
        "churn_result": None,
        "report": None,
        "action": None,
        "error": None,
    })
    return state
def run_sentiment_batch(reviews_df: pd.DataFrame,
                        text_col: str = "review_comment_message",
                        id_col: str   = "customer_id") -> dict:
    """
    Chạy Agent 1 trên toàn bộ Olist reviews.
    Trả về summary thống kê để đưa vào Agent 3.
    """
    results = []
    for _, row in reviews_df.iterrows():
        state = sentiment_pipeline.invoke({
            "customer_id"    : str(row[id_col]),
            "review_text"    : str(row.get(text_col, "")),
            "sentiment_result": None,
            "error"          : None,
        })
        if not state.get("error"):
            results.append(state["sentiment_result"])

    if not results:
        return {"error": "Không có kết quả sentiment"}

    labels      = [r["label"] for r in results]
    label_counts = pd.Series(labels).value_counts()

    return {
        "total_reviews"   : len(results),
        "dominant_label"  : label_counts.index[0],
        "positive_pct"    : round(labels.count("positive") / len(labels), 3),
        "neutral_pct"     : round(labels.count("neutral")  / len(labels), 3),
        "negative_pct"    : round(labels.count("negative") / len(labels), 3),
        "avg_confidence"  : round(sum(r["confidence"] for r in results) / len(results), 4),
    }


def run_churn_batch(customers_df: pd.DataFrame,
                    feature_cols: list,
                    id_col: str = "Customer ID") -> dict:
    """
    Chạy Agent 2 trên toàn bộ Online Retail II customers.
    Trả về summary thống kê để đưa vào Agent 3.
    """
    results = []
    for _, row in customers_df.iterrows():
        features = row[feature_cols].to_dict()
        state    = churn_pipeline.invoke({
            "customer_id" : str(row[id_col]),
            "features"    : features,
            "churn_result": None,
            "error"       : None,
        })
        if not state.get("error") and state["churn_result"].get("churn_probability") is not None:
            results.append(state["churn_result"])

    if not results:
        return {"error": "Không có kết quả churn"}

    probs      = [r["churn_probability"] for r in results]
    risks      = [r["risk_level"] for r in results]
    risk_counts = pd.Series(risks).value_counts()

    return {
        "total_customers" : len(results),
        "avg_churn_prob"  : round(sum(probs) / len(probs), 4),
        "high_risk_pct"   : round(risks.count("high")   / len(risks), 3),
        "medium_risk_pct" : round(risks.count("medium") / len(risks), 3),
        "low_risk_pct"    : round(risks.count("low")    / len(risks), 3),
        "dominant_risk"   : risk_counts.index[0],
    }


def run_full_system(sentiment_summary: dict,
                    churn_summary: dict) -> dict:
    """
    Chạy Agent 3 + 4 để tổng hợp báo cáo và đề xuất hành động.
    """
    state = report_pipeline.invoke({
        "sentiment_summary": sentiment_summary,
        "churn_summary"    : churn_summary,
        "report"           : None,
        "action_plan"      : None,
        "error"            : None,
    })
    return state


# ── Demo ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ── Bước 1: Load data ──────────────────────────────────────────────────────
    # Thay bằng path thực của bạn
    # reviews_df   = pd.read_parquet("data/processed/olist_reviews.parquet")
    # customers_df = pd.read_parquet("data/features/features.parquet")
    # feature_cols = [c for c in customers_df.columns
    #                 if c not in ["Customer ID", "snapshot_date"]]

    # ── Mock data để test nhanh ────────────────────────────────────────────────
    print("── Bước 1: Chạy Agent 1 (Sentiment) ──")
    sentiment_summary = {
        "total_reviews" : 500,
        "dominant_label": "negative",
        "positive_pct"  : 0.35,
        "neutral_pct"   : 0.20,
        "negative_pct"  : 0.45,
        "avg_confidence": 0.82,
    }
    print(f"  Sentiment summary: {sentiment_summary}")

    print("\n── Bước 2: Chạy Agent 2 (Churn) ──")
    churn_summary = {
        "total_customers": 5878,
        "avg_churn_prob" : 0.61,
        "high_risk_pct"  : 0.38,
        "medium_risk_pct": 0.29,
        "low_risk_pct"   : 0.33,
        "dominant_risk"  : "high",
    }
    print(f"  Churn summary: {churn_summary}")

    print("\n── Bước 3: Chạy Agent 3 + 4 (Report + Action) ──")
    final = run_full_system(sentiment_summary, churn_summary)

    if final.get("error"):
        print(f"  ✗ Error: {final['error']}")
    else:
        print(f"\n{'═'*55}")
        print("BÁO CÁO TỔNG HỢP:")
        print('═'*55)
        print(final["report"])
        print(f"\n{'═'*55}")
        print("KẾ HOẠCH HÀNH ĐỘNG:")
        print('═'*55)
        print(json.dumps(final["action_plan"], ensure_ascii=False, indent=2))