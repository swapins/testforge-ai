"""FastAPI entry point for the TestForge AI draft-only API."""

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from app.generators import GenerationError, generate
from app.review_api import router as review_router
from app.mvp_api import router as mvp_router
from app.schemas import (
    GenerationResult,
    Requirement,
    RequirementSubmission,
)

app = FastAPI(
    title="TestForge AI",
    description="Human-reviewed requirement-to-test draft generation.",
    version="1.0.0-mvp",
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
app.include_router(mvp_router)


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    """Serve the built dashboard when frontend assets are present locally."""
    entry = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "index.html"
    if not entry.exists():
        return JSONResponse(status_code=404, content={"detail": "Build frontend with npm run build"})
    return FileResponse(entry)
