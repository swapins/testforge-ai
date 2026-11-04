# Repository audit

Audit date: 2026-11-04 (Asia/Singapore)

## Git and workspace findings

- The checkout originally pointed at the initial MVP commit `2fc6105` on `main`.
- `origin/main` contained attribution commits `33f641d` and `3781af0`; both were
  incorporated into the feature branch without rewriting history.
- Three local, uncommitted edits were found before this work: Java/CI compiler
  settings and the matching README requirement. They were preserved.
- The feature branch is `codex/audit-and-requirement-traceability`.

## Findings and severity

- **High (fixed):** Java CI, Maven compiler release, and README now agree on
  Java 17, which is sufficient for the demo and preserves the project’s
  original compatibility baseline.
- **High (fixed):** CI now passes the browser binary installed by
  `browser-actions/setup-chrome` to Selenium, preventing the runner’s separate
  system Chrome from being paired with the installed ChromeDriver.
- **Medium (fixed):** The project had no standalone contributor document and
  attribution was only in README; `CONTRIBUTORS.md` now records the supplied
  credits without addresses.
- **Medium (fixed):** Generated cases lacked explicit traceability metadata and
  review state; the schema now carries requirement ID, criteria, objective,
  assumptions, scenario type, and review status.
- **Low (remaining):** Requirements and review decisions are not persisted.
- **Low (remaining):** The Hugging Face adapter does not yet expose configurable
  timeout/retry controls; remote output is still bounded and schema-validated.

## Security and honesty checks

No credentials or API tokens are committed. The application does not execute
generated code or test uncontrolled external websites. No model training,
fine-tuning, benchmark, autonomous testing, or defect-detection claim is made.
