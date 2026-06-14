# test_agents.py — Test từng agent độc lập, hiển thị lỗi rõ ràng
import traceback
import pandas as pd
import numpy as np
from pathlib import Path
from churn_prediction.paths import FEATURES_ONLINE_RETAIL_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENTIMENT_MODEL_PATH = PROJECT_ROOT / "models" / "sentiment_model.pkl"
CHURN_MODEL_PATH     = FEATURES_ONLINE_RETAIL_DIR / "churn_model.pkl"

# ── Color output ───────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):   print(f"{GREEN}  ✓ {msg}{RESET}")
def fail(msg): print(f"{RED}  ✗ {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  ⚠ {msg}{RESET}")
def section(title): print(f"\n{'═'*55}\n  {title}\n{'═'*55}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST CASES — dữ liệu đầu vào đa dạng để bắt lỗi
# ══════════════════════════════════════════════════════════════════════════════
SENTIMENT_CASES = [
    # (label, input, mô tả)
    ("valid_positive",  "Sản phẩm tuyệt vời, giao hàng nhanh, rất hài lòng!",  "Review bình thường - tích cực"),
    ("valid_negative",  "Chất lượng tệ, giao chậm, không như mô tả.",            "Review bình thường - tiêu cực"),
    ("empty_string",    "",                                                        "Chuỗi rỗng"),
    ("none_value",      None,                                                      "None"),
    ("only_spaces",     "   ",                                                     "Chỉ có khoảng trắng"),
    ("very_long",       "tốt " * 500,                                             "Review rất dài (500 từ)"),
    ("special_chars",   "!@#$%^&*() 😀🛒 <script>alert(1)</script>",             "Ký tự đặc biệt + emoji + HTML"),
    ("number_string",   "12345 67890",                                             "Chỉ có số"),
    ("mixed_lang",      "Good product rất tốt sehr gut",                          "Đa ngôn ngữ"),
]

CHURN_CASES = [
    # (label, features_dict, mô tả)
    ("valid_high_risk", {
        "Recency": 200, "Frequency": 1, "Monetary": 50.0,
        "avg_order_value": 50.0, "avg_items_per_order": 1.0,
        "total_orders": 1, "unique_products": 1,
        "customer_age_days": 300, "days_since_last_purchase": 200,
        "purchase_span_days": 0, "avg_days_between_orders": np.nan,
        "total_revenue": 50.0, "avg_revenue_per_item": 50.0,
        "revenue_std": np.nan, "max_revenue": 50.0,
        "recent_30d_revenue": 0.0, "repeat_product_ratio": 0.0,
        "customer_lifetime_days": 0, "purchase_rate": np.nan,
    }, "Khách hàng rủi ro cao"),

    ("valid_low_risk", {
        "Recency": 5, "Frequency": 20, "Monetary": 5000.0,
        "avg_order_value": 250.0, "avg_items_per_order": 10.0,
        "total_orders": 20, "unique_products": 50,
        "customer_age_days": 700, "days_since_last_purchase": 5,
        "purchase_span_days": 690, "avg_days_between_orders": 35.0,
        "total_revenue": 5000.0, "avg_revenue_per_item": 25.0,
        "revenue_std": 80.0, "max_revenue": 600.0,
        "recent_30d_revenue": 300.0, "repeat_product_ratio": 0.8,
        "customer_lifetime_days": 690, "purchase_rate": 0.029,
    }, "Khách hàng trung thành"),

    ("missing_features", {
        "Recency": 50, "Frequency": 5,
        # thiếu nhiều features
    }, "Thiếu nhiều features"),

    ("all_nan", {col: np.nan for col in [
        "Recency","Frequency","Monetary","avg_order_value",
        "avg_items_per_order","total_orders","unique_products",
        "customer_age_days","days_since_last_purchase","purchase_span_days",
        "avg_days_between_orders","total_revenue","avg_revenue_per_item",
        "revenue_std","max_revenue","recent_30d_revenue",
        "repeat_product_ratio","customer_lifetime_days","purchase_rate",
    ]}, "Tất cả giá trị NaN"),

    ("empty_dict", {}, "Dict rỗng"),

    ("negative_values", {
        "Recency": -10, "Frequency": -1, "Monetary": -500.0,
        "avg_order_value": -50.0, "avg_items_per_order": -2.0,
        "total_orders": -1, "unique_products": -5,
        "customer_age_days": -100, "days_since_last_purchase": -10,
        "purchase_span_days": -50, "avg_days_between_orders": -5.0,
        "total_revenue": -500.0, "avg_revenue_per_item": -10.0,
        "revenue_std": -20.0, "max_revenue": -100.0,
        "recent_30d_revenue": -50.0, "repeat_product_ratio": -0.5,
        "customer_lifetime_days": -100, "purchase_rate": -0.01,
    }, "Giá trị âm"),

    ("string_in_features", {
        "Recency": "abc", "Frequency": "xyz", "Monetary": "N/A",
        "avg_order_value": None, "avg_items_per_order": "",
        "total_orders": 5, "unique_products": 10,
        "customer_age_days": 200, "days_since_last_purchase": 30,
        "purchase_span_days": 150, "avg_days_between_orders": 20.0,
        "total_revenue": 400.0, "avg_revenue_per_item": 40.0,
        "revenue_std": 30.0, "max_revenue": 200.0,
        "recent_30d_revenue": 50.0, "repeat_product_ratio": 0.3,
        "customer_lifetime_days": 150, "purchase_rate": 0.033,
    }, "Features chứa string thay vì số"),
]


# ══════════════════════════════════════════════════════════════════════════════
# RUNNER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def run_test(label, description, fn, *args):
    """Chạy 1 test case, bắt mọi exception và in kết quả."""
    print(f"\n  [{label}] {description}")
    try:
        result = fn(*args)
        ok(f"Passed → {result}")
        return True, result
    except Exception as e:
        fail(f"Failed → {type(e).__name__}: {e}")
        print(f"  {RED}{'─'*50}")
        traceback.print_exc()
        print(f"{'─'*50}{RESET}")
        return False, None


def summarize(name, passed, total):
    color = GREEN if passed == total else (YELLOW if passed > 0 else RED)
    print(f"\n  {color}[{name}] {passed}/{total} tests passed{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST AGENT 1 — Sentiment
# ══════════════════════════════════════════════════════════════════════════════
def test_sentiment_agent():
    section("AGENT 1 — SentimentAgent")

    # Kiểm tra load model
    try:
        from agents import SentimentAgent
        agent = SentimentAgent(str(SENTIMENT_MODEL_PATH))
        ok(f"Model loaded từ {SENTIMENT_MODEL_PATH}")
    except Exception as e:
        fail(f"Không load được model: {e}")
        return

    passed = 0
    for label, text, desc in SENTIMENT_CASES:
        success, result = run_test(label, desc, agent.analyze, text)
        if success:
            # Validate output schema
            assert "label" in result,      "Missing key: label"
            assert "confidence" in result, "Missing key: confidence"
            assert result["confidence"] >= 0 and result["confidence"] <= 1, \
                f"Confidence out of range: {result['confidence']}"
            passed += 1

    summarize("SentimentAgent", passed, len(SENTIMENT_CASES))


# ══════════════════════════════════════════════════════════════════════════════
# TEST AGENT 2 — Churn
# ══════════════════════════════════════════════════════════════════════════════
def test_churn_agent():
    section("AGENT 2 — ChurnAgent")

    try:
        from agents import ChurnAgent
        agent = ChurnAgent(str(CHURN_MODEL_PATH))
        ok(f"Model loaded từ {CHURN_MODEL_PATH}")
    except Exception as e:
        fail(f"Không load được model: {e}")
        return

    passed = 0
    for label, features, desc in CHURN_CASES:
        success, result = run_test(label, desc, agent.predict, features)
        if success:
            assert "churn_probability" in result, "Missing key: churn_probability"
            assert "risk_level" in result,        "Missing key: risk_level"
            assert result["risk_level"] in ("high","medium","low"), \
                f"Invalid risk_level: {result['risk_level']}"
            passed += 1

    summarize("ChurnAgent", passed, len(CHURN_CASES))


# ══════════════════════════════════════════════════════════════════════════════
# TEST AGENT 3 — Report (LLM)
# ══════════════════════════════════════════════════════════════════════════════
def test_report_agent():
    section("AGENT 3 — ReportAgent (LLM)")

    try:
        from agents import ReportAgent
        agent = ReportAgent()
        ok("ReportAgent initialized")
    except Exception as e:
        fail(f"Init failed: {e}")
        return

    cases = [
        ("normal", "C001",
         {"label": "negative", "confidence": 0.85, "proba": {}},
         {"churn_probability": 0.82, "churn_prediction": 1, "risk_level": "high"},
         "Input chuẩn - high risk negative"),

        ("positive_low_risk", "C002",
         {"label": "positive", "confidence": 0.91, "proba": {}},
         {"churn_probability": 0.12, "churn_prediction": 0, "risk_level": "low"},
         "Input chuẩn - low risk positive"),
    ]

    passed = 0
    for label, cid, sentiment, churn, desc in cases:
        success, result = run_test(
            label, desc, agent.generate, cid, sentiment, churn
        )
        if success:
            assert isinstance(result, str) and len(result) > 10, \
                "Report quá ngắn hoặc không phải string"
            ok(f"Report length: {len(result)} chars")
            passed += 1

    summarize("ReportAgent", passed, len(cases))


# ══════════════════════════════════════════════════════════════════════════════
# TEST AGENT 4 — Action
# ══════════════════════════════════════════════════════════════════════════════
def test_action_agent():
    section("AGENT 4 — ActionAgent (Rules + LLM)")

    try:
        from agents import ActionAgent
        agent = ActionAgent()
        ok("ActionAgent initialized")
    except Exception as e:
        fail(f"Init failed: {e}")
        return

    cases = [
        ("high_neg",  "C001",
         {"label": "negative", "confidence": 0.85, "proba": {}},
         {"churn_probability": 0.82, "churn_prediction": 1, "risk_level": "high"},
         "Báo cáo mẫu.", "Negative + High risk"),

        ("low_pos",   "C002",
         {"label": "positive", "confidence": 0.91, "proba": {}},
         {"churn_probability": 0.12, "churn_prediction": 0, "risk_level": "low"},
         "Báo cáo mẫu.", "Positive + Low risk"),
    ]

    passed = 0
    for label, cid, sentiment, churn, report, desc in cases:
        success, result = run_test(
            label, desc, agent.recommend, cid, sentiment, churn, report
        )
        if success:
            assert "rule_actions" in result, "Missing key: rule_actions"
            assert "priority" in result,     "Missing key: priority"
            assert "detail" in result,       "Missing key: detail"
            assert isinstance(result["rule_actions"], list), \
                "rule_actions phải là list"
            passed += 1

    summarize("ActionAgent", passed, len(cases))


# ══════════════════════════════════════════════════════════════════════════════
# TEST FULL PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def test_full_pipeline():
    section("FULL PIPELINE — End-to-end")

    try:
        from graph import pipeline
        ok("Pipeline compiled thành công")
    except Exception as e:
        fail(f"Pipeline compile failed: {e}")
        traceback.print_exc()
        return

    state = {
        "customer_id"      : "TEST_001",
        "review_text"      : "Giao hàng chậm, sản phẩm bị lỗi.",
        "features"         : {
            "Recency": 150, "Frequency": 2, "Monetary": 120.0,
            "avg_order_value": 60.0, "avg_items_per_order": 2.0,
            "total_orders": 2, "unique_products": 3,
            "customer_age_days": 400, "days_since_last_purchase": 150,
            "purchase_span_days": 100, "avg_days_between_orders": 100.0,
            "total_revenue": 120.0, "avg_revenue_per_item": 20.0,
            "revenue_std": 10.0, "max_revenue": 80.0,
            "recent_30d_revenue": 0.0, "repeat_product_ratio": 0.2,
            "customer_lifetime_days": 100, "purchase_rate": 0.02,
        },
        "sentiment_result" : None,
        "churn_result"     : None,
        "report"           : None,
        "action_plan"      : None,
        "error"            : None,
    }

    try:
        result = pipeline.invoke(state)
        if result.get("error"):
            fail(f"Pipeline error: {result['error']}")
        else:
            ok("Pipeline chạy thành công")
            ok(f"Sentiment : {result['sentiment_result']['label']}")
            ok(f"Churn prob: {result['churn_result']['churn_probability']}")
            ok(f"Risk level: {result['churn_result']['risk_level']}")
            ok(f"Report    : {len(result['report'])} chars")
            ok(f"Actions   : {result['action_plan']['rule_actions']}")
    except Exception as e:
        fail(f"Pipeline crashed: {e}")
        traceback.print_exc()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "█"*55)
    print("  MULTI-AGENT TEST SUITE")
    print("█"*55)

    test_sentiment_agent()   # Agent 1
    test_churn_agent()       # Agent 2
    test_report_agent()      # Agent 3 (cần API key)
    test_action_agent()      # Agent 4 (cần API key)
    test_full_pipeline()     # End-to-end

    print("\n" + "█"*55)
    print("  DONE")
    print("█"*55 + "\n")