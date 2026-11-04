"""Pilot persistence and review state tests: no generated-code execution."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
headers = {"X-Review-Key": "unit-test-secret", "X-Reviewer": "qa-reviewer"}
requirement = {
    "requirement_id": "AUTH-900",
    "description": "A user account must be locked after five failed login attempts.",
    "acceptance_criteria": ["Fifth failed attempt locks the account"],
}


def test_review_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTFORGE_DB_PATH", str(tmp_path / "testforge.sqlite3"))
    monkeypatch.setenv("TESTFORGE_REVIEW_API_KEY", "unit-test-secret")
    created = client.post("/v1/review/generations", json=requirement, headers=headers)
    assert created.status_code == 201, created.text
    assert created.json()["executable"] is False
    case = created.json()["test_cases"][0]
    assert case["review_status"] == "draft"
    assert client.post("/v1/review/generations", json=requirement, headers=headers).status_code == 409
    decision = {"test_case_id": case["id"], "review_status": "approved",
                "reviewer_note": "Synthetic case reviewed"}
    saved = client.post(f'/v1/review/cases/{case["id"]}/decision', json=decision, headers=headers)
    assert saved.status_code == 200, saved.text
    assert saved.json()["review_status"] == "approved"
    assert saved.json()["review_required"] is True
    assert client.post(f'/v1/review/cases/{case["id"]}/decision',
                       json=decision, headers=headers).status_code == 409
    history = client.get(f'/v1/review/cases/{case["id"]}/history', headers=headers)
    assert history.status_code == 200
    assert history.json()["events"][0]["new_status"] == "approved"
    assert history.json()["events"][0]["reviewer"] == "qa-reviewer"


def test_review_requires_configured_access(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTFORGE_DB_PATH", str(tmp_path / "testforge.sqlite3"))
    monkeypatch.delenv("TESTFORGE_REVIEW_API_KEY", raising=False)
    assert client.post("/v1/review/generations", json=requirement).status_code == 403
