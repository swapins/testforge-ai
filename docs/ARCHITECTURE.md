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

## Not implemented

The project has no durable requirement database, login to external systems,
generated-code execution, sandbox, model fine-tuning, automated test oracle,
defect classifier, API system-under-test, JMeter integration, or production
telemetry. Those must be implemented and evaluated before being described as
capabilities.
