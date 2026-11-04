# Evaluation methodology

TestForge AI does not currently publish benchmark results. This document
defines a method to evaluate future generators without claiming that the work
has already been performed.

## Evaluation set

- Use synthetic or explicitly licensed requirements and test applications.
- Exclude private requirements, credentials, customer information, and
  production logs.
- Have QA reviewers approve acceptance criteria and an expected coverage
  matrix before generating candidates.
- Include positive, negative, boundary, and regression scenarios where the
  requirement supports them.
- Maintain a documented set of seeded, known defects and a separate control
  set. Keep the answer key unavailable to the generator.

## Comparisons and measures

Compare human-authored cases, the deterministic baseline, and each
model-assisted candidate set on the same held-out requirements. Record the
model identifier/version, prompt, parameters, date, and any exclusions.

Report, at minimum:

- Requirement coverage: approved criteria covered / total approved criteria.
- Reviewer-rated correctness, relevance, and unsupported-assumption rate,
  with the rubric and number of independent reviewers.
- Seeded-defect detection: distinct known defects detected / total seeded
  defects, plus false positives on the control set.
- Executability and flakiness only after cases have been implemented and
  repeatedly run in a controlled environment.
- Inference latency and cost, where applicable, separately from test runtime.

Include sample sizes, confidence intervals where meaningful, disagreements,
failures, and limitations. A passing generated test is not evidence that the
application is defect-free. Do not claim “AI validation” or defect detection
until those measures have been implemented and independently reviewed.
