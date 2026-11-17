from datetime import datetime, timezone

from app.repositories import ai_repository, ticket_repository
from app.services import ai_service


def ticket_record(**overrides):
    record = {
        "ticket_id": 41,
        "requester_id": 12,
        "requester_name": "Avery Employee",
        "requester_email": "avery@example.test",
        "title": "Keyboard is not responding",
        "description": "The wireless keyboard stopped responding.",
        "category": "HARDWARE",
        "priority": "MEDIUM",
        "status": "OPEN",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    record.update(overrides)
    return record


def test_create_ticket_returns_requester_information(client, monkeypatch):
    monkeypatch.setattr(
        ticket_repository,
        "create_ticket",
        lambda conn, data: ticket_record(**data),
    )

    response = client.post(
        "/tickets/",
        json={
            "requester_id": 12,
            "title": "Keyboard is not responding",
            "description": "The wireless keyboard stopped responding.",
            "category": "HARDWARE",
        },
    )

    assert response.status_code == 201
    assert response.json()["requester_name"] == "Avery Employee"
    assert response.json()["requester_email"] == "avery@example.test"


def test_create_ticket_rejects_missing_required_fields(client):
    response = client.post("/tickets/", json={"requester_id": 12})

    assert response.status_code == 422
    assert {error["loc"][-1] for error in response.json()["detail"]} >= {
        "title",
        "description",
    }


def test_status_update_returns_updated_ticket(client, monkeypatch):
    monkeypatch.setattr(
        ticket_repository,
        "update_ticket_status",
        lambda **kwargs: ticket_record(status=kwargs["new_status"]),
    )

    response = client.patch(
        "/tickets/41/status",
        json={"status": "IN_PROGRESS", "updated_by": 27},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"
    assert response.json()["requester_email"] == "avery@example.test"


def test_ai_model_unavailable_does_not_break_ticket_api(client, monkeypatch):
    monkeypatch.setattr(
        ticket_repository,
        "get_ticket_by_id",
        lambda conn, ticket_id: ticket_record(),
    )
    monkeypatch.setattr(ai_repository, "get_recent_tickets", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        ai_service,
        "format_ticket_analysis_prompt",
        lambda **kwargs: type("Prompt", (), {"to_string": lambda self: "prompt"})(),
    )

    def unavailable_model():
        raise RuntimeError("model is offline")

    monkeypatch.setattr(ai_service, "get_llm", unavailable_model)

    response = client.post("/api/tickets/41/analyze")

    assert response.status_code == 503
    assert "model is offline" in response.json()["detail"]

    monkeypatch.setattr(
        ticket_repository,
        "create_ticket",
        lambda conn, data: ticket_record(**data),
    )
    create_response = client.post(
        "/tickets/",
        json={
            "requester_id": 12,
            "title": "Keyboard is not responding",
            "description": "The wireless keyboard stopped responding.",
        },
    )
    assert create_response.status_code == 201


def test_feedback_correction_saves_final_values(client, monkeypatch):
    monkeypatch.setattr(
        ai_repository,
        "get_ai_suggestion_by_id",
        lambda conn, suggestion_id: {
            "suggestion_id": suggestion_id,
            "ticket_id": 41,
            "suggested_category": "SOFTWARE",
            "suggested_priority": "LOW",
        },
    )
    monkeypatch.setattr(
        ai_repository,
        "get_active_support_staff",
        lambda conn, staff_id: {"staff_id": staff_id},
    )
    saved = {}

    def save_feedback(
        conn,
        suggestion_id,
        feedback,
        final_category,
        final_priority,
    ):
        saved["final_category"] = final_category
        saved["final_priority"] = final_priority
        return {
            "feedback_id": 3,
            "suggestion_id": suggestion_id,
            "reviewed_by": feedback["reviewed_by"],
            "is_useful": feedback["is_useful"],
            "decision": feedback["decision"],
            "corrected_category": feedback["corrected_category"],
            "corrected_priority": feedback["corrected_priority"],
            "final_category": final_category,
            "final_priority": final_priority,
            "comments": feedback["comments"],
        }

    monkeypatch.setattr(ai_repository, "save_ai_feedback", save_feedback)

    response = client.post(
        "/api/ai-suggestions/7/feedback",
        json={
            "reviewed_by": 27,
            "is_useful": True,
            "corrected_category": "HARDWARE",
            "comments": "Corrected after review.",
        },
    )

    assert response.status_code == 201
    assert response.json()["decision"] == "CORRECTED"
    assert response.json()["final_category"] == "HARDWARE"
    assert response.json()["final_priority"] == "LOW"
    assert saved == {
        "final_category": "HARDWARE",
        "final_priority": "LOW",
    }


def test_feedback_repository_applies_final_values_to_ticket():
    class Cursor:
        def __init__(self):
            self.queries = []
            self.current_query = ""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, query, params):
            self.current_query = query
            self.queries.append((query, params))

        def fetchone(self):
            if "SELECT t.ticket_id" in self.current_query:
                return {"ticket_id": 41, "category": "SOFTWARE", "priority": "LOW"}
            if "INSERT INTO ai_feedback" in self.current_query:
                return {"feedback_id": 5}
            return None

    class Connection:
        def __init__(self):
            self.test_cursor = Cursor()

        def cursor(self):
            return self.test_cursor

    connection = Connection()
    ai_repository.save_ai_feedback(
        connection,
        7,
        {
            "reviewed_by": 27,
            "is_useful": True,
            "decision": "CORRECTED",
            "corrected_category": "HARDWARE",
            "corrected_priority": None,
            "comments": None,
        },
        "HARDWARE",
        "LOW",
    )

    update_query, update_params = next(
        (query, params)
        for query, params in connection.test_cursor.queries
        if "UPDATE tickets" in query
    )
    assert "final_category" in connection.test_cursor.queries[1][0]
    assert update_params == ("HARDWARE", "LOW", 41)
