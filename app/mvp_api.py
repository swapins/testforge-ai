"""Authenticated MVP API: accounts, projects, review, safe export and execution."""

from __future__ import annotations

import os
import re
import subprocess
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

from app.generators import generate
from app.mvp_store import (
    StoreError, attach_requirement, authenticated_decision, bootstrap, create_project,
    edit_case, initialize_mvp, list_projects, login, save_execution, submit_case,
    user_for_token, regression_priorities,
)
from app.review_store import DuplicateRequirement, get_case, review_history, save_generation
from app.schemas import (
    BootstrapRequest, EditCaseRequest, ExecutionResult, LoginRequest, LoginResponse,
    AuthenticatedDecision, Project, ProjectCreate, Requirement, TestCase,
)

router = APIRouter(prefix="/v1", tags=["mvp"])
_DEMO_ROOT = Path(__file__).resolve().parent.parent / "examples" / "java"


def _token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def current_user(authorization: str | None) -> dict:
    try:
        return user_for_token(_token(authorization))
    except StoreError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_role(authorization: str | None, role: str) -> dict:
    user = current_user(authorization)
    if user["role"] != role:
        raise HTTPException(status_code=403, detail="This role is not authorized for the operation")
    return user


@router.on_event("startup")
def startup() -> None:
    initialize_mvp()


@router.post("/auth/bootstrap", status_code=201)
def bootstrap_accounts(request: BootstrapRequest):
    try:
        bootstrap(request.developer_password, request.reviewer_password)
    except StoreError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "bootstrapped", "accounts": ["saritha", "swapin"]}


@router.post("/auth/login", response_model=LoginResponse)
def auth_login(request: LoginRequest):
    try:
        return login(request.username, request.password)
    except StoreError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/auth/me")
def auth_me(authorization: str | None = Header(None)):
    return current_user(authorization)


@router.post("/projects", response_model=Project, status_code=201)
def projects_create(project: ProjectCreate, authorization: str | None = Header(None)):
    require_role(authorization, "developer")
    return create_project(project)


@router.get("/projects", response_model=list[Project])
def projects_list(authorization: str | None = Header(None)):
    current_user(authorization)
    return list_projects()


@router.post("/projects/{project_id}/generations", response_model=dict, status_code=201)
def project_generation(project_id: str, requirement: Requirement, authorization: str | None = Header(None)):
    require_role(authorization, "developer")
    result = generate(requirement)
    try:
        attach_requirement(project_id, requirement)
        save_generation(requirement, result)
    except (StoreError, DuplicateRequirement) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"project_id": project_id, **result.model_dump()}


@router.post("/cases/{case_id}/submit", response_model=TestCase)
def case_submit(case_id: str, authorization: str | None = Header(None)):
    user = require_role(authorization, "developer")
    try:
        return submit_case(case_id, user["username"])
    except StoreError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/cases/{case_id}", response_model=TestCase)
def case_edit(case_id: str, edit: EditCaseRequest, authorization: str | None = Header(None)):
    require_role(authorization, "developer")
    try:
        return edit_case(case_id, edit)
    except StoreError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/cases/{case_id}/decision", response_model=TestCase)
def case_decision(case_id: str, body: AuthenticatedDecision, authorization: str | None = Header(None)):
    user = require_role(authorization, "qa_reviewer")
    try:
        return authenticated_decision(case_id, body.review_status, user["username"], body.reviewer_note)
    except StoreError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/cases/{case_id}/history")
def case_history(case_id: str, authorization: str | None = Header(None)):
    current_user(authorization)
    try:
        get_case(case_id)
        return {"test_case_id": case_id, "events": review_history(case_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc


def _supported_template(case: TestCase) -> bool:
    text = f"{case.title} {case.objective}".lower()
    return "lockout" in text or "login" in text


def _java_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\r", " ").replace("\n", " ")


@router.get("/cases/{case_id}/export")
def export_case(case_id: str, authorization: str | None = Header(None)):
    require_role(authorization, "developer")
    try:
        case = get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc
    if case.review_status != "approved":
        raise HTTPException(status_code=403, detail="Only approved cases can be exported")
    if not _supported_template(case):
        return {"status": "unsupported", "reason": "No safe template matches this scenario"}
    safe_id = re.sub(r"[^A-Za-z0-9_ -]", "", case.id)
    class_name = f"{re.sub(r'[^A-Za-z0-9]', '', case.id)}Export"
    source = f'''package ai.testforge.generated;

import static org.junit.jupiter.api.Assertions.assertEquals;
import ai.testforge.demo.pages.LoginPage;
import java.nio.file.Paths;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

// Controlled TestForge template. The renderer owns imports, selectors and target paths.
public final class {class_name} {{
    private WebDriver driver;

    @BeforeEach
    void setUp() {{
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new", "--no-sandbox", "--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
    }}

    @AfterEach
    void tearDown() {{ if (driver != null) driver.quit(); }}

    @Test
    void generatedLoginLockoutScenario() {{
        LoginPage page = new LoginPage(driver).openDemo();
        for (int attempt = 0; attempt < 5; attempt++) page.login("demo", "incorrect-password");
        assertEquals("Account locked for 15 minutes.", page.statusMessage());
    }}
}}
'''
    return {"status": "exported", "template": "login-lockout", "files": {f"{safe_id}Export.java": source}}


@router.post("/cases/{case_id}/execute", response_model=ExecutionResult)
def execute_case(case_id: str, authorization: str | None = Header(None)):
    require_role(authorization, "developer")
    try:
        case = get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Test case not found") from exc
    if case.review_status != "approved":
        raise HTTPException(status_code=403, detail="Only approved cases can execute")
    if not _supported_template(case):
        raise HTTPException(status_code=422, detail="Scenario is unsupported by the controlled executor")
    if os.getenv("TESTFORGE_ENABLE_EXECUTION") != "1":
        result = ExecutionResult(execution_id=str(uuid.uuid4()), test_case_id=case_id, status="blocked", duration_ms=0, failure_category="none", log="Execution disabled; set TESTFORGE_ENABLE_EXECUTION=1 for the local synthetic demo.", environment={"target": "bundled synthetic demo"})
        return save_execution(result)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            ["mvn", "--batch-mode", "-Dtest=LoginLockoutTest", "test"],
            cwd=_DEMO_ROOT, capture_output=True, text=True, timeout=90,
            env={"PATH": os.environ.get("PATH", ""), "JAVA_HOME": os.environ.get("JAVA_HOME", "")},
            check=False,
        )
        status = "passed" if completed.returncode == 0 else "failed"
        category = "none" if status == "passed" else "assertion-failure"
        log = (completed.stdout + "\n" + completed.stderr)[-20_000:]
    except subprocess.TimeoutExpired as exc:
        status, category, log = "error", "timeout", str(exc)
    duration = int((time.monotonic() - started) * 1000)
    return save_execution(ExecutionResult(execution_id=str(uuid.uuid4()), test_case_id=case_id, status=status, duration_ms=duration, failure_category=category, log=log, environment={"target": "bundled synthetic demo", "runner": "Maven"}))


@router.get("/reports/regression")
def regression_report(authorization: str | None = Header(None)):
    current_user(authorization)
    return {"method": "priority weight + historical failure frequency", "items": regression_priorities()}
