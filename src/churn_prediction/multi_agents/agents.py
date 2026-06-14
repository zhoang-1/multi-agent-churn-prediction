# agents.py — 4 agents khớp với 2 pipeline độc lập
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import joblib
import pandas as pd
import numpy as np
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client       = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-2.5-flash"

def call_llm(system_prompt: str, user_prompt: str) -> str:
    prompt = f"""
{system_prompt}

------------------------
{user_prompt}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text
# ══════════════════════════════════════════════════════════════════════════════
# AGENT 1 — Sentiment (Olist dataset)
# ══════════════════════════════════════════════════════════════════════════════
class SentimentAgent:
    def __init__(self, model_path: str):
        self.pipeline  = joblib.load(model_path)
        # Điều chỉnh label_map theo thứ tự class lúc bạn train
        self.label_map = {0: "negative", 1: "neutral", 2: "positive"}

    def analyze(self, review_text: str) -> dict:
        if not review_text or not str(review_text).strip():
            return {"label": "unknown", "confidence": 0.0,
                    "error": "empty review"}
        try:
            proba     = self.pipeline.predict_proba([str(review_text)])[0]
            label_idx = int(np.argmax(proba))
            return {
                "label"     : self.label_map.get(label_idx, str(label_idx)),
                "confidence": round(float(proba[label_idx]), 4),
                "proba"     : {
                    self.label_map.get(i, str(i)): round(float(p), 4)
                    for i, p in enumerate(proba)
                },
            }
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 2 — Churn (Online Retail II dataset)
# ══════════════════════════════════════════════════════════════════════════════
class ChurnAgent:
    RISK_THRESHOLDS = {"high": 0.7, "medium": 0.4}

    def __init__(self, model_path: str):
        self.pipeline = joblib.load(model_path)

    def predict(self, features: dict) -> dict:
        if not features:
            return {"churn_probability": None, "churn_prediction": None,
                    "risk_level": None, "error": "empty features"}
        try:
            X = pd.DataFrame([features])
            X = X.select_dtypes(include=[np.number])
            churn_proba = float(self.pipeline.predict_proba(X)[0][1])
            churn_pred  = int(self.pipeline.predict(X)[0])
            risk = ("high"   if churn_proba >= self.RISK_THRESHOLDS["high"]
                    else "medium" if churn_proba >= self.RISK_THRESHOLDS["medium"]
                    else "low")
            return {
                "churn_probability": round(churn_proba, 4),
                "churn_prediction" : churn_pred,
                "risk_level"       : risk,
            }
        except Exception as e:
            return {"churn_probability": None, "churn_prediction": None,
                    "risk_level": None, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 3 — Report: nhận SUMMARY của 2 dataset, không phải 1 customer
# ══════════════════════════════════════════════════════════════════════════════
class ReportAgent:
    SYSTEM_PROMPT = """Bạn là chuyên gia phân tích khách hàng thương mại điện tử.
Bạn nhận 2 nguồn dữ liệu độc lập:
1. Kết quả phân tích cảm xúc từ reviews (Olist dataset)
2. Kết quả dự đoán churn từ hành vi mua hàng (Online Retail II dataset)

Hãy tổng hợp thành báo cáo ngắn gọn bằng tiếng Việt gồm:
1. Tổng quan tình trạng trải nghiệm khách hàng (từ sentiment)
2. Tổng quan rủi ro rời bỏ (từ churn)
3. Nhận định chung và mức độ ưu tiên hành động
Giữ dưới 300 từ."""

    def generate(self,
                 sentiment_summary: dict,
                 churn_summary: dict) -> str:
        user_msg = f"""
=== KẾT QUẢ PHÂN TÍCH CẢM XÚC (Olist) ===
{self._format_dict(sentiment_summary)}

=== KẾT QUẢ DỰ ĐOÁN CHURN (Online Retail II) ===
{self._format_dict(churn_summary)}

Hãy viết báo cáo tổng hợp từ 2 nguồn dữ liệu trên.
"""
        return call_llm(
            self.SYSTEM_PROMPT,
            user_msg
        )
    def _format_dict(self, d: dict) -> str:
        if not d:
            return "Không có dữ liệu"
        return "\n".join(f"  - {k}: {v}" for k, v in d.items())


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 4 — Action: đề xuất dựa trên tổng hợp 2 nguồn
# ══════════════════════════════════════════════════════════════════════════════
class ActionAgent:
    # Rule-based theo (dominant_sentiment, dominant_risk)
    RULE_ACTIONS = {
        ("negative", "high")  : ["Cải thiện chất lượng sản phẩm/dịch vụ ngay",
                                  "Chiến dịch win-back với ưu đãi đặc biệt",
                                  "Khảo sát nguyên nhân rời bỏ"],
        ("negative", "medium"): ["Gửi email xin lỗi + voucher",
                                  "Cải thiện quy trình giao hàng"],
        ("negative", "low")   : ["Theo dõi xu hướng sentiment",
                                  "Cải thiện mô tả sản phẩm"],
        ("neutral",  "high")  : ["Chương trình loyalty khẩn cấp",
                                  "Cá nhân hóa trải nghiệm mua sắm"],
        ("neutral",  "medium"): ["Newsletter sản phẩm mới",
                                  "Ưu đãi thành viên"],
        ("neutral",  "low")   : ["Tăng engagement qua content"],
        ("positive", "high")  : ["VIP program",
                                  "Early access sản phẩm mới",
                                  "Chương trình referral"],
        ("positive", "medium"): ["Tích điểm đổi quà",
                                  "Upsell sản phẩm liên quan"],
        ("positive", "low")   : ["Duy trì trải nghiệm tốt",
                                  "Khuyến khích review"],
    }

    SYSTEM_PROMPT = """Bạn là chuyên gia CRM thương mại điện tử.
Dựa trên báo cáo tổng hợp từ 2 nguồn dữ liệu (sentiment + churn),
hãy đề xuất kế hoạch hành động cụ thể, thực tế bằng tiếng Việt.
Chia thành: Hành động ngay (0-7 ngày), Ngắn hạn (1 tháng), Dài hạn (3 tháng)."""

    def recommend(self,
                  sentiment_summary: dict,
                  churn_summary: dict,
                  report: str) -> dict:

        # Lấy dominant sentiment và risk từ summary
        dominant_sentiment = sentiment_summary.get("dominant_label", "neutral")
        dominant_risk      = churn_summary.get("dominant_risk", "medium")

        key          = (dominant_sentiment, dominant_risk)
        rule_actions = self.RULE_ACTIONS.get(key, ["Phân tích thêm dữ liệu"])

        user_msg = f"""
Báo cáo tổng hợp:
{report}

Thông tin bổ sung:
- Sentiment chủ đạo  : {dominant_sentiment}
- Rủi ro churn chủ đạo: {dominant_risk}
- Hành động đề xuất (rule-based): {', '.join(rule_actions)}

Hãy xây dựng kế hoạch hành động chi tiết theo 3 giai đoạn.
"""
        detail = call_llm(
            self.SYSTEM_PROMPT,
            user_msg
        )

        return {
            "rule_actions"      : rule_actions,
            "dominant_sentiment": dominant_sentiment,
            "dominant_risk"     : dominant_risk,
            "priority"          : dominant_risk,
            "detail"            : detail,
        }