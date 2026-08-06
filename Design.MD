# Design

## Purpose and safety boundary

MediTriage AI is an educational and research demonstration for reproducible tabular triage-classification workflows using only the repository's synthetic records. It predicts low, urgent, or immediate categories from structured example inputs, but it is not clinically validated, is not a medical device, and must not direct patient care or replace clinician judgment.

## Training and evaluation path

`train_model.py` loads `database/patient_records_sample.csv`, trains the repository's triage modeling pipeline, and writes a serialized model plus held-out metric output. The documented model is a preprocessing pipeline with a class-balanced 200-tree random forest. The benchmark harness retrains from the synthetic data and records held-out quality, timing, throughput, memory, and test-coverage evidence in `benchmarks/latest.json`.

## Application components

The Streamlit interface in `app.py` is the interactive demonstration surface. `evaluate_model.py` generates a confusion-matrix artifact, while `api_service.java` is a separate Java REST-style console example. Docker, Kubernetes, Ansible, Terraform, and GitHub Actions files describe automation or deployment experiments; they do not establish a clinically deployable service.

## Operational constraints

Benchmark results are in-process measurements on synthetic data; they do not evaluate network latency, concurrent-user load, database behavior, EHR integration, clinical workflows, or patient outcomes. The repository has no clinician-defined outcome protocol, prospective evaluation, external validation, subgroup fairness analysis, calibration study, uncertainty/abstention policy, or regulated quality-management process.

## Required work before any real-world consideration

Any clinical use would require governed representative data, clinician-defined outcomes, external and prospective validation, safety and hazard analysis, fairness and calibration studies, privacy and security controls, model governance, audit logging, human oversight, regulatory review, and continuous monitoring.

## Evidence in this repository

- `train_model.py` and `triage/modeling.py` implement the deterministic training/evaluation path.
- `benchmarks/run_benchmark.py`, `benchmarks/latest.json`, and `benchmarks/benchmark_report.md` contain the benchmark harness and evidence.
- `model_card.md` records the safety boundary, inputs, outputs, and limitations.
