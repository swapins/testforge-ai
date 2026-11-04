"""Opt-in persistent review API; existing draft endpoints remain unchanged."""
import os
import secrets

from fastapi import APIRouter, Header, HTTPException

from app.generators import generate
from app.schemas import GenerationResult, Requirement, ReviewDecision, TestCase
from app.review_store import (
    DuplicateRequirement, MissingCase, ReviewConflict,
    get_case, review_case, review_history, save_generation,
)

router = APIRouter(prefix="/v1/review", tags=["experimental-review"])


def _authorize(key: str | None) -> None:
    expected = os.getenv("TESTFORGE_REVIEW_API_KEY")
    if not expected or not key or not secrets.compare_digest(key, expected):
        raise HTTPException(status_code=403, detail="Review API access denied")


@router.post("/generations", response_model=GenerationResult, status_code=201)
def create_generation(requirement: Requirement, x_review_key: str | None = Header(None)):
    _authorize(x_review_key)
    result = generate(requirement)
    try:
        save_generation(requirement, result)
    except DuplicateRequirement as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return result


@router.get("/cases/{case_id}", response_model=TestCase)
def read_case(case_id: str, x_review_key: str | None = Header(None)):
    _authorize(x_review_key)
    try:
        return get_case(case_id)
    except MissingCase as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc


@router.post("/cases/{case_id}/decision", response_model=TestCase)
def decide(
    case_id: str, decision: ReviewDecision, x_reviewer: str = Header(...),
    x_review_key: str | None = Header(None),
):
    _authorize(x_review_key)
    try:
        return review_case(case_id, decision, x_reviewer)
    except MissingCase as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc
    except ReviewConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/cases/{case_id}/history")
def history(case_id: str, x_review_key: str | None = Header(None)):
    _authorize(x_review_key)
    try:
        return {"test_case_id": case_id, "events": review_history(case_id)}
    except MissingCase as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc
