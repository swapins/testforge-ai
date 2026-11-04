"""FastAPI entry point for the TestForge AI draft-only API."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.generators import GenerationError, generate
from app.review_api import router as review_router
from app.schemas import (
    GenerationResult,
    Requirement,
    RequirementSubmission,
)

app = FastAPI(
    title="TestForge AI",
    description="Human-reviewed requirement-to-test draft generation.",
    version="0.2.0",
)


@app.exception_handler(GenerationError)
async def generation_error_handler(
    _request: Request, exc: GenerationError
) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "draft-only"}


@app.post("/requirements", response_model=RequirementSubmission, status_code=201)
def submit_requirement(requirement: Requirement) -> RequirementSubmission:
    """Validate a requirement for this request; submissions are not persisted."""
    return RequirementSubmission(
        requirement=requirement,
        message="Requirement received. Test cases must be reviewed by QA.",
    )


@app.post("/generate", response_model=GenerationResult)
def generate_test_cases(requirement: Requirement) -> GenerationResult:
    """Generate structured, non-executable test-case drafts."""
    return generate(requirement)


# Experimental, authenticated pilot endpoints for durable QA review.
app.include_router(review_router)
