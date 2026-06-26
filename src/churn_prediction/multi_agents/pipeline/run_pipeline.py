# run_pipeline.py — Chạy 2 pipeline độc lập rồi tổng hợp
import pandas as pd
from ..graph.data_graph import data_pipeline
from ..graph.sentiment_graph import sentiment_pipeline
from ..graph.churn_graph import churn_pipeline
from ..graph.report_graph import report_pipeline

def run_prediction(order_input: dict) -> dict:
    """
    Chạy toàn bộ hệ thống Multi-Agent.

    FastAPI chỉ cần gọi hàm này.
    """
    state = data_pipeline.invoke({
        "order_input": order_input,
        "customer_profile": None,
        "sentiment_ready": None,
        "sentiment_result": None,
        "sentiment_summary": None,
        "features": None,
        "churn_result": None,
        "churn_summary": None,
        "report": None,
        "action_plan": None,
        "error": None,
    })


    state = sentiment_pipeline.invoke(state)
    
    #print(type(state))

    #for k, v in state.items():
    #    print(k, type(v))

    # if state.get("error"):
    #     return state
    # state = churn_pipeline.invoke(state)

    # if state.get("error"):
    #     return state
    # state = report_pipeline.invoke(state)

    return state

# def run_customer_data_pipeline(order_input: dict) -> dict:
#     """
#     Chạy Agent 0 để xử lý dữ liệu đầu vào.
#     Trả về customer_profile và sentiment_result.
#     """
#     state = data_pipeline.invoke({
#         "order_input": order_input,
#         "customer_profile": None,
#         "sentiment_ready": None,
#         "sentiment_result": None,
#         "sentiment_summary": None,
#         "features": None,
#         "churn_result": None,
#         "churn_summary": None,
#         "report": None,
#         "action_plan": None,
#         "error": None,
#     })
#     return state


# def run_sentiment_batch(reviews_df: pd.DataFrame,
#                         text_col: str = "review_comment_message",
#                         id_col: str   = "customer_id") -> dict:
#     """
#     Chạy Agent 1 (Sentiment) trên toàn bộ Olist reviews.
#     Trả về summary thống kê để đưa vào Agent 3.
#     """
#     results = []
#     for _, row in reviews_df.iterrows():
#         state = sentiment_pipeline.invoke({
#             "customer_id": str(row[id_col]),
#             "review_text": str(row.get(text_col, "")),
#             "sentiment_result": None,
#             "error": None,
#         })
#         if not state.get("error"):
#             results.append(state["sentiment_result"])

#     if not results:
#         return {"error": "Không có kết quả sentiment"}

#     labels = [r["label"] for r in results]
#     label_counts = pd.Series(labels).value_counts()

#     return {
#         "total_reviews": len(results),
#         "dominant_label": label_counts.index[0],
#         "positive_pct": round(labels.count("positive") / len(labels), 3),
#         "neutral_pct": round(labels.count("neutral") / len(labels), 3),
#         "negative_pct": round(labels.count("negative") / len(labels), 3),
#         "avg_confidence": round(sum(r["confidence"] for r in results) / len(results), 4),
#     }


# def run_churn_batch(customers_df: pd.DataFrame,
#                     feature_cols: list,
#                     id_col: str = "Customer ID") -> dict:
#     """
#     Chạy Agent 2 (Churn) trên toàn bộ Online Retail II customers.
#     Trả về summary thống kê để đưa vào Agent 3.
#     """
#     results = []
#     for _, row in customers_df.iterrows():
#         features = row[feature_cols].to_dict()
#         state = churn_pipeline.invoke({
#             "customer_id": str(row[id_col]),
#             "features": features,
#             "churn_result": None,
#             "error": None,
#         })
#         if not state.get("error") and state["churn_result"].get("churn_probability") is not None:
#             results.append(state["churn_result"])

#     if not results:
#         return {"error": "Không có kết quả churn"}

#     probs = [r["churn_probability"] for r in results]
#     risks = [r["risk_level"] for r in results]
#     risk_counts = pd.Series(risks).value_counts()

#     return {
#         "total_customers": len(results),
#         "avg_churn_prob": round(sum(probs) / len(probs), 4),
#         "high_risk_pct": round(risks.count("high") / len(risks), 3),
#         "medium_risk_pct": round(risks.count("medium") / len(risks), 3),
#         "low_risk_pct": round(risks.count("low") / len(risks), 3),
#         "dominant_risk": risk_counts.index[0],
#     }


# def run_full_system(sentiment_summary: dict,
#                     churn_summary: dict) -> dict:
#     """
#     Chạy Agent 3 + 4 để tổng hợp báo cáo và đề xuất hành động.
#     """
#     state = report_pipeline.invoke({
#         "sentiment_summary": sentiment_summary,
#         "churn_summary": churn_summary,
#         "report": None,
#         "action_plan": None,
#         "error": None,
#     })
#     return state


# ── Demo ─────────────────────────────────────
# if __name__ == "__main__":

#     print("── Bước 1: Chạy Agent 1 (Sentiment) ──")
#     sentiment_summary = {
#         "email": "nguyenvana@gmail.com",
#         "review_comment_message": "Sản phẩm rất tốt, giao hàng nhanh, tôi hài lòng!",
#         "order_id": "ORD20231201-001",
#         "order_purchase_timestamp": "2023-12-01",
#         "total_payment": 250.0,
#         "payment_type": "credit_card",
#         "max_installments": 3,  
#     }
#     print(f"  Sentiment summary: {sentiment_summary}")

#     print("\n── Bước 2: Chạy Agent 2 (Churn) ──")
#     churn_summary = {
#         "total_customers": 5878,
#         "avg_churn_prob": 0.61,
#         "high_risk_pct": 0.38,
#         "medium_risk_pct": 0.29,
#         "low_risk_pct": 0.33,
#         "dominant_risk": "high",
#     }
#     print(f"  Churn summary: {churn_summary}")

#     print("\n── Bước 3: Chạy Agent 3 + 4 (Report + Action) ──")
#     final = run_full_system(sentiment_summary, churn_summary)

#     if final.get("error"):
#         print(f"  ✗ Error: {final['error']}")
#     else:
#         print(f"\n{'═'*55}")
#         print("BÁO CÁO TỔNG HỢP:")
#         print('═'*55)
#         print(final["report"])
#         print(f"\n{'═'*55}")
#         print("KẾ HOẠCH HÀNH ĐỘNG:")
#         print('═'*55)
#         print(json.dumps(final["action_plan"], ensure_ascii=False, indent=2))