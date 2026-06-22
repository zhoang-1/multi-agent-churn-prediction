# agents/data_agent.py
import logging
import re
import json
from copy import deepcopy
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from ..services.customer_service import CustomerService
from ..core.llm_client import call_llm
from ..tools.customer_lookup_tools import CustomerLookupTools
from ..tools.harmonization_tool import HarmonizationTool
logger = logging.getLogger(__name__)

class CustomerDataAgent:
    """
    Customer Data Agent
    Đây là Agent đầu tiên trong pipeline.
    Nhiệm vụ:
    - Nhận order_input
    - Làm sạch dữ liệu
    - Dùng LLM chọn Tool
    - Truy vấn Customer
    - Chuẩn hóa Customer Context
    - Trả về Customer Profile
    """
    def __init__(self, customer_service: Optional[CustomerService] = None) -> None:
        self.customer_service = customer_service or CustomerService()
        self.harmonizer_tool = HarmonizationTool()
        self.lookup_tool = CustomerLookupTools( self.customer_service)
        self.SYSTEM_PROMPT = ""
        self._load_agent_specification()
        logger.info("CustomerDataAgent khởi tạo thành công.")

    def process(self, order_input: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry của Agent.
        Order Input-> clean data -> agentic data -> execute tool -> Harmonization ->Return customer_profile
        """
        logger.info("bắt đầu agent...")
        # clean review
        order_input = deepcopy(order_input)
        if "review_comment_message" in order_input:
            order_input["review_comment_message"] = (
                self._clean_review(
                    order_input.get(
                        "review_comment_message"
                    )
                )
            )
        logger.info("Input cleaned!")
        
        # Reasoning
        decision = self._agentic_lookup(order_input)
        # Action
        customer_profile = self.lookup_tool.execute(
            decision["chosen_tool"],
            decision["query_value"]
        )
        # không tìm thấy khách hàng
        if customer_profile is None:
            logger.warning(
                "Customer not found. "
                "Create profile from input."
            )
            customer_profile = (self.customer_service.create_profile_from_input(order_input))

        # Harmonization
        customer_profile = (self.harmonizer_tool.harmonize(customer_profile))
        logger.info("Customer Context created successfully")
        return customer_profile
    
    def _load_agent_specification(self, prompts_dir: str = "prompts"):
        """Đọc cấu hình/prompt từ file Đọc Prompt từ file data_agent_spec.md
            Chỉ lấy block  
            ```agent
            ...
            ```
        """
        prompt_file = Path(__file__).parent.parent / prompts_dir / "data_agent_spec.md"
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}"
            )

        content = prompt_file.read_text(
            encoding="utf-8"
        )

        match = re.search(
            r"```agent\s*(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE
        )
        if not match:
            raise ValueError(
                "Cannot find ```agent block "
                "inside data_agent_spec.md"
            )
        self.SYSTEM_PROMPT = match.group(1).strip()
        logger.info("prompt loaded.")
    
    def _clear_review(self, text : Optional[str]) -> str:
        """ CHuẩn hóa dữ liệu"""
        if not text:
            return ""

        text = str(text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()
    
 
    def _agentic_lookup(self, order_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent sẽ:
        1. Gọi LLM để quyết định Tool truy vấn.
        2. LLM trả về JSON
        {
            "reasoning": "...",
            "chosen_tool": "...",
            "query_value": "..."
        }
        3. Sau đó Python thực thi Tool.
        """

        available_fields = {
            key : value
            for key, value in order_input.items()
            if value not in (None, "", [], {})
        }

        user_prompt = f"""
        Đây là dữ liệu đầu vào:

        {json.dumps(available_fields, ensure_ascii=False, indent=2)}

        Hãy phân tích dữ liệu.
        Chọn Tool phù hợp nhất.
        Chỉ trả về JSON.
        """
        logger.info("Calling LLM for reasoning...")

        response = call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        logger.debug("LLM Response:\n%s", response)
        decision = self._extract_json(response)
        logger.info("LLM selected %s",decision.get("chosen_tool"))
        return decision
    
    def _execute_lookup(self, decision: dict[str,Any]) -> Optional[dict[str,Any]]:
        """ thực thi tool mà llm đã chọn
        Agent chỉ đóng vai trò điều phối (Orchestrator),
        việc truy vấn sẽ do CustomerLookupTool đảm nhiệm
        """
        tool_name = decision.get("chosen_tool")
        query_value = decision.get("query_value")

        logger.info( "Executing Tool: %s | Query: %s",tool_name,query_value)

        if tool_name == "NONE":
            logger.warning("LLM returned NONE.")
            return None

        if not query_value:
            logger.warning("Query value is empty.")
            return None
        
        try:
            customer_profile = self.lookup_tool.execute(
                tool_name=tool_name,
                query_value=query_value
            )
            if customer_profile:
                logger.info("Customer profile retrieved successfully.")
            else:
                logger.warning( "Customer profile not found.")
            return customer_profile

        except Exception as ex:
            logger.exception("Customer lookup failed: %s",ex)
            return None