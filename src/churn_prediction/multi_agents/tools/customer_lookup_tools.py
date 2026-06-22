from typing import Any, Dict, Optional
from services.customer_service import CustomerService
class CustomerLookupTools:
    """
    Customer Lookup Tool
    Tool chịu trách nhiệm truy vấn CustomerService.
    Data Agent sẽ chọn Tool bằng LLM.
    Tool này chỉ thực hiện Action.
    """
    def __init__(self, customer_service: Optional[CustomerService] = None):
        self.customer_service = (customer_service or CustomerService())
        self.tool_map = {
            "FIND_BY_ID": self.find_by_id,
            "FIND_BY_EMAIL": self.find_by_email,
            "FIND_BY_PHONE": self.find_by_phone,
            "FIND_BY_ORDER": self.find_by_order,
        }
    def execute(self, tool_name: str , query_value: str ) -> Optional[Dict[str, Any]]:
        tool = self.tool_map.get(tool_name)
        if tool is None:
            return None
        return tool(query_value)
    def find_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self.customer_service.get_profile_by_customer_id(customer_id)
    def find_by_phone(self,phone: str) -> Optional[Dict[str, Any]]:
        return self.customer_service.get_profile_by_phone(phone)
    def find_by_order(self,order_id: str) -> Optional[Dict[str, Any]]:
        return self.customer_service.get_profile_by_order_id(order_id)