# MVP roadmap

## Phase 1 — Review-first foundations

- [x] FastAPI requirement submission and structured test-case draft endpoints
- [x] Deterministic baseline that works without a model or GPU
- [x] Optional configurable Hugging Face Inference API adapter
- [x] Selenium-Java/JUnit 5 Page Object Model demo against a local synthetic app
- [x] Python and Java CI checks
- [x] Requirement IDs and traceable structured draft metadata
- [x] Review-state schema with draft-first, non-executable output
- [x] Requirement persistence and durable human approval workflow
- [x] API test-case category generation for positive, negative, boundary, and business-rule cases

## Phase 2 — Evidence and execution

- [x] Export approved supported cases through a controlled template renderer
- [x] Add explicitly authorized local execution gate and run evidence
- [ ] Add a dedicated restricted execution container and screenshots
- [ ] Add JMeter/performance-test examples and define safe test-environment limits
- [ ] Track flaky runs and reproducibility without treating a pass as correctness

## Phase 3 — Measured evaluation

- [ ] Create a reviewed, privacy-safe requirements and known-defect benchmark
- [ ] Compare human-authored, deterministic, and model-assisted cases
- [ ] Publish results with baseline, sample size, model/version, and limitations

No phase is a claim of model training, automated test validation, defect
detection, or benchmark performance until implemented and evaluated.
