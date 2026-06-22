from copy import deepcopy

class HarmonizationTool:
    """
    Customer Context Harmonization
    Chuẩn hóa Customer Profile để toàn bộ
    Feature Builder sử dụng cùng một schema.
    """
    def harmonize(self, customer_profile: dict) -> dict:
        customer_profile = deepcopy(customer_profile)
        orders = customer_profile.get("orders", [])
        customer_profile["orders"] = [
            self._harmonize_order(order)
            for order in orders
        ]
        return customer_profile

    def _harmonize_order(self, order: dict) -> dict:
        order = deepcopy(order)
        alias_map = {
            "Invoice":
                order.get("Invoice", order.get("order_id")),
            "InvoiceDate":
                order.get(
                    "InvoiceDate",
                    order.get("order_purchase_timestamp")
                ),
            "StockCode":
                order.get(
                    "StockCode",
                    order.get("product_id")
                ),
            "Quantity":
                order.get(
                    "Quantity",
                    order.get("quantity")
                ),
            "Price":
                order.get(
                    "Price",
                    order.get("price")
                ),
            "Revenue":
                order.get(
                    "Revenue",
                    order.get("total_payment")
                ),
            "order_value":
                order.get(
                    "order_value",
                    order.get("total_payment")
                ),
            "main_payment_type":
                order.get(
                    "main_payment_type",
                    order.get("payment_type")
                )
        }
        order.update(alias_map)
        self._fill_missing(order)
        return order
    
    def _fill_missing(self, order: dict) -> None:
        defaults = {
            "review_comment_message": "",
            "review_score": 0,
            "days_to_answer": 0,
            "delivery_time_days": 0,
            "delivery_delay": 0,
            "avg_freight": 0,
            "payment_installments": 0,
            "num_products": 0,
            "num_items": 0,
            "price": 0,
            "Price": 0,
            "Revenue": 0,
            "total_payment": 0,
            "order_value": 0,
            "Quantity": 0,
            "quantity": 0,
            "Invoice": "",
            "InvoiceDate": "",
            "StockCode": "",
            "payment_type": "",
            "main_payment_type": ""
        }
        for key, value in defaults.items():
            if key not in order:
                order[key] = value