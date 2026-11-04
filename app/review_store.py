"""SQLite-backed draft test cases and append-only review decisions.

Pilot storage only: deploy behind trusted authentication and protect the DB file.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.schemas import GenerationResult, Requirement, ReviewDecision, TestCase


def _db_path() -> str:
    return os.environ.get("TESTFORGE_DB_PATH", "testforge.sqlite3")


@contextmanager
def connect():
    path = _db_path()
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize() -> None:
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                requirement_id TEXT NOT NULL REFERENCES requirements(id),
                payload TEXT NOT NULL,
                review_status TEXT NOT NULL DEFAULT 'draft'
                    CHECK(review_status IN ('draft','submitted','approved','rejected')),
                version INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS review_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL REFERENCES cases(id),
                prior_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)


class DuplicateRequirement(ValueError):
    pass


class MissingCase(KeyError):
    pass


class ReviewConflict(ValueError):
    pass


def save_generation(requirement: Requirement, result: GenerationResult) -> None:
    """Atomically save a new requirement and its generated drafts; never overwrite."""
    initialize()
    with connect() as db:
        try:
            db.execute("INSERT INTO requirements(id,payload) VALUES(?,?)",
                       (requirement.requirement_id, requirement.model_dump_json()))
            for case in result.test_cases:
                if case.requirement_id != requirement.requirement_id or case.review_status != "draft":
                    raise ValueError("Only draft cases linked to the requirement may be saved")
                db.execute(
                    "INSERT INTO cases(id,requirement_id,payload) VALUES(?,?,?)",
                    (case.id, case.requirement_id, case.model_dump_json()),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateRequirement("Requirement or test case already exists") from exc


def get_case(case_id: str) -> TestCase:
    initialize()
    with connect() as db:
        row = db.execute("SELECT payload,review_status FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            raise MissingCase(case_id)
        case = TestCase.model_validate_json(row["payload"])
        return case.model_copy(update={"review_status": row["review_status"]})


def review_case(case_id: str, decision: ReviewDecision, reviewer: str) -> TestCase:
    """Persist decision with audit history; approvals never authorize execution."""
    if decision.test_case_id != case_id:
        raise ReviewConflict("Test case ID does not match request path")
    if decision.review_status == "draft":
        raise ReviewConflict("A completed decision cannot return a case to draft")
    if not reviewer.strip():
        raise ReviewConflict("Reviewer identifier required")
    initialize()
    with connect() as db:
        row = db.execute(
            "SELECT payload,review_status,version FROM cases WHERE id=?", (case_id,)
        ).fetchone()
        if row is None:
            raise MissingCase(case_id)
        if row["review_status"] != "draft":
            raise ReviewConflict("This case already has a final decision")
        db.execute(
            "UPDATE cases SET review_status=?,version=version+1 WHERE id=? AND version=?",
            (decision.review_status, case_id, row["version"]),
        )
        if db.execute("SELECT changes()").fetchone()[0] != 1:
            raise ReviewConflict("Concurrent review update detected")
        db.execute(
            "INSERT INTO review_events(case_id,prior_status,new_status,reviewer,note) VALUES(?,?,?,?,?)",
            (case_id, "draft", decision.review_status, reviewer.strip(), decision.reviewer_note),
        )
        case = TestCase.model_validate_json(row["payload"])
        return case.model_copy(update={"review_status": decision.review_status})


def review_history(case_id: str) -> list[dict]:
    get_case(case_id)
    with connect() as db:
        rows = db.execute(
            "SELECT id,prior_status,new_status,reviewer,note,created_at "
            "FROM review_events WHERE case_id=? ORDER BY id", (case_id,)
        ).fetchall()
    return [dict(row) for row in rows]
