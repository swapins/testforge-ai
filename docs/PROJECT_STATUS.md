# Project status

## Working and verified

- FastAPI validates requirements and generates deterministic, structured draft cases.
- Requirement IDs are copied into every generated case for traceability.
- Cases include scenario type, objective, acceptance criteria, assumptions, and
  a `draft` review status.
- Optional Hugging Face output is schema-validated and remains non-executable.
- The local Selenium-Java demo and Python/Java CI definitions are present.

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

The current pilot accepts a self-declared reviewer label. Assigning Swapin Vidya
as the designated reviewer in documentation does not authenticate the caller;
reviewer identity enforcement is required before external or production use.

## Experimental or planned

- Model-assisted generation is experimental and has no benchmark claim.
- Pilot SQLite persistence and append-only review events are implemented on the
  Phase 2 feature branch; GitHub CI verification is pending. A single shared
  API key gates write/read access, but the supplied reviewer identifier is not
  independently authenticated. This is not production-grade identity assurance.
- Selenium export, isolated execution evidence, and regression recommendations
  are planned.

## Known limitations

Generated cases are suggestions, not verified executable tests. The baseline
endpoints do not persist data. The experimental review API stores requirements,
cases and decision history in SQLite; it does not authenticate reviewer identities
beyond a shared API key and a self-declared reviewer label. The service never
executes generated code.
