# Development plan

## Completed milestone: traceable draft generation

- Keep `requirement_id` as the stable trace key.
- Carry acceptance criteria from a requirement into generated cases.
- Label positive, negative, boundary, and business-rule scenario types in the
  schema without inventing unprovided application behavior.
- Require objectives, explicit expected results, assumptions, and initial
  `draft` review status.
- Keep all generated output non-executable.

## Next milestone: controlled Selenium export

1. Define an explicit export contract for approved scenarios only.
2. Render controlled Page Object Model and JUnit templates.
3. Compile generated output before any execution is considered.
4. Run only against synthetic or explicitly authorized applications in isolation.
5. Capture screenshots, logs, and failure evidence.
6. Add reviewer-facing failure analysis and regression recommendations.

No generated code should be executed directly, and no planned feature should be
described as complete before tests and evidence exist.
