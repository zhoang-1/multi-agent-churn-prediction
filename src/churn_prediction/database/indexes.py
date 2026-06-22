from connection import db

def create_indexes():
    db.customers.create_index("customer_id", unique=True)
    db.customers.create_index("email", unique=True)
    db.customers.create_index("phone")

    db.orders.create_index("order_id", unique=True)
    db.orders.create_index("customer_id")
    db.orders.create_index("order_status")
    db.orders.create_index("order_date")