# TestForge AI

TestForge AI is an open-source portfolio MVP for human-reviewed QA test
engineering. It combines a deterministic requirement-to-test API with a
separate Selenium-Java demonstration suite. Its design is aligned with
Selenium-Java, API testing, regression automation, and future performance-test
evaluation; no experience or benchmark claims are implied.

## Current status

**MVP: draft-only test generation and a runnable local browser demo.**

- The API validates submitted requirements and returns structured test-case
  drafts. The default generator is deterministic and requires no model or GPU.
- An optional Hugging Face Inference API adapter can be selected by
  configuration. Model output remains untrusted draft text and always requires
  QA approval.
- Selenium tests run separately against a local demonstration login page.
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
and [MVP roadmap](docs/ROADMAP.md).

## License and attribution

Licensed under Apache-2.0; see [LICENSE](LICENSE). Project ownership and
contributor attribution should reflect actual contributions. No benchmark or
professional-experience claims are made by this repository.
