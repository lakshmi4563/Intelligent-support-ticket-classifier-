"""MongoDB access. The connection is created lazily so importing this module
(e.g. in tests) never needs a live database."""
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError(
                "MONGO_URI is not set. Copy .env.example to .env and fill it in."
            )
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _collection = client["support_ticket_db"]["tickets"]
    return _collection


def insert_ticket(subject: str, body: str, category: str) -> dict:
    timestamp = datetime.now(timezone.utc)
    result = get_collection().insert_one(
        {"subject": subject, "body": body, "category": category, "timestamp": timestamp}
    )
    return {
        "id": str(result.inserted_id),
        "subject": subject,
        "body": body,
        "category": category,
        "timestamp": timestamp.isoformat(),
    }


def get_all_tickets() -> list:
    return [
        {
            "id": str(t["_id"]),
            "subject": t.get("subject", ""),
            "body": t.get("body", ""),
            "category": t.get("category", ""),
            "timestamp": t["timestamp"].isoformat(),
        }
        for t in get_collection().find().sort("timestamp", -1)
    ]
