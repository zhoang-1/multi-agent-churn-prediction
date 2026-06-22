from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
try:
    print('URI:', os.getenv('MONGODB_URI'))
    client = MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=2000)
    client.server_info()
    print('DB connection successful')
except Exception as e:
    print('DB connection failed:', e)
