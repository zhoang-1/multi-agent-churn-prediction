import random
import sys
import os
from datetime import datetime, timedelta, timezone
from faker import Faker
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from connection import db

fake = Faker()

# --- Cấu hình ---
NUM_CUSTOMERS = 500
# Mỗi khách có từ 20-30 đơn -> tổng ~ 12.500
MIN_ORDERS_PER_CUSTOMER = 20
MAX_ORDERS_PER_CUSTOMER = 30
PRODUCT_COUNT = 200

# --- Khoảng thời gian để tạo đơn hàng (tất cả đều cũ, không có đơn gần đây) ---
# Chúng ta sẽ tạo đơn từ 6 tháng trước đến 2 tháng trước (tính từ hiện tại)
# Điều này tạo hiệu ứng churn: khách hàng không mua gì trong 2 tháng cuối.
END_DATE_OFFSET_DAYS = 60   # 2 tháng trước
START_DATE_OFFSET_DAYS = 180 # 6 tháng trước

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

# --- 1. Xoá dữ liệu cũ nếu cần ---
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

# --- 3. Xác định số đơn hàng cho mỗi khách (từ 20 đến 30) ---
order_counts = []
total_orders = 0
for _ in range(NUM_CUSTOMERS):
    cnt = random.randint(MIN_ORDERS_PER_CUSTOMER, MAX_ORDERS_PER_CUSTOMER)
    order_counts.append(cnt)
    total_orders += cnt

print(f"Tổng số đơn hàng sẽ được tạo: {total_orders}")

# --- 4. Sinh dữ liệu khách hàng và đơn hàng ---
print("Đang sinh dữ liệu khách hàng và đơn hàng...")
customers_to_insert = []
orders_to_insert = []
order_counter = 1

# Các mốc thời gian
now = utc_now()
start_date = now - timedelta(days=START_DATE_OFFSET_DAYS)
end_date = now - timedelta(days=END_DATE_OFFSET_DAYS)
# Đảm bảo start_date < end_date
if start_date >= end_date:
    # fallback
    start_date = now - timedelta(days=180)
    end_date = now - timedelta(days=60)

# Hàm chọn ngẫu nhiên một ngày trong khoảng [start_date, end_date]
def random_order_date():
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

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

    # Sinh đơn hàng cho khách này – tất cả đều trong khoảng thời gian cũ
    for _ in range(num_orders):
        order_date = random_order_date()

        # Vì đơn hàng đều cũ (> 2 tháng), nên trạng thái chỉ có thể là delivered, returned, canceled
        status = random.choices(["delivered", "returned", "canceled"], weights=[0.8, 0.15, 0.05])[0]

        # Thanh toán
        method = random.choice(PAYMENT_METHODS)
        installments = random.randint(1, 12) if method in ["credit_card", "debit_card"] else 1

        # Giao hàng – đã hoàn tất
        estimated_days = random.randint(1, 10)
        actual_days = max(1, estimated_days + random.randint(-2, 5))
        delivered_date = order_date if status == "delivered" else None
        delivery_delay = actual_days - estimated_days
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
            "order_date": order_date,
            "order_status": status,
            "payment": {
                "method": method,
                "installments": installments,
                "total_payment": total_payment,
                "payment_sequence": []
            },
            "delivery": {
                "estimated_days": estimated_days,
                "actual_days": actual_days,
                "freight_value": freight_value,
                "delivered_date": delivered_date,
                "delivery_delay": delivery_delay
            },
            "items": items,
            "review": review,
            "created_at": utc_now(),
            "updated_at": utc_now()
        }

        orders_to_insert.append(order)
        order_counter += 1

        # Cập nhật tổng chi tiêu
        total_spent += total_payment
        if last_order_date is None or order_date > last_order_date:
            last_order_date = order_date

    # Gán tổng chi tiêu và ngày mua cuối
    customer["total_spent"] = round(total_spent, 2)
    customer["last_order_date"] = last_order_date
    customers_to_insert.append(customer)

# --- 5. Insert vào MongoDB ---
print("\nĐang insert khách hàng...")
try:
    result_cust = db.customers.insert_many(customers_to_insert)
    print(f"✅ Insert thành công {len(result_cust.inserted_ids)} khách hàng.")
except Exception as e:
    print(f"❌ Lỗi: {e}")

print("Đang insert đơn hàng...")
try:
    result_ord = db.orders.insert_many(orders_to_insert, ordered=False)
    print(f"✅ Insert thành công {len(result_ord.inserted_ids)} đơn hàng.")
except Exception as e:
    print(f"❌ Lỗi: {e}")

# --- 6. Kiểm tra ---
print("\n--- XÁC NHẬN ---")
print(f"Tổng khách hàng: {db.customers.count_documents({})}")
print(f"Tổng đơn hàng: {db.orders.count_documents({})}")

# Kiểm tra ngày tháng của đơn hàng mới nhất
latest_order = db.orders.find_one(sort=[("order_date", -1)])
if latest_order:
    print(f"Ngày đơn hàng mới nhất: {latest_order['order_date']}")

print("Hoàn tất! 🎉")