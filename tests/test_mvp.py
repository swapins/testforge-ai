from fastapi.testclient import TestClient

from app.main import app


def test_authenticated_mvp_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTFORGE_DB_PATH", str(tmp_path / "mvp.sqlite3"))
    monkeypatch.delenv("TESTFORGE_ENABLE_EXECUTION", raising=False)
    with TestClient(app) as client:
        boot = client.post("/v1/auth/bootstrap", json={
            "developer_password": "developer-password-123",
            "reviewer_password": "reviewer-password-123",
        })
        assert boot.status_code == 201
        developer = client.post("/v1/auth/login", json={
            "username": "saritha", "password": "developer-password-123"
        }).json()["access_token"]
        reviewer = client.post("/v1/auth/login", json={
            "username": "swapin", "password": "reviewer-password-123"
        }).json()["access_token"]
        dev_headers = {"Authorization": f"Bearer {developer}"}
        qa_headers = {"Authorization": f"Bearer {reviewer}"}

        project = client.post("/v1/projects", json={"name": "Synthetic login"}, headers=dev_headers)
        assert project.status_code == 201
        project_id = project.json()["id"]
        requirement = {
            "requirement_id": "AUTH-MVP-001",
            "title": "Login account lockout",
            "description": "A user account must be locked after five failed login attempts.",
            "acceptance_criteria": ["The fifth failure locks the account."],
            "priority": "high",
        }
        generated = client.post(f"/v1/projects/{project_id}/generations", json=requirement, headers=dev_headers)
        assert generated.status_code == 201
        case = generated.json()["test_cases"][0]
        case_id = case["id"]
        assert case["review_status"] == "draft"

        assert client.post(f"/v1/cases/{case_id}/submit", headers=dev_headers).json()["review_status"] == "submitted"
        assert client.post(f"/v1/cases/{case_id}/decision", json={"review_status": "approved"}, headers=dev_headers).status_code == 403
        approved = client.post(f"/v1/cases/{case_id}/decision", json={"review_status": "approved", "reviewer_note": "Reviewed"}, headers=qa_headers)
        assert approved.status_code == 200
        assert approved.json()["review_status"] == "approved"
        assert client.patch(f"/v1/cases/{case_id}", json={"title": "changed", "steps": ["x"], "expected_result": "y", "objective": "z"}, headers=dev_headers).status_code == 409
        exported = client.get(f"/v1/cases/{case_id}/export", headers=dev_headers)
        assert exported.status_code == 200
        assert exported.json()["status"] == "exported"
        execution = client.post(f"/v1/cases/{case_id}/execute", headers=dev_headers)
        assert execution.status_code == 200
        assert execution.json()["status"] == "blocked"


def test_mvp_rejects_weak_bootstrap_and_unauthenticated_project_access(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTFORGE_DB_PATH", str(tmp_path / "mvp.sqlite3"))
    with TestClient(app) as client:
        assert client.post("/v1/auth/bootstrap", json={"developer_password": "short", "reviewer_password": "short"}).status_code == 422
        assert client.get("/v1/projects").status_code == 401
