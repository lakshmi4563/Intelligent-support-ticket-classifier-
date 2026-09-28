"""Quick check that MONGO_URI works. Run: python scripts/check_mongo_connection.py"""
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
if not uri:
    raise SystemExit("MONGO_URI is not set. Copy .env.example to .env and fill it in.")
try:
    MongoClient(uri, serverSelectionTimeoutMS=5000).admin.command("ping")
    print("MongoDB connection successful!")
except Exception as e:
    raise SystemExit(f"MongoDB connection failed: {e}")
