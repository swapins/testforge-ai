"""Authenticated MVP persistence built on the existing SQLite review store."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import uuid
from datetime import UTC, datetime

from app.review_store import connect, get_case, initialize
from app.schemas import EditCaseRequest, ExecutionResult, Project, ProjectCreate, Requirement, TestCase


class StoreError(ValueError):
    pass


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2$240000${salt.hex()}${digest.hex()}"


def _check_password(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt_hex, digest_hex = encoded.split("$")
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)
        )
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def initialize_mvp() -> None:
    initialize()
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('developer','qa_reviewer')),
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL REFERENCES users(username),
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS requirement_revisions (
                project_id TEXT NOT NULL REFERENCES projects(id),
                requirement_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY(project_id, requirement_id, version)
            );
            CREATE TABLE IF NOT EXISTS executions (
                execution_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)


def bootstrap(developer_password: str, reviewer_password: str) -> None:
    initialize_mvp()
    with connect() as db:
        if db.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            raise StoreError("Accounts are already bootstrapped")
        db.executemany(
            "INSERT INTO users(username,display_name,role,password_hash) VALUES(?,?,?,?)",
            [
                ("saritha", "Saritha S", "developer", _hash_password(developer_password)),
                ("swapin", "Swapin Vidya", "qa_reviewer", _hash_password(reviewer_password)),
            ],
        )


def login(username: str, password: str) -> dict:
    initialize_mvp()
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if row is None or not _check_password(password, row["password_hash"]):
            raise StoreError("Invalid credentials")
        token = secrets.token_urlsafe(32)
        created = datetime.now(UTC)
        db.execute(
            "INSERT INTO sessions(token,username,created_at,expires_at) VALUES(?,?,?,?)",
            (token, username, created.isoformat(), (created.replace(year=created.year + 1)).isoformat()),
        )
        return {"access_token": token, "user": {"username": row["username"], "display_name": row["display_name"], "role": row["role"]}}


def user_for_token(token: str | None) -> dict:
    if not token:
        raise StoreError("Authentication required")
    initialize_mvp()
    with connect() as db:
        row = db.execute(
            "SELECT u.username,u.display_name,u.role,s.expires_at FROM sessions s JOIN users u ON u.username=s.username WHERE s.token=?",
            (token,),
        ).fetchone()
    if row is None or datetime.fromisoformat(row["expires_at"]) <= datetime.now(UTC):
        raise StoreError("Authentication required")
    return dict(row)


def create_project(data: ProjectCreate) -> Project:
    project_id = f"PRJ-{uuid.uuid4().hex[:10].upper()}"
    created = _now()
    with connect() as db:
        db.execute("INSERT INTO projects VALUES(?,?,?,?)", (project_id, data.name, data.description, created))
    return Project(id=project_id, name=data.name, description=data.description, created_at=created)


def list_projects() -> list[Project]:
    initialize_mvp()
    with connect() as db:
        rows = db.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    return [Project(id=r["id"], name=r["name"], description=r["description"], created_at=r["created_at"]) for r in rows]


def attach_requirement(project_id: str, requirement: Requirement) -> None:
    initialize_mvp()
    with connect() as db:
        if db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone() is None:
            raise StoreError("Project not found")
        db.execute(
            "INSERT INTO requirement_revisions VALUES(?,?,?,?,?)",
            (project_id, requirement.requirement_id, requirement.version, requirement.model_dump_json(), _now()),
        )


def submit_case(case_id: str, username: str) -> TestCase:
    initialize_mvp()
    with connect() as db:
        row = db.execute("SELECT payload,review_status,version FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            raise StoreError("Test case not found")
        if row["review_status"] not in {"draft", "rejected"}:
            raise StoreError("Only draft or rejected cases may be submitted")
        db.execute("UPDATE cases SET review_status=?,version=version+1 WHERE id=?", ("submitted", case_id))
        db.execute("INSERT INTO review_events(case_id,prior_status,new_status,reviewer,note) VALUES(?,?,?,?,?)", (case_id, row["review_status"], "submitted", username, "Submitted for QA review"))
        return TestCase.model_validate_json(row["payload"]).model_copy(update={"review_status": "submitted"})


def authenticated_decision(case_id: str, decision: str, reviewer: str, note: str) -> TestCase:
    if decision not in {"approved", "rejected"}:
        raise StoreError("QA decisions must be approved or rejected")
    initialize_mvp()
    with connect() as db:
        row = db.execute("SELECT payload,review_status FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            raise StoreError("Test case not found")
        if row["review_status"] != "submitted":
            raise StoreError("Only submitted cases may be decided")
        db.execute("UPDATE cases SET review_status=?,version=version+1 WHERE id=?", (decision, case_id))
        db.execute("INSERT INTO review_events(case_id,prior_status,new_status,reviewer,note) VALUES(?,?,?,?,?)", (case_id, "submitted", decision, reviewer, note))
        return TestCase.model_validate_json(row["payload"]).model_copy(update={"review_status": decision})


def edit_case(case_id: str, edit: EditCaseRequest) -> TestCase:
    initialize_mvp()
    with connect() as db:
        row = db.execute("SELECT payload,review_status FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            raise StoreError("Test case not found")
        if row["review_status"] == "approved":
            raise StoreError("Approved cases are immutable; create a new revision")
        original = TestCase.model_validate_json(row["payload"])
        new_id = f"{original.id}-R{secrets.randbelow(9999):04d}"
        updated = original.model_copy(update={**edit.model_dump(), "id": new_id, "review_status": "draft"})
        db.execute("INSERT INTO cases(id,requirement_id,payload,review_status,version) VALUES(?,?,?,?,0)", (new_id, updated.requirement_id, updated.model_dump_json(), "draft"))
        return updated


def save_execution(result: ExecutionResult) -> ExecutionResult:
    initialize_mvp()
    with connect() as db:
        db.execute("INSERT INTO executions VALUES(?,?,?,?)", (result.execution_id, result.test_case_id, result.model_dump_json(), _now()))
    return result


def regression_priorities() -> list[dict]:
    """Transparent score: requirement priority plus historical failure count."""
    initialize_mvp()
    with connect() as db:
        rows = db.execute("SELECT id,requirement_id,payload FROM cases WHERE review_status='approved'").fetchall()
        weights = {"critical": 45, "high": 35, "medium": 20, "low": 10}
        output = []
        for row in rows:
            case = TestCase.model_validate_json(row["payload"])
            req = db.execute("SELECT payload FROM requirements WHERE id=?", (row["requirement_id"],)).fetchone()
            priority = Requirement.model_validate_json(req["payload"]).priority if req else "medium"
            failures = db.execute(
                "SELECT COUNT(*) FROM executions WHERE case_id=? AND payload LIKE '%\\\"status\\\":\\\"failed\\\"%'",
                (row["id"],),
            ).fetchone()[0]
            output.append({"test_case_id": case.id, "score": min(100, weights[priority] + failures * 10), "reason": f"{priority} priority plus {failures} historical failure(s)"})
    return sorted(output, key=lambda item: item["score"], reverse=True)
