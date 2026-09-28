"""Flask REST API: receives tickets, classifies them, stores and lists them."""
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.classifier import get_model, predict_category
from backend.database import get_all_tickets, insert_ticket

app = Flask(__name__)
CORS(app)

get_model()  # fail fast at startup if the model file is missing


@app.route("/")
def home():
    return jsonify({"message": "Intelligent Support Ticket Classifier API is running"})


@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    body = (data.get("body") or "").strip()

    if not subject and not body:
        return jsonify({"error": "Subject or body is required"}), 400
    if len(subject) + len(body) > 5000:
        return jsonify({"error": "Ticket is too long (max 5000 characters)"}), 400

    category = predict_category(subject, body)
    try:
        ticket = insert_ticket(subject, body, category)
    except Exception:
        return jsonify({"error": "Could not save ticket. Check the database connection."}), 503
    return jsonify({"message": "Ticket created successfully", "ticket": ticket}), 201


@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    try:
        return jsonify(get_all_tickets())
    except Exception:
        return jsonify({"error": "Could not load tickets. Check the database connection."}), 503


if __name__ == "__main__":
    app.run(debug=True)
