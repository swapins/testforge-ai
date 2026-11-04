# Architecture

## Implemented request flow

1. `POST /requirements` validates the requirement schema and returns a receipt.
   The MVP does not persist the submission.
2. `POST /generate` validates the same requirement shape and selects the
   configured generator.
3. The default deterministic generator emits a conservative, structured draft
   without inferring application-specific selectors or behavior.
4. The optional Hugging Face adapter requests JSON-shaped suggestions and
   validates the response against a bounded Pydantic schema.
5. All results are explicitly marked as requiring QA review and
   non-executable. No generated code is run.

## Traceability and review state

`Requirement.requirement_id` is the stable trace key. Generated `TestCase`
objects copy that ID and include a scenario type, objective, acceptance
criteria, assumptions, explicit expected result, and `review_status`. Every
generated case starts as `draft`; `approved` and `rejected` are reserved review
states. This metadata does not authorize execution, and `GenerationResult`
always remains `executable: false`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `TESTFORGE_GENERATOR` | `deterministic` | `deterministic` or `huggingface` |
| `TESTFORGE_MODEL_ID` | unset | Required model identifier for Hugging Face |
| `HUGGINGFACEHUB_API_TOKEN` | unset | Optional inference authentication token |

Model inference requires installing `requirements-ai.txt`, network access, and
any model-specific access approval. A malformed response produces an explicit
gateway error rather than a successful deterministic fallback.

## Independent browser demo

`examples/java` is a standalone Maven project. JUnit 5 launches Selenium
ChromeDriver and interacts with the bundled static login demonstration through
the `LoginPage` Page Object. It has no dependency on or network connection to
the FastAPI service. Credentials and behavior in the demo are synthetic.

## Authenticated MVP boundary

The SQLite store is extended with users, bearer sessions, projects, requirement
revisions, and execution records. Passwords use PBKDF2-SHA256. Backend role
checks distinguish the Developer (`saritha`) from the QA Reviewer (`swapin`);
the developer cannot approve a case. Cases move through
`draft → submitted → approved/rejected`, and review events are append-only.

The exporter emits only a fixed login/lockout template. It does not accept
source code, imports, shell commands, URLs, or arbitrary paths from users or
models. The executor accepts only approved supported cases and invokes the
bundled synthetic Maven test with a fixed command. It is disabled by default.

The `frontend` directory contains the React/Vite dashboard. It is a thin client
for the authenticated API, while authorization remains entirely server-side.

## Not implemented

The project has no production identity provider, dedicated restricted execution
container, screenshot capture, model fine-tuning, automated test oracle, defect
classifier, API system-under-test, JMeter integration, or production telemetry.
Those must be implemented and evaluated before being described as capabilities.
