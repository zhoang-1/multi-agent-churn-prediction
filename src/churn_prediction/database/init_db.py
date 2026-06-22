import os
import sys

# Tự động thêm thư mục hiện tại của file vào danh sách tìm kiếm của Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from connection import db
from customer_schema import customer_schema
from order_schema import order_schema
from indexes import create_indexes

if "customers" not in db.list_collection_names():
    db.create_collection(
        "customers",
        validator=customer_schema
    )

if "orders" not in db.list_collection_names():
    db.create_collection(
        "orders",
        validator=order_schema
    )

create_indexes()

print("Database initialized successfully!")