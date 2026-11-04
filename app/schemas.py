"""API schemas for requirement submission and draft test-case generation."""

from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement_id: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=10, max_length=10_000)


class TestCase(BaseModel):
    id: str
    requirement_id: str
    title: str
    steps: list[str]
    expected_result: str
    origin: Literal["deterministic-baseline", "huggingface-inference"]
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


class ModelGeneration(BaseModel):
    test_cases: list[ModelTestCase] = Field(min_length=1, max_length=10)
