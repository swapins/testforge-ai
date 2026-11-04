"""API schemas for traceable, review-first draft test-case generation."""

from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement_id: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=10, max_length=10_000)
    acceptance_criteria: list[str] = Field(default_factory=list, max_length=20)


ScenarioType = Literal["positive", "negative", "boundary", "business-rule"]
ReviewStatus = Literal["draft", "approved", "rejected"]


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


class ModelGeneration(BaseModel):
    test_cases: list[ModelTestCase] = Field(min_length=1, max_length=10)
