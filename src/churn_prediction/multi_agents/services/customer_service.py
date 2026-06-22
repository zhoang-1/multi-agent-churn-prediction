# services/customer_service.py
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.connection import customers, orders

logger = logging.getLogger(__name__)

class CustomerService:
    def get_profile_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        customer = customers.find_one({"customer_id": customer_id})
        if not customer:
            return None
        customer["_id"] = str(customer["_id"])  # chuyển ObjectId thành string
        # Lấy danh sách đơn hàng
        order_list = list(orders.find({"customer_id": customer_id}).sort("order_date", -1))
        for o in order_list:
            o["_id"] = str(o["_id"])
        customer["orders"] = order_list
        return customer

    def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        customer = customers.find_one({"email": email})
        if not customer:
            return None
        customer["_id"] = str(customer["_id"])
        order_list = list(orders.find({"customer_id": customer["customer_id"]}).sort("order_date", -1))
        for o in order_list:
            o["_id"] = str(o["_id"])
        customer["orders"] = order_list
        return customer

    def get_profile_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        customer = customers.find_one({"phone": phone})
        if not customer:
            return None
        customer["_id"] = str(customer["_id"])
        order_list = list(orders.find({"customer_id": customer["customer_id"]}).sort("order_date", -1))
        for o in order_list:
            o["_id"] = str(o["_id"])
        customer["orders"] = order_list
        return customer

    def get_profile_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = orders.find_one({"order_id": order_id})
        if not order:
            return None
        customer_id = order.get("customer_id")
        if not customer_id:
            return None
        return self.get_profile_by_customer_id(customer_id)

    def get_orders_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        order_list = list(orders.find({"customer_id": customer_id}).sort("order_date", -1))
        for o in order_list:
            o["_id"] = str(o["_id"])
        return order_list

    def create_profile_from_input(self, order_input: dict) -> Dict[str, Any]:
        """Tạo mới hồ sơ khách hàng từ input (khi chưa tìm thấy)"""
        from datetime import datetime
        customer_id = order_input.get("customer_id") or f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_customer = {
            "customer_id": customer_id,
            "email": order_input.get("email"),
            "phone": order_input.get("phone"),
            "full_name": order_input.get("full_name"),
            "address": order_input.get("address", {}),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_orders": 0,
            "total_spent": 0.0,
            "last_order_date": None
        }
        # Lưu vào DB
        customers.insert_one(new_customer)
        logger.info(f"Tạo mới khách hàng: {customer_id}")
        # Trả về profile (không có orders)
        new_customer["_id"] = str(new_customer["_id"])
        new_customer["orders"] = []
        return new_customer