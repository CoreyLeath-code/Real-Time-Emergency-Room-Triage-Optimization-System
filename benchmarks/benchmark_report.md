# MediTriage Research Benchmark Report

## Safety statement

**Research and educational use only.** This system is trained and evaluated exclusively on synthetic records. It is not clinically validated, is not a medical device, and must not direct patient care or replace clinician judgment.

## Executive summary

| Metric | Measured value |
|---|---:|
| Model artifact load | 86.993 ms |
| Single-record mean / median | 14.304 / 14.226 ms |
| Single-record P95 / P99 | 14.665 / 15.176 ms |
| Single-record min / max | 13.975 / 43.037 ms |
| Sequential throughput | 69.89 predictions/s |
| 10,000-row batch throughput | 248,475.21 samples/s |
| Peak traced Python memory | 2.611 MiB |
| Process maximum RSS | 187.988 MiB |
| Held-out accuracy | 0.9833 |
| Balanced accuracy / macro recall | 0.9654 / 0.9654 |
| Macro precision / F1 | 0.9804 / 0.9718 |
| Weighted one-vs-rest ROC-AUC | 0.9997 |
| Coverage | 92.16% of `triage` package |
| Tests | 6 passed |

## Protocol

- Synthetic repository dataset; no PHI
- Deterministic, stratified 80/20 split with seed 42
- 120 held-out records
- Class-balanced 200-tree random forest, single CPU thread
- 5,000 timed predictions after 200 warm-ups
- Batch scaling at 1, 10, 100, 1,000, and 10,000 synthetic rows
- GitHub-hosted Linux runner: Python 3.10.20, 4 reported CPUs
- Percentiles use linear interpolation
- Python allocations use `tracemalloc`; process memory uses maximum RSS

Reproduce:

```bash
pip install -r requirements.txt
python train_model.py
python benchmarks/run_benchmark.py --output benchmarks/latest.json
```

## Held-out quality

| Class | Recall | Held-out support |
|---|---:|---:|
| Low | 0.9091 | 11 |
| Urgent | 1.0000 | 32 |
| Immediate | 0.9870 | 77 |

Confusion matrix (rows actual, columns predicted; low, urgent, immediate):

```text
[[10, 1, 0],
 [ 0,32, 0],
 [ 0, 1,76]]
```

The class distribution is imbalanced, so balanced accuracy, macro F1, and per-class recall are primary evidence. High synthetic-data scores do not imply calibration, fairness, safety, or clinical validity.

## Scalability

| Batch size | Duration | Throughput |
|---:|---:|---:|
| 1 | 14.297 ms | 69.95 samples/s |
| 10 | 14.111 ms | 708.65 samples/s |
| 100 | 15.617 ms | 6,403.34 samples/s |
| 1,000 | 18.927 ms | 52,835.59 samples/s |
| 10,000 | 40.245 ms | 248,475.21 samples/s |

These are in-process batch results, not concurrent-user or network load tests.

## Regression policy

CI rejects invalid evidence and macro recall below 0.50. On comparable runners, investigate median/P95 regressions above 15%, any drop in class-specific urgent/immediate recall, or coverage below 85%. Baselines change only with a documented environment and rationale.

## Limitations and next evidence

- Synthetic data cannot establish clinical performance, bias, calibration, or operational safety.
- Streamlit, Java integration, container startup, network, concurrency, database, and EHR latency are excluded.
- Prospective evaluation, subgroup fairness, calibration error, uncertainty thresholds, failure-mode testing, and clinician oversight are mandatory before any real-world consideration.

Raw evidence: [latest.json](latest.json). Harness: [run_benchmark.py](run_benchmark.py).
