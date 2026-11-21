"""Streaming, read-only quality audit of the 9 original SCANIA Component X CSV files.

Run: python src/preprocessing/audit_scania.py --data-dir data/raw/scania --output data/processed/scania_audit.json
No model training. Intended to be run against complete original files, not samples.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

SPLITS = ("train", "validation", "test")
EXPECTED_VEHICLES = {"train": 23550, "validation": 5046, "test": 5045}
EXPECTED_READOUTS = {"train": 1122452, "validation": 196227, "test": 198140}
SPEC_COLS = {f"Spec_{i}" for i in range(8)}
# Only filenames from the user's Researchdata dataset listing (version 2).
# The original files are not available here; source checksums are NOT invented.
FILES = (
    "train_operational_readouts.csv",
    "train_specifications.csv",
    "train_tte.csv",
    "validation_operational_readouts.csv",
    "validation_specifications.csv",
    "validation_labels.csv",
    "test_operational_readouts.csv",
    "test_specifications.csv",
    "test_labels.csv",
)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def rows_from_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Invalid or duplicate CSV headers: {path.name}")
        columns = list(reader.fieldnames)
        for n, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"Excess columns in {path.name}, line {n}")
            yield columns, row, n

def read_small(path: Path, fields: set[str], kind: str) -> dict:
    ids = set()
    counts = Counter()
    missing = Counter()
    columns = None
    total = 0
    for header, row, line in rows_from_csv(path):
        columns = header
        if set(header) != fields:
            raise ValueError(f"Unexpected {kind} fields in {path.name}: {header}")
        ident = row["vehicle_id"]
        if not ident or ident in ids:
            raise ValueError(f"Empty or duplicate vehicle_id in {path.name}, line {line}")
        ids.add(ident)
        total += 1
        for key, val in row.items():
            if val is None or not val.strip():
                missing[key] += 1
        if kind == "tte":
            if row["in_study_repair"] not in ("0", "1"):
                raise ValueError(f"Invalid repair event at {path.name}:{line}")
            if not math.isfinite(float(row["length_of_study_time_step"])):
                raise ValueError(f"Invalid study time at {path.name}:{line}")
            counts[row["in_study_repair"]] += 1
        if kind == "labels":
            if row["class_label"] not in ("0", "1", "2", "3", "4"):
                raise ValueError(f"Invalid class label at {path.name}:{line}")
            counts[row["class_label"]] += 1
    if columns is None:
        raise ValueError(f"CSV {path.name} has no data rows")
    return {"rows": total, "ids": ids, "counts": dict(sorted(counts.items())),
            "missing_cells_by_column": dict(sorted(missing.items())), "columns": columns}

def audit_readouts(path: Path) -> dict:
    ids: set[str] = set()
    missing = Counter()
    malformed = Counter()
    by_vehicle: dict[str, dict] = {}
    row_count = 0
    feature_cols = None
    for header, row, line in rows_from_csv(path):
        if feature_cols is None:
            if len(header) != 107 or "vehicle_id" not in header or "time_step" not in header:
                raise ValueError(f"Expected 107 operational columns including ID/time in {path.name}; got {len(header)}")
            feature_cols = [c for c in header if c not in {"vehicle_id", "time_step"}]
        vid = row["vehicle_id"]
        if not vid:
            raise ValueError(f"Missing vehicle_id in {path.name}:{line}")
        ids.add(vid)
        time_raw = row["time_step"]
        try:
            t = float(time_raw)
            if not math.isfinite(t) or t < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError(f"Invalid time_step at {path.name}:{line}") from None
        st = by_vehicle.get(vid)
        if st is None:
            by_vehicle[vid] = {"readouts": 1, "first": t, "last": t,
                               "min_time": t, "max_time": t, "backward_steps": 0,
                               "repeated_adjacent_steps": 0}
        else:
            st["readouts"] += 1
            if t < st["last"]:
                st["backward_steps"] += 1
            elif t == st["last"]:
                st["repeated_adjacent_steps"] += 1
            st["last"] = t
            st["min_time"] = min(st["min_time"], t)
            st["max_time"] = max(st["max_time"], t)
        for key in feature_cols:
            val = row[key]
            if val is None or not val.strip():
                missing[key] += 1
            else:
                try:
                    num = float(val)
                    if not math.isfinite(num):
                        malformed[key] += 1
                except ValueError:
                    malformed[key] += 1
        row_count += 1
    if not row_count:
        raise ValueError(f"No readouts in {path.name}")
    return {"rows": row_count, "ids": ids, "columns": len(feature_cols or []) + 2,
            "feature_columns": feature_cols, "missing_values_by_feature": dict(sorted(missing.items())),
            "invalid_values_by_feature": dict(sorted(malformed.items())),
            "max_missing_fraction": max(missing.values(), default=0) / row_count,
            "vehicles_with_backwards_file_order": sum(st["backward_steps"] > 0 for st in by_vehicle.values()),
            "repeated_adjacent_time_steps": sum(st["repeated_adjacent_steps"] for st in by_vehicle.values()),
            "min_readouts_per_vehicle": min(st["readouts"] for st in by_vehicle.values()),
            "max_readouts_per_vehicle": max(st["readouts"] for st in by_vehicle.values()),
            "by_vehicle": by_vehicle}

def audit_folder(folder: Path) -> dict:
    missing_files = sorted(set(FILES) - {p.name for p in folder.glob("*.csv")})
    if missing_files:
        raise FileNotFoundError(f"Missing required CSVs: {missing_files}")
    report = {"status": "RAW_CSV_AUDIT_EXECUTED", "source_version": "2024-34/2",
              "source_url": "https://researchdata.se/en/catalogue/dataset/2024-34/2",
              "checksums": {}, "splits": {}, "warnings": []}
    # Record hashes of the real downloaded files; without a provider hash
    # these are provenance fingerprints, NOT proof of source authenticity.
    for name in FILES:
        report["checksums"][name] = {"sha256": digest(folder / name),
                                     "provider_hash_verified": False}
    report["warnings"].append("File SHA-256 values computed locally but not checked against official provider hashes")
    all_ids = {}
    reference_features = None
    for split in SPLITS:
        reads = audit_readouts(folder / f"{split}_operational_readouts.csv")
        if reference_features is None:
            reference_features = reads["feature_columns"]
        elif reads["feature_columns"] != reference_features:
            raise ValueError(f"Operational feature schema/order differs in {split} split")
        specs = read_small(folder / f"{split}_specifications.csv", {"vehicle_id", *SPEC_COLS}, "specifications")
        target_kind = "tte" if split == "train" else "labels"
        targets = read_small(folder / ("train_tte.csv" if split == "train" else f"{split}_labels.csv"),
                             {"vehicle_id", "length_of_study_time_step", "in_study_repair"}
                             if split == "train" else {"vehicle_id", "class_label"}, target_kind)
        all_ids[split] = reads["ids"]
        if not reads["ids"] == specs["ids"] == targets["ids"]:
            raise ValueError(f"Split {split}: vehicle IDs do not align across all 3 CSVs")
        if (len(reads["ids"]) != EXPECTED_VEHICLES[split] or
                                        reads["rows"] != EXPECTED_READOUTS[split]):
            raise ValueError(f"Split {split}: published vehicle/readout counts do not match")
        if split == "train":
            # Training event marker is about first repair or censoring, not physical breakdown.
            with (folder / "train_tte.csv").open(encoding="utf-8-sig", newline="") as stream:
                endpoints = {r["vehicle_id"]: float(r["length_of_study_time_step"])
                             for r in csv.DictReader(stream)}
            beyond = sum(st["max_time"] > endpoints[vid] for vid, st in reads["by_vehicle"].items())
            if beyond:
                report["warnings"].append(f"{beyond} training vehicles have readouts after study endpoint")
        info = {"vehicles": len(reads["ids"]), "readouts": reads["rows"],
                "operational_columns": reads["columns"],
                "max_feature_missing_fraction": reads["max_missing_fraction"],
                "non_numeric_values": sum(reads["invalid_values_by_feature"].values()),
                "backwards_order_vehicle_count": reads["vehicles_with_backwards_file_order"],
                "repeated_adjacent_time_steps": reads["repeated_adjacent_time_steps"],
                "min_readouts_per_vehicle": reads["min_readouts_per_vehicle"],
                "max_readouts_per_vehicle": reads["max_readouts_per_vehicle"],
                "feature_missing_counts": reads["missing_values_by_feature"],
                "target_counts": targets["counts"],
                "specification_missing_cells": specs["missing_cells_by_column"],
                "target_missing_cells": targets["missing_cells_by_column"]}
        if info["non_numeric_values"]:
            report["warnings"].append(f"{split}: {info['non_numeric_values']} invalid numerical sensor entries")
        report["splits"][split] = info
    for i, a in enumerate(SPLITS):
        for b in SPLITS[i + 1:]:
            overlap = all_ids[a] & all_ids[b]
            if overlap:
                raise ValueError(f"Vehicle IDs shared across {a}/{b} splits: {len(overlap)}")
    report["overall"] = {"vehicles": sum(len(s) for s in all_ids.values()),
                         "readouts": sum(v["readouts"] for v in report["splits"].values()),
                         "disjoint_vehicle_splits": True,
                         "source_data_modified": False}
    return report

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--output", type=Path, default=Path("data/processed/scania_audit.json"))
    args = ap.parse_args()
    result = audit_folder(args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "overall": result["overall"],
                      "warnings": result["warnings"]}, indent=2))

if __name__ == "__main__":
    main()
