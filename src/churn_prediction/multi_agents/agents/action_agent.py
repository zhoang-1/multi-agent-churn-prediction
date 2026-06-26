# agents/action_agent.py
import json
import re
from pathlib import Path
from ..core.llm_client import call_llm

class ActionAgent:
    def __init__(self, config_dir: str = "config", prompts_dir: str = "prompts"):
        # ── 1. Đọc rule_actions từ file JSON ──
        rules_path = Path(__file__).parent.parent / config_dir / "action_rules.json"
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                raw_rules = json.load(f)
            self.RULE_ACTIONS = {}
            for key, actions in raw_rules.items():
                parts = key.split("_")
                if len(parts) == 2:
                    sentiment, risk = parts[0], parts[1]
                    self.RULE_ACTIONS[(sentiment, risk)] = actions
                else:
                    # Bỏ qua key không đúng định dạng
                    continue
        else:
            # Fallback nếu không có file
            self.RULE_ACTIONS = {
                ("negative", "high"): ["Cải thiện chất lượng sản phẩm/dịch vụ ngay"],
                ("negative", "medium"): ["Gửi email xin lỗi + voucher"],
                ("negative", "low"): ["Theo dõi xu hướng sentiment"],
                ("neutral", "high"): ["Chương trình loyalty khẩn cấp"],
                ("neutral", "medium"): ["Newsletter sản phẩm mới"],
                ("neutral", "low"): ["Tăng engagement qua content"],
                ("positive", "high"): ["VIP program"],
                ("positive", "medium"): ["Tích điểm đổi quà"],
                ("positive", "low"): ["Duy trì trải nghiệm tốt"],
            }

        # ── 2. Đọc SYSTEM_PROMPT từ file .md ──
        prompt_file = Path(__file__).parent.parent / prompts_dir / "action.md"
        if prompt_file.exists():
            content = prompt_file.read_text(encoding="utf-8")
            # Trích xuất phần nội dung giữa cặp ba dấu backticks (``` ... ```)
            match = re.search(r"```(.*?)```", content, re.DOTALL)
            if match:
                self.SYSTEM_PROMPT = match.group(1).strip()
            else:
                # Nếu không tìm thấy, lấy toàn bộ nội dung (loại bỏ frontmatter)
                # Đơn giản: lấy sau dòng "```" (nếu có)
                lines = content.splitlines()
                start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("```"):
                        start = i + 1
                        break
                self.SYSTEM_PROMPT = "\n".join(lines[start:]).strip()
        else:
            # Fallback nếu file không tồn tại
            self.SYSTEM_PROMPT = """Bạn là chuyên gia CRM thương mại điện tử.
Dựa trên báo cáo tổng hợp từ 2 nguồn dữ liệu (sentiment + churn),
hãy đề xuất kế hoạch hành động cụ thể, thực tế bằng tiếng Việt.
Chia thành: Hành động ngay (0-7 ngày), Ngắn hạn (1 tháng), Dài hạn (3 tháng)."""

    def recommend(self,
                  sentiment_result: dict,
                  churn_result: dict,
                  report: str) -> dict:
        """
        Tạo kế hoạch hành động dựa trên tổng hợp sentiment + churn.
        """
        dominant_sentiment = sentiment_result.get("dominant_label", "neutral")
        dominant_risk      = churn_result.get("dominant_risk", "medium")

        key = (dominant_sentiment, dominant_risk)
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
        detail = call_llm(self.SYSTEM_PROMPT, user_msg)

        return {
            "rule_actions"      : rule_actions,
            "dominant_sentiment": dominant_sentiment,
            "dominant_risk"     : dominant_risk,
            "priority"          : dominant_risk,
            "detail"            : detail,
        }