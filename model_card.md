# Model Card: MediTriage AI

## Safety and intended use

MediTriage AI is an educational and research demonstration trained exclusively on synthetic data. It may be used to study reproducible tabular ML, testing, and deployment patterns. **It is not clinically validated, is not a medical device, and must not direct patient care or replace clinician judgment.**

## Model details

- Model: 200-tree random forest in a preprocessing pipeline
- Class weighting: `balanced_subsample`
- Seed: `42`
- Inputs: age, systolic blood pressure, heart rate, temperature, symptom score
- Outputs: 0 low, 1 urgent, 2 immediate
- Data: repository synthetic patient dataset
- Evaluation: deterministic stratified 80/20 split

## Measured held-out evidence

| Metric | Value |
|---|---:|
| Samples | 120 |
| Accuracy | 0.9833 |
| Balanced accuracy | 0.9654 |
| Macro precision | 0.9804 |
| Macro recall | 0.9654 |
| Macro F1 | 0.9718 |
| Weighted OVR ROC-AUC | 0.9997 |
| Low recall | 0.9091 |
| Urgent recall | 1.0000 |
| Immediate recall | 0.9870 |

Confusion matrix (rows actual, columns predicted; low, urgent, immediate): `[[10,1,0],[0,32,0],[0,1,76]]`.

Evidence was generated on 2026-07-19. See [the benchmark report](benchmarks/benchmark_report.md) and [raw JSON](benchmarks/latest.json).

## Limitations and risks

- Synthetic results do not estimate clinical performance.
- Features omit history, comorbidities, medications, allergies, clinician assessment, and contextual factors.
- No prospective, external, subgroup fairness, calibration, or human-factors validation exists.
- The dataset is imbalanced; aggregate accuracy alone is insufficient.
- No uncertainty/abstention policy, safety fallback, or regulated quality-management process exists.
- Distribution shift, missingness, sensor error, and adversarial input behavior are not clinically characterized.

## Required work before any real-world consideration

Governed representative data, clinician-defined outcomes, external validation, fairness and calibration studies, hazard analysis, privacy/security controls, model governance, audit logging, human oversight, regulatory review, and prospective monitoring.

## Maintainer

[CoreyLeath-code](https://github.com/CoreyLeath-code)
