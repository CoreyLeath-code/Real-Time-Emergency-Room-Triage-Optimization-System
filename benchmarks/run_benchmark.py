#!/usr/bin/env python3
"""Reproducible benchmark for the saved MediTriage model artifact.

Uses only synthetic repository data. No clinical records or PHI are processed.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import resource
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from triage.modeling import evaluate, load_dataset, split_dataset

SEED = 20260719


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def repeated_rows(frame: pd.DataFrame, size: int) -> pd.DataFrame:
    repeats = math.ceil(size / len(frame))
    return pd.concat([frame] * repeats, ignore_index=True).iloc[:size]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=5_000)
    parser.add_argument("--warmup", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/latest.json"))
    args = parser.parse_args()
    if args.iterations < 100 or args.warmup < 10:
        parser.error("iterations must be >= 100 and warmup must be >= 10")

    features, target = load_dataset("database/patient_records_sample.csv")
    _, x_test, _, y_test = split_dataset(features, target)

    tracemalloc.start()
    load_started = time.perf_counter_ns()
    model = joblib.load("ml_model/triage_model.pkl")
    artifact_load_ms = (time.perf_counter_ns() - load_started) / 1_000_000

    single = x_test.iloc[[0]]
    for _ in range(args.warmup):
        model.predict_proba(single)

    timings_us: list[float] = []
    started_all = time.perf_counter_ns()
    for _ in range(args.iterations):
        started = time.perf_counter_ns()
        model.predict_proba(single)
        timings_us.append((time.perf_counter_ns() - started) / 1_000)
    elapsed_s = (time.perf_counter_ns() - started_all) / 1_000_000_000

    scale_results = {}
    for size in (1, 10, 100, 1_000, 10_000):
        batch = repeated_rows(x_test, size)
        started = time.perf_counter_ns()
        model.predict_proba(batch)
        duration_s = (time.perf_counter_ns() - started) / 1_000_000_000
        scale_results[str(size)] = {
            "duration_ms": duration_s * 1_000,
            "samples_s": size / duration_s,
        }

    _, peak_python_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_scale = 1024 if sys.platform != "darwin" else 1
    metrics = evaluate(model, x_test, y_test)

    result = {
        "schema_version": 1,
        "benchmark": "meditriage-random-forest-artifact",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": __import__("os").cpu_count(),
            "device": "cpu",
        },
        "protocol": {
            "iterations": args.iterations,
            "warmup": args.warmup,
            "dataset": "repository synthetic patient dataset",
            "holdout": "deterministic stratified 20%",
        },
        "artifact_load_ms": artifact_load_ms,
        "single_record_latency_us": {
            "mean": statistics.fmean(timings_us),
            "median": statistics.median(timings_us),
            "p95": percentile(timings_us, 0.95),
            "p99": percentile(timings_us, 0.99),
            "min": min(timings_us),
            "max": max(timings_us),
        },
        "single_record_throughput_s": args.iterations / elapsed_s,
        "batch_scaling": scale_results,
        "memory": {
            "peak_python_tracemalloc_mib": peak_python_bytes / 1_048_576,
            "process_max_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_scale / 1_048_576,
        },
        "heldout_quality": metrics,
        "limitations": [
            "All records are synthetic; metrics do not establish clinical validity.",
            "Benchmark excludes Streamlit, Java integration, containers, network, and concurrent clients.",
            "This software is research-only and must not direct patient care.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
