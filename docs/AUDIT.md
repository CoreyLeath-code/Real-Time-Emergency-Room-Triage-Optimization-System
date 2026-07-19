# Production Readiness Audit

## Executive assessment

MediTriage is a useful synthetic-data research demonstrator, not a production clinical system. This change raises software-engineering maturity through a shared validated pipeline, deterministic evidence, stronger tests, CI coverage, a hardened container, and explicit safety boundaries. Clinical deployment remains out of scope.

## Strengths

- Small, understandable tabular pipeline with pinned dependencies.
- Synthetic dataset avoids PHI exposure in the repository.
- Deterministic stratified evaluation and class-specific recall.
- Versioned benchmark protocol and raw evidence.
- Container, Kubernetes, Ansible, and Terraform examples.
- Model card and reproducible CI artifacts.

## Material risks

| Priority | Risk | Impact | Current control |
|---|---|---|---|
| P0 | No clinical validation or regulatory review | Unsafe triage decisions | Explicit research-only boundary |
| P0 | Synthetic data only | Unknown generalization and bias | Claims limited to synthetic holdout |
| P1 | No probability calibration/abstention | Overconfident predictions | Documented as required future work |
| P1 | No authentication/audit trail/EHR contract | Privacy and accountability gaps | No production deployment claim |
| P1 | Limited feature set | Missing clinically relevant context | Model-card limitation |
| P2 | UI loads a local pickle directly | Artifact integrity/versioning risk | Deterministic artifact; signing pending |
| P2 | No concurrent end-to-end load test | Unknown service SLOs | In-process benchmark clearly scoped |

## Implemented improvements

- Centralized data validation, stratified splitting, model construction, and evaluation.
- Added class-balanced training and safety-relevant macro/per-class metrics.
- Added negative, deterministic, probability, and training regression tests.
- Enforced 85% coverage; current measured coverage is 92.16%.
- Added benchmark CI with raw JSON artifacts and scaling evidence.
- Removed an unused JDK from the runtime image; added non-root execution and health checking.
- Replaced unsupported README estimates with measured, qualified evidence.

## Prioritized roadmap

1. Define a clinician-owned intended-use statement and hazard analysis.
2. Obtain governed, representative data with consent, lineage, and subgroup labels.
3. Run external validation, calibration, fairness, and uncertainty/abstention studies.
4. Add immutable signed model artifacts, provenance, rollback, and audit logging.
5. Build authenticated APIs with strict schemas, rate limits, PHI controls, and EHR integration tests.
6. Add end-to-end concurrency, failure injection, container startup, and recovery benchmarks.
7. Establish monitoring for drift, calibration, class recall, latency, and alert fatigue.
8. Complete privacy, security, regulatory, and human-factors review before any clinical pilot.

## Decision

Suitable for recruiter review and synthetic research demonstrations after this PR. **Not approved for clinical deployment or patient-care decisions.**
