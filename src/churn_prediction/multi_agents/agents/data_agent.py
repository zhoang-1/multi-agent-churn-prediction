# agents/data_agent.py
class CustomerDataAgent:
    def __init__(self):
        pass  # Có thể thêm DB connection sau

    def process(self, order_input: dict) -> tuple:
        """
        Chuẩn hóa dữ liệu, trả về (customer_profile, sentiment_result).
        """
        if not order_input:
            return {}, {}

        # 1. Chuẩn hóa review_text
        review_text = order_input.get("review_comment_message", "")
        order_input["review_comment_message"] = str(review_text).strip()

        # 2. Tạo customer_profile (giả lập, bạn có thể lưu DB ở đây)
        customer_profile = {
            "customer_id": order_input.get("customer_id", "unknown"),
            "total_orders": 1,  # Giả định
            "total_spent": 0.0,
            "last_order_date": order_input.get("order_purchase_timestamp"),
        }

        # 3. Lấy sentiment_result (nếu có review_text)
        sentiment_result = None
        if review_text:
            # Gợi ý: có thể gọi sentiment_agent ở đây, 
            # NHƯNG trong kiến trúc multi-agent, Data Agent chỉ nên prep data.
            # Để đơn giản, tôi trả về review_text đã chuẩn hóa để Agent 1 xử lý sau.
            sentiment_result = {"cleaned_review": review_text}

        return customer_profile, sentiment_result