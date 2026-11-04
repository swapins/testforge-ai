# TestForge AI

TestForge AI is an open-source portfolio MVP for human-reviewed QA test
engineering. It combines a deterministic requirement-to-test API with a
separate Selenium-Java demonstration suite. Its design is aligned with
Selenium-Java, API testing, regression automation, and future performance-test
evaluation; no experience or benchmark claims are implied.

## Current status

**MVP v1.0: authenticated, traceable draft generation with controlled export and
an integrated dashboard.**

- The API validates submitted requirements and returns structured test-case
  drafts. Each case references its requirement ID, includes an objective,
  assumptions, acceptance criteria, scenario type, and starts in `draft` review
  status. The default generator is deterministic and requires no model or GPU.
- An optional Hugging Face Inference API adapter can be selected by
  configuration. Model output remains untrusted draft text and always requires
  QA approval.
- Selenium tests run separately against a local demonstration login page.
- An authenticated SQLite workflow supports developer and QA reviewer roles,
  projects, submission, approval/rejection, immutable approved cases, controlled
  export, and a disabled-by-default local execution pathway.
- A React/Vite dashboard provides sign-in, project creation, and visible review
  guardrails against the backend API.
- There is no test-code generation or execution, model fine-tuning, automated
  test validation, defect detection, persistent requirement store, or
  performance-testing integration.

## Quick start: API

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Submit a requirement:

```powershell
curl.exe -X POST http://127.0.0.1:8000/requirements `
  -H "Content-Type: application/json" `
  -d '{"requirement_id":"AUTH-001","description":"A registered user must be locked for 15 minutes after five consecutive failed login attempts."}'
```

Generate draft test cases with `POST /generate` using the same JSON body.
Submissions are validated but not persisted. Every generated case has
`review_required: true`, and every response has `executable: false`.

Run backend tests:

```powershell
python -m pytest -q
```

## Optional Hugging Face inference

Hugging Face support is disabled unless explicitly selected. It uses remote
inference; it does not download or fine-tune a model locally.

```powershell
python -m pip install -r requirements-ai.txt
$env:TESTFORGE_GENERATOR = "huggingface"
$env:TESTFORGE_MODEL_ID = "your-approved-model-id"
# Set HUGGINGFACEHUB_API_TOKEN if the chosen model requires authentication.
uvicorn app.main:app --reload
```

Choose a model whose availability, license, privacy properties, and inference
terms have been reviewed. Do not send confidential requirements, credentials,
customer data, or production logs to an external model. Malformed model output
is rejected; it is not silently replaced by deterministic output.

## Experimental persistent QA review (Phase 2)

This feature branch introduces pilot SQLite persistence with an append-only
review-event history. Configure `TESTFORGE_REVIEW_API_KEY` (required) and
optionally `TESTFORGE_DB_PATH` (default: `testforge.sqlite3`).
Send the API key using `X-Review-Key`. The protected endpoints are:

- `POST /v1/review/generations` — persist a requirement and its draft test cases.
- `GET /v1/review/cases/{case_id}` — retrieve a saved case and review status.
- `POST /v1/review/cases/{case_id}/decision` — record approved/rejected decision;
  also requires `X-Reviewer` identifying the reviewer.
- `GET /v1/review/cases/{case_id}/history` — retrieve audit events.

This is a **local pilot**, not production identity verification: the supplied
reviewer label is not independently authenticated. Do not expose this service
directly to untrusted users. Approval never authorises execution of generated
code, and duplicate requirements return HTTP 409 rather than overwrite data.
The original endpoints remain unchanged and non-persistent.

## Quick start: Selenium-Java demo

Requires Java 17+, Maven, and Google Chrome. Run independently from FastAPI:

```powershell
Set-Location examples\java
mvn test
```

Selenium Manager resolves a compatible ChromeDriver when needed. The test
opens `src/test/resources/demo/login.html`, a local synthetic application
with fake credentials and no network or private data. The Page Object Model is
under `src/test/java/ai/testforge/demo/pages`.

## Repository map

```text
app/                  FastAPI schemas, endpoints, and draft generators
tests/                Python API tests
examples/java/        Independent Maven/Selenium/JUnit demo and local app
docs/                 Architecture, evaluation methodology, and roadmap
.github/workflows/    Python and Java CI
```

## Safety and evaluation

Generated test cases are suggestions, not verified tests. A qualified human
must review requirements, assumptions, test data, selectors, and expected
results before use. Never execute untrusted generated code. Test only systems
you own or are authorized to assess.

See [Architecture](docs/ARCHITECTURE.md), [Evaluation methodology](docs/EVALUATION.md),
and [MVP roadmap](docs/ROADMAP.md). Current limitations and verification status
are recorded in [Project status](docs/PROJECT_STATUS.md).

## MVP authenticated workflow

The first-run operator bootstraps local accounts with passwords supplied at
runtime. `saritha` is the Developer account and `swapin` is the QA Reviewer
account. The backend enforces roles; the dashboard is not an authorization
boundary. See the [user guide](docs/USER_GUIDE.md) for the reproducible flow.

The review path is `draft → submitted → approved/rejected`. Only approved cases
can use the controlled exporter. Execution is restricted to the bundled
synthetic Maven demo and is disabled unless explicitly enabled by the operator.

## Docker Compose

```powershell
docker compose up --build
```

The API is available at `http://localhost:8000` and the Vite dashboard at
`http://localhost:5173`. See [deployment](docs/DEPLOYMENT.md).

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for project credits and attribution rules.

## Project credits

**Published by [TechSphere Consultancy Services Private Limited](https://techsphereconsultancy.com/)**

- **Developer:** Saritha S
- **Designated QA reviewer:** Swapin Vidya
- **Co-authors:** Swapin Vidya and [Rajah Shanmugasundaram](https://www.linkedin.com/in/rajahshan/)
- **Publishing company:** TechSphere Consultancy Services Private Limited
- **Corporate Identification Number (CIN):** U62020TN2025PTC177827
- **Company website:** https://techsphereconsultancy.com/

These are designated project credits; individual Git commit authorship remains
attributed to the people who made the commits.

## License and attribution

Licensed under Apache-2.0; see [LICENSE](LICENSE). Individual contributions must be credited accurately. No benchmark or
professional-experience claims are made by this repository.
