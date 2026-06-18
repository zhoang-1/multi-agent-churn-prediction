# Agent 0 – Data Agent (Tiền xử lý)

## 🎯 Mục tiêu
Đóng vai trò là **tầng hợp nhất dữ liệu** duy nhất.  
Chuẩn hóa đầu vào, làm sạch review, và chuẩn bị profile khách hàng trước khi gửi đến các Agent phân tích chuyên sâu.

## 📥 Định dạng đầu vào (Input)
```json
{
  "order_input": {
    "customer_id": "string (bắt buộc)",
    "review_comment_message": "string (có thể rỗng)",
    "order_purchase_timestamp": "ISO 8601 datetime",
    "price": "float (optional)",
    "product_category": "string (optional)"
  }
}