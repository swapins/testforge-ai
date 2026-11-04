# Project status

## Working and verified

- FastAPI validates requirements and generates deterministic, structured draft cases.
- Requirement IDs are copied into every generated case for traceability.
- Cases include scenario type, objective, acceptance criteria, assumptions, and
  a `draft` review status.
- Optional Hugging Face output is schema-validated and remains non-executable.
- The local Selenium-Java demo and Python/Java CI definitions are present.
- Authenticated MVP accounts, project creation, review transitions, controlled
  export, execution records, Docker Compose, and a React/Vite dashboard are present.

## Implemented but environment-dependent

- The Hugging Face adapter requires the optional dependency, a configured model,
  network access, and any required token.
- Selenium execution requires Java 17, Maven, Chrome, and a compatible driver.

Java 17 is the CI/build baseline: the demo uses no Java 25-specific APIs or
language features, so Java 25 is not required. The workflow supplies the exact
browser binary installed by `browser-actions/setup-chrome` to Selenium.

## Designated project responsibilities

- **Developer:** Saritha S — implementation and development role.
- **QA reviewer:** Swapin Vidya — designated reviewer for QA test-case decisions.
- **Co-authors:** Swapin Vidya and Rajah Shanmugasundaram (project credits).

The MVP uses locally bootstrapped authenticated accounts. This is suitable for
the local demonstration, not a production identity provider.

## Experimental or planned

- Model-assisted generation is experimental and has no benchmark claim.
- Regression scoring and AI-assisted defect summaries remain planned.

## Known limitations

Generated cases are suggestions, not verified executable tests. There is no
production identity provider, multi-tenant isolation, dedicated execution
container, screenshot capture, or full regression-intelligence implementation.
