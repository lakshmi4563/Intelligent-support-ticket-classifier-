from unittest.mock import patch

from backend.app import app

VALID_CATEGORIES = {"Technical", "Billing", "General Inquiry"}


def fake_insert(subject, body, category):
    return {"id": "test_id", "subject": subject, "body": body,
            "category": category, "timestamp": "2026-01-01T00:00:00+00:00"}


def test_home():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert "running" in response.get_json()["message"]


@patch("backend.app.insert_ticket", side_effect=fake_insert)
def test_create_billing_ticket(mock_insert):
    response = app.test_client().post(
        "/api/tickets",
        json={"subject": "Payment issue", "body": "I was charged twice for my subscription"},
    )
    assert response.status_code == 201
    assert response.get_json()["ticket"]["category"] == "Billing"
    mock_insert.assert_called_once()


@patch("backend.app.insert_ticket", side_effect=fake_insert)
def test_category_is_always_valid(mock_insert):
    response = app.test_client().post(
        "/api/tickets",
        json={"subject": "Return policy", "body": "Can I return an opened item after 30 days?"},
    )
    assert response.get_json()["ticket"]["category"] in VALID_CATEGORIES


def test_empty_ticket_rejected():
    response = app.test_client().post("/api/tickets", json={"subject": "", "body": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Subject or body is required"


def test_invalid_json_rejected():
    response = app.test_client().post("/api/tickets", data="not json",
                                      content_type="text/plain")
    assert response.status_code == 400


@patch("backend.app.insert_ticket", side_effect=RuntimeError("db down"))
def test_database_failure_returns_503(mock_insert):
    response = app.test_client().post("/api/tickets", json={"subject": "Hi", "body": "Test"})
    assert response.status_code == 503


@patch("backend.app.get_all_tickets", return_value=[])
def test_list_tickets(mock_get):
    response = app.test_client().get("/api/tickets")
    assert response.status_code == 200
    assert response.get_json() == []
