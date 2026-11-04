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
- Selenium execution requires Java 25, Maven, Chrome, and a compatible driver.

## Experimental or planned

- Model-assisted generation is experimental and has no benchmark claim.
- Review decisions are currently schema-level metadata; persistence and a durable
  approval workflow are planned.
- Selenium export, isolated execution evidence, and regression recommendations
  are planned.

## Known limitations

Generated cases are suggestions, not verified executable tests. The service does
not persist requirements or review decisions and never executes generated code.
