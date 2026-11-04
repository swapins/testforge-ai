"""API schemas for traceable, review-first draft test-case generation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement_id: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=10, max_length=10_000)
    acceptance_criteria: list[str] = Field(default_factory=list, max_length=20)
    title: str = Field(default="Untitled requirement", min_length=1, max_length=200)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    version: int = Field(default=1, ge=1, le=10_000)


ScenarioType = Literal["positive", "negative", "boundary", "business-rule"]
ReviewStatus = Literal["draft", "submitted", "approved", "rejected"]


class TestCase(BaseModel):
    id: str
    requirement_id: str
    title: str
    scenario_type: ScenarioType
    objective: str = Field(min_length=1, max_length=2_000)
    steps: list[str]
    expected_result: str
    acceptance_criteria: list[str] = Field(default_factory=list, max_length=20)
    assumptions: list[str] = Field(default_factory=list, max_length=20)
    origin: Literal["deterministic-baseline", "huggingface-inference"]
    review_status: ReviewStatus = "draft"
    review_required: Literal[True] = True


class GenerationResult(BaseModel):
    test_cases: list[TestCase]
    assumptions: list[str]
    generation_mode: Literal["deterministic-baseline", "huggingface-inference"]
    executable: Literal[False] = False


class RequirementSubmission(BaseModel):
    requirement: Requirement
    status: Literal["received"] = "received"
    message: str


class ModelTestCase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    steps: list[str] = Field(min_length=1, max_length=20)
    expected_result: str = Field(min_length=1, max_length=2_000)


class ReviewDecision(BaseModel):
    """A review state is metadata only; approval never makes a case executable."""

    test_case_id: str = Field(min_length=1, max_length=120)
    review_status: ReviewStatus
    reviewer_note: str = Field(default="", max_length=2_000)


class AuthenticatedDecision(BaseModel):
    review_status: Literal["approved", "rejected"]
    reviewer_note: str = Field(default="", max_length=2_000)


class BootstrapRequest(BaseModel):
    developer_password: str = Field(min_length=12, max_length=256)
    reviewer_password: str = Field(min_length=12, max_length=256)


class LoginRequest(BaseModel):
    username: Literal["saritha", "swapin"]
    password: str = Field(min_length=1, max_length=256)


class UserSummary(BaseModel):
    username: str
    display_name: str
    role: Literal["developer", "qa_reviewer"]


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserSummary


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2_000)


class Project(ProjectCreate):
    id: str
    created_at: datetime


class RequirementRevision(BaseModel):
    project_id: str
    requirement: Requirement
    created_at: datetime


class EditCaseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    steps: list[str] = Field(min_length=1, max_length=20)
    expected_result: str = Field(min_length=1, max_length=2_000)
    objective: str = Field(min_length=1, max_length=2_000)


class ExecutionResult(BaseModel):
    execution_id: str
    test_case_id: str
    status: Literal["passed", "failed", "blocked", "error"]
    duration_ms: int = Field(ge=0)
    failure_category: Literal[
        "assertion-failure", "browser-infrastructure", "timeout",
        "test-data", "unknown", "none"
    ]
    log: str = Field(default="", max_length=20_000)
    screenshot_path: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)


class ModelGeneration(BaseModel):
    test_cases: list[ModelTestCase] = Field(min_length=1, max_length=10)
