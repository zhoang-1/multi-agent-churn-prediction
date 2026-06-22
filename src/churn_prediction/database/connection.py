from pymongo import MongoClient
from dotenv import load_dotenv
from customer_schema import customer_schema
from order_schema import order_schema
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(MONGODB_URI)

db = client[DATABASE_NAME]

customers = db["customers"]
orders = db["orders"]
reports = db["reports"]
agent_logs = db["agent_logs"]