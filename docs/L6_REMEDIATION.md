# L6 remediation plan: safety boundary and verification

Tracks #12.

## Non-clinical boundary

This repository is an engineering/optimization project. It is not a clinical decision-support system and must not be used to prioritize, diagnose, delay, or determine patient care without formal clinical validation, governance, and deployment authorization.

## Required verification

- [ ] Add automated tests for the implemented triage logic and API behavior.
- [ ] Record data provenance, intended-use constraints, and known failure modes.
- [ ] Use only de-identified or synthetic non-production data for any environment validation.
- [ ] Define a rollback/disable mechanism before any hosted demonstration.
- [ ] Keep release notes and the README aligned with observed evidence, not aspirational clinical claims.
