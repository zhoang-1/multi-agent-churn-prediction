# agents/data_agent.py
import logging
import re
from copy import deepcopy
from typing import Dict, Any, Optional
from pathlib import Path
from ..services.customer_service import CustomerService
from ..tools.customer_lookup_tools import CustomerLookupTools
from ..tools.harmonization_tool import HarmonizationTool

logger = logging.getLogger(__name__)

class CustomerDataAgent:
    """
    Customer Data Agent (không dùng LLM)
    Nhiệm vụ:
    - Nhận order_input
    - Làm sạch dữ liệu
    - Tự động chọn Tool truy vấn dựa trên thông tin có sẵn
    - Truy vấn Customer
    - Chuẩn hóa Customer Context
    - Trả về Customer Profile
    """
    def __init__(self, customer_service: Optional[CustomerService] = None) -> None:
        self.customer_service = customer_service or CustomerService()
        self.harmonizer_tool = HarmonizationTool()
        self.lookup_tool = CustomerLookupTools(self.customer_service)
        logger.info("CustomerDataAgent khởi tạo thành công (không dùng LLM).")

    def process(self, order_input: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry của Agent."""
        logger.info("Bắt đầu agent...")
        # Làm sạch review
        order_input = deepcopy(order_input)
        if "review_comment_message" in order_input:
            order_input["review_comment_message"] = (
                self._clean_review(order_input.get("review_comment_message"))
            )
        logger.info("Input cleaned!")

        # Tự động chọn tool (không dùng LLM)
        decision = self._agentic_lookup(order_input)
        # Thực thi tool
        customer_profile = self.lookup_tool.execute(
            decision["chosen_tool"],
            decision["query_value"]
        )

        # Nếu không tìm thấy, tạo profile mới từ input
        if customer_profile is None:
            logger.warning("Customer not found. Create profile from input.")
            customer_profile = self.customer_service.create_profile_from_input(order_input)

        # Chuẩn hóa
        customer_profile = self.harmonizer_tool.harmonize(customer_profile)
        logger.info("Customer Context created successfully")
        return customer_profile

    def _clean_review(self, text: Optional[str]) -> str:
        """Làm sạch nội dung review."""
        if text is None:
            return ""
        text = str(text)
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").replace("\r", " ")
        return text.strip()

    def _agentic_lookup(self, order_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tự động chọn tool dựa trên dữ liệu đầu vào.
        Ưu tiên: customer_id > email > phone > order_id
        """
        # Lọc các trường có giá trị
        available = {k: v for k, v in order_input.items() if v not in (None, "", [], {})}

        # Thứ tự ưu tiên
        tool_rules = [
            ("FIND_BY_ID", "customer_id"),
            ("FIND_BY_EMAIL", "email"),
            ("FIND_BY_PHONE", "phone"),
            ("FIND_BY_ORDER", "order_id"),
        ]

        for tool_name, key in tool_rules:
            if key in available:
                query_value = available[key]
                logger.info(f"Chọn tool {tool_name} với giá trị {query_value}")
                return {
                    "reasoning": f"Tìm thấy {key} trong input",
                    "chosen_tool": tool_name,
                    "query_value": query_value,
                }

        # Không có thông tin định danh
        logger.warning("Không có thông tin định danh khách hàng, trả về NONE")
        return {
            "reasoning": "Không có customer_id, email, phone, order_id",
            "chosen_tool": "NONE",
            "query_value": "",
        }