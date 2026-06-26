# agents/report_agent.py
import re
from pathlib import Path
from ..core.llm_client import call_llm

class ReportAgent:
    def __init__(self, prompts_dir: str = "prompts"):
        # Đọc SYSTEM_PROMPT từ file markdown
        prompt_file = Path(__file__).parent.parent / prompts_dir / "report_system.md"
        if prompt_file.exists():
            content = prompt_file.read_text(encoding="utf-8")
            # Trích xuất phần nội dung giữa cặp ba dấu backticks (``` ... ```)
            match = re.search(r"```(.*?)```", content, re.DOTALL)
            if match:
                self.SYSTEM_PROMPT = match.group(1).strip()
            else:
                # Nếu không tìm thấy, lấy toàn bộ nội dung (loại bỏ frontmatter)
                lines = content.splitlines()
                start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("```"):
                        start = i + 1
                        break
                self.SYSTEM_PROMPT = "\n".join(lines[start:]).strip()
        else:
            # Fallback nếu file không tồn tại
            self.SYSTEM_PROMPT = """Bạn là chuyên gia phân tích khách hàng thương mại điện tử.
Bạn nhận 2 nguồn dữ liệu độc lập:
1. Kết quả phân tích cảm xúc từ reviews (Olist dataset)
2. Kết quả dự đoán churn từ hành vi mua hàng (Online Retail II dataset)

Hãy tổng hợp thành báo cáo ngắn gọn bằng tiếng Việt gồm:
1. Tổng quan tình trạng trải nghiệm khách hàng (từ sentiment)
2. Tổng quan rủi ro rời bỏ (từ churn)
3. Nhận định chung và mức độ ưu tiên hành động
Giữ dưới 300 từ."""

    def generate(self,
                 sentiment_result: dict,
                 churn_result: dict) -> str:
        user_msg = f"""
=== KẾT QUẢ PHÂN TÍCH CẢM XÚC (Olist) ===
{self._format_dict(sentiment_result)}

=== KẾT QUẢ DỰ ĐOÁN CHURN (Online Retail II) ===
{self._format_dict(churn_result)}

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