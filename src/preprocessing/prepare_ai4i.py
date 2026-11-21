"""Audit and make leakage-aware AI4I binary-failure splits (standard library only).

Usage:
    python src/preprocessing/prepare_ai4i.py --input data/raw/ai4i2020.csv \
        --output data/processed/ai4i

The source file is never edited. Outputs are local-only (.gitignore).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path

INPUTS = (
    "Type", "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
)
TARGET = "Machine failure"
MODES = ("TWF", "HDF", "PWF", "OSF", "RNF")
COLUMNS = ("UDI", "Product ID", *INPUTS, TARGET, *MODES)
NUMERIC = INPUTS[1:]
SOURCE_SHA256 = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"


def load_and_validate(path: Path) -> tuple[list[dict[str, str]], str]:
    raw = path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(COLUMNS):
            raise ValueError(f"Unexpected columns: {reader.fieldnames!r}")
        rows = list(reader)
    if not rows:
        raise ValueError("Input CSV is empty")
    seen_udis: set[str] = set()
    seen_inputs: set[tuple[str, ...]] = set()
    for line, row in enumerate(rows, 2):
        if any(row.get(c) is None or not row[c].strip() for c in COLUMNS):
            raise ValueError(f"Missing/blank value in CSV line {line}")
        if row["Type"] not in ("L", "M", "H"):
            raise ValueError(f"Unexpected product Type in line {line}")
        if not row["UDI"].isdigit() or row["UDI"] in seen_udis:
            raise ValueError(f"Non-numeric or duplicated UDI in line {line}")
        seen_udis.add(row["UDI"])
        for col in NUMERIC:
            try:
                val = float(row[col])
            except ValueError as exc:
                raise ValueError(f"Non-numeric {col} at line {line}") from exc
            if not math.isfinite(val):
                raise ValueError(f"Non-finite {col} at line {line}")
        if any(row[c] not in ("0", "1") for c in (TARGET, *MODES)):
            raise ValueError(f"Non-binary target/flag in line {line}")
        features = tuple(row[c] for c in INPUTS)
        if features in seen_inputs:
            raise ValueError(f"Repeated feature vector in line {line}: potential split leakage")
        seen_inputs.add(features)
    return rows, sha256


def find_label_conflicts(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows
            if int(row[TARGET]) != int(any(row[m] == "1" for m in MODES))]


def stratified_split(rows: list[dict[str, str]], seed: int = 42) -> dict[str, list[dict[str, str]]]:
    rng = random.Random(seed)
    splits: dict[str, list[dict[str, str]]] = {"train": [], "validation": [], "test": []}
    for label in ("0", "1"):
        bucket = [row for row in rows if row[TARGET] == label]
        rng.shuffle(bucket)
        ntrain = round(len(bucket) * 0.70)
        nval = round(len(bucket) * 0.15)
        splits["train"].extend(bucket[:ntrain])
        splits["validation"].extend(bucket[ntrain:ntrain + nval])
        splits["test"].extend(bucket[ntrain + nval:])
    for bucket in splits.values():
        bucket.sort(key=lambda row: int(row["UDI"]))
    assigned = [row["UDI"] for bucket in splits.values() for row in bucket]
    if len(assigned) != len(rows) or len(set(assigned)) != len(rows):
        raise AssertionError("Split overlap, lost row, or duplicate UDI")
    return splits


def write_csv(path: Path, fieldnames: tuple[str, ...] | list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def prepare(source: Path, output: Path, seed: int = 42,
            expected_sha256: str | None = SOURCE_SHA256) -> dict:
    rows, sha = load_and_validate(source)
    if expected_sha256 and sha.lower() != expected_sha256.lower():
        raise ValueError(f"Source SHA-256 mismatch: got {sha}; expected {expected_sha256}")
    splits = stratified_split(rows, seed)
    conflicts = find_label_conflicts(rows)
    report = {
        "status": "AUDITED_LOCAL_PREPARATION_NOT_MODEL_EVALUATION",
        "source_sha256": sha,
        "source_filename": source.name,
        "rows": len(rows),
        "input_features": list(INPUTS),
        "prediction_target": TARGET,
        "excluded_from_model": ["UDI", "Product ID", *MODES],
        "type_counts": dict(sorted(Counter(r["Type"] for r in rows).items())),
        "label_counts": dict(sorted(Counter(r[TARGET] for r in rows).items())),
        "failure_mode_positive_counts": {m: sum(r[m] == "1" for r in rows) for m in MODES},
        "label_conflicts": len(conflicts),
        "flag_positive_binary_negative": sum(r[TARGET] == "0" for r in conflicts),
        "binary_positive_no_flag": sum(r[TARGET] == "1" for r in conflicts),
        "multi_mode_rows": sum(sum(r[m] == "1" for m in MODES) > 1 for r in rows),
        "missing_cells": 0,
        "duplicate_udi": 0,
        "duplicate_feature_vectors": 0,
        "split_seed": seed,
        "split_policy": "stratified deterministic 70/15/15 by original binary label, rows ordered by UDI in output",
        "splits": {
            name: {"rows": len(bucket), "labels": dict(sorted(Counter(r[TARGET] for r in bucket).items()))}
            for name, bucket in splits.items()
        },
        "limitations": [
            "Synthetic observations, not linked longitudinal machine histories",
            "Random stratified split is an IID benchmark, not a genuine future-time or external-plant evaluation",
            "No imputation or scaling: learn transformations on train data only when modeling",
            "Original contradictory target flags retained and separately reported",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, bucket in splits.items():
        write_csv(output / f"{name}.csv", [*INPUTS, TARGET], bucket)
    assignment = [
        {"UDI": r["UDI"], "split": name, TARGET: r[TARGET]}
        for name, bucket in splits.items() for r in bucket
    ]
    assignment.sort(key=lambda r: int(r["UDI"]))
    write_csv(output / "split_index.csv", ["UDI", "split", TARGET], assignment)
    write_csv(output / "label_conflicts.csv", ["UDI", TARGET, *MODES], conflicts)
    (output / "quality_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Original ai4i2020.csv")
    parser.add_argument("--output", default=Path("data/processed/ai4i"), type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-hash-check", action="store_true", help="Allow documented source variants")
    args = parser.parse_args()
    report = prepare(args.input, args.output, args.seed,
                     expected_sha256=None if args.no_hash_check else SOURCE_SHA256)
    print(json.dumps({k: report[k] for k in
                      ("status", "rows", "label_counts", "label_conflicts", "splits")}, indent=2))


if __name__ == "__main__":
    main()
