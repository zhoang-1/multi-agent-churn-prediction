import random
import sys
import os
from datetime import datetime, timedelta, timezone
from faker import Faker
from tqdm import tqdm

# Thêm thư mục hiện tại vào sys.path để import connection
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from connection import db

fake = Faker()

# --- Cấu hình ---
NUM_CUSTOMERS = 500
NUM_ORDERS = 4000
PRODUCT_COUNT = 200

# --- Dữ liệu mẫu ---
CATEGORIES = [
    "Electronics", "Clothing", "Home & Kitchen", "Books", "Toys",
    "Sports", "Automotive", "Health", "Beauty", "Groceries"
]
PAYMENT_METHODS = ["credit_card", "debit_card", "voucher", "pix", "boleto"]
CITIES = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Can Tho", "Hai Phong"]

POSITIVE = ["Excellent product.", "Very good quality.", "Fast delivery.", "Amazing service.", "Highly recommended."]
NEUTRAL = ["Product is okay.", "Normal quality.", "Average experience.", "Nothing special."]
NEGATIVE = ["Very disappointed.", "Late delivery.", "Poor quality.", "Terrible experience.", "Not recommended."]

def utc_now():
    return datetime.now(timezone.utc)

# --- 1. Xoá dữ liệu cũ (nếu muốn chạy lại từ đầu) ---
print("Xoá dữ liệu cũ trong collections (tuỳ chọn)...")
# Bỏ comment 2 dòng dưới nếu bạn muốn reset toàn bộ dữ liệu trước khi insert
# db.customers.delete_many({})
# db.orders.delete_many({})

# --- 2. Tạo danh mục sản phẩm ---
print("Đang tạo danh mục sản phẩm...")
products = []
for i in range(1, PRODUCT_COUNT + 1):
    products.append({
        "product_id": f"P{i:04d}",
        "product_name": fake.catch_phrase()[:30],
        "category": random.choice(CATEGORIES),
        "base_price": round(random.uniform(10, 500), 2)
    })

# --- 3. Phân bổ 4000 đơn hàng cho 500 khách ---
order_counts = [1] * NUM_CUSTOMERS
remaining = NUM_ORDERS - NUM_CUSTOMERS
while remaining > 0:
    idx = random.randint(0, NUM_CUSTOMERS - 1)
    if order_counts[idx] < 15:  # Giới hạn tối đa 15 đơn/khách để dữ liệu đa dạng
        order_counts[idx] += 1
        remaining -= 1

# --- 4. Sinh dữ liệu khách hàng và đơn hàng ---
print("Đang sinh dữ liệu khách hàng và đơn hàng...")
customers_to_insert = []
orders_to_insert = []
order_counter = 1

for cust_idx in tqdm(range(1, NUM_CUSTOMERS + 1), desc="Xử lý khách hàng"):
    customer_id = f"CUST{cust_idx:05d}"
    num_orders = order_counts[cust_idx - 1]
    total_spent = 0.0
    last_order_date = None

    # Tạo document khách hàng
    customer = {
        "customer_id": customer_id,
        "email": f"customer{cust_idx}@gmail.com",
        "phone": f"09{random.randint(10000000, 99999999)}",
        "full_name": fake.name(),
        "address": {
            "street": fake.street_name(),
            "ward": f"Ward {random.randint(1, 20)}",
            "district": f"District {random.randint(1, 12)}",
            "city": random.choice(CITIES)
        },
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "total_orders": num_orders,
        "total_spent": 0.0,
        "last_order_date": None
    }

    # Sinh đơn hàng cho khách này
    for _ in range(num_orders):
        days_ago = random.randint(1, 700)
        order_date = utc_now() - timedelta(days=days_ago)

        # Trạng thái dựa trên ngày tạo
        if days_ago < 7:
            status = random.choices(["pending", "processing", "shipped"], weights=[0.3, 0.4, 0.3])[0]
        elif days_ago < 30:
            status = random.choices(["shipped", "delivered"], weights=[0.2, 0.8])[0]
        else:
            status = random.choices(["delivered", "returned", "canceled"], weights=[0.8, 0.15, 0.05])[0]

        # Thanh toán
        method = random.choice(PAYMENT_METHODS)
        installments = random.randint(1, 12) if method in ["credit_card", "debit_card"] else 1

        # Giao hàng
        estimated_days = random.randint(1, 10)
        if status in ["delivered", "returned", "canceled"]:
            actual_days = max(1, estimated_days + random.randint(-2, 5))
            delivered_date = order_date if status == "delivered" else None
            delivery_delay = actual_days - estimated_days
        else:
            actual_days = estimated_days  # BẮT BUỘC phải là int (không được null)
            delivered_date = None
            delivery_delay = None

        freight_value = round(random.uniform(10, 50), 2)

        # Sản phẩm (1-3 món)
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, num_items)
        items = []
        total_items_price = 0.0
        for prod in selected_products:
            qty = random.randint(1, 5)
            unit_price = round(prod["base_price"] * random.uniform(0.8, 1.2), 2)
            total_price = round(unit_price * qty, 2)
            items.append({
                "product_id": prod["product_id"],
                "product_name": prod["product_name"],
                "category": prod["category"],
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": total_price
            })
            total_items_price += total_price

        total_payment = round(total_items_price + freight_value, 2)

        # Đánh giá (chỉ khi đã giao hàng)
        review = None
        if status == "delivered" and random.random() < 0.7:
            sentiment = random.random()
            if sentiment < 0.55:
                score = random.randint(4, 5)
                comment = random.choice(POSITIVE)
            elif sentiment < 0.80:
                score = 3
                comment = random.choice(NEUTRAL)
            else:
                score = random.randint(1, 2)
                comment = random.choice(NEGATIVE)
            review = {
                "score": score,
                "comment": comment,
                "comment_cleaned": comment,
                "answer_time_days": random.randint(0, 5) if random.random() < 0.5 else None
            }

        # Tạo document đơn hàng
        order = {
            "order_id": f"ORD{order_counter:06d}",
            "customer_id": customer_id,
            "order_date": order_date,          # Python datetime => pymongo tự chuyển thành BSON Date
            "order_status": status,
            "payment": {
                "method": method,
                "installments": installments,
                "total_payment": total_payment,
                "payment_sequence": []         # Schema yêu cầu là array (có thể rỗng)
            },
            "delivery": {
                "estimated_days": estimated_days,
                "actual_days": actual_days,    # Luôn là int
                "freight_value": freight_value,
                "delivered_date": delivered_date,  # datetime hoặc None
                "delivery_delay": delivery_delay   # int hoặc None
            },
            "items": items,
            "review": review,
            "created_at": utc_now(),
            "updated_at": utc_now()
        }

        orders_to_insert.append(order)
        order_counter += 1

        # Cập nhật tổng chi tiêu cho khách hàng
        total_spent += total_payment
        if last_order_date is None or order_date > last_order_date:
            last_order_date = order_date

    # Gán tổng chi tiêu và ngày mua cuối cho khách
    customer["total_spent"] = round(total_spent, 2)
    customer["last_order_date"] = last_order_date
    customers_to_insert.append(customer)

# --- 5. Insert vào MongoDB ---
print("\nĐang insert khách hàng vào MongoDB...")
try:
    result_cust = db.customers.insert_many(customers_to_insert)
    print(f"Đã insert thành công {len(result_cust.inserted_ids)} khách hàng.")
except Exception as e:
    print(f"Lỗi insert khách hàng: {e}")

print("Đang insert đơn hàng vào MongoDB...")
try:
    # insert_many với ordered=False để bỏ qua lỗi trùng lặp (nếu có)
    result_ord = db.orders.insert_many(orders_to_insert, ordered=False)
    print(f"Đã insert thành công {len(result_ord.inserted_ids)} đơn hàng.")
except Exception as e:
    print(f"Lỗi insert đơn hàng: {e}")

# --- 6. Kiểm tra ---
print("\n--- XÁC NHẬN ---")
print(f"Tổng khách hàng trong DB: {db.customers.count_documents({})}")
print(f"Tổng đơn hàng trong DB: {db.orders.count_documents({})}")
print("Hoàn tất!")