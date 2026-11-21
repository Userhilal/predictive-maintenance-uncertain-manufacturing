"""Run with: python -m unittest discover -s tests -v"""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_FILE = Path(__file__).resolve().parents[1] / "src" / "preprocessing" / "prepare_ai4i.py"
spec = importlib.util.spec_from_file_location("prepare_ai4i", MODULE_FILE)
ai4i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai4i)


def fixture_rows(n=100):
    rows = []
    for idx in range(n):
        failed = idx % 5 == 0
        row = {"UDI": str(idx + 1), "Product ID": f"M{idx+1}", "Type": "M",
               "Air temperature [K]": "298.1", "Process temperature [K]": "308.2",
               "Rotational speed [rpm]": str(1400 + idx), "Torque [Nm]": "44.1",
               "Tool wear [min]": str(idx), "Machine failure": "1" if failed else "0",
               **{m: "0" for m in ai4i.MODES}}
        if failed:
            row["TWF"] = "1"
        rows.append(row)
    return rows


class TestAI4IPreparation(unittest.TestCase):
    def test_deterministic_disjoint_stratified_split(self):
        rows = fixture_rows()
        a = ai4i.stratified_split(rows, 42)
        b = ai4i.stratified_split(rows, 42)
        self.assertEqual({k: [r["UDI"] for r in v] for k, v in a.items()},
                         {k: [r["UDI"] for r in v] for k, v in b.items()})
        self.assertEqual({k: len(v) for k, v in a.items()},
                         {"train": 70, "validation": 15, "test": 15})
        self.assertEqual(len({r["UDI"] for bucket in a.values() for r in bucket}), 100)
        self.assertEqual({k: sum(r[ai4i.TARGET] == "1" for r in v) for k, v in a.items()},
                         {"train": 14, "validation": 3, "test": 3})

    def test_conflicting_flags_preserved(self):
        rows = fixture_rows()
        rows[1]["RNF"] = "1"
        rows[5]["TWF"] = "0"
        conflicts = ai4i.find_label_conflicts(rows)
        self.assertEqual([r["UDI"] for r in conflicts], ["2", "6"])
        self.assertEqual(rows[1][ai4i.TARGET], "0")

    def test_roundtrip_does_not_change_source_and_excludes_leakage_columns(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d) / "ai4i2020.csv"
            with raw.open("w", encoding="utf-8", newline="") as handle:
                w = csv.DictWriter(handle, fieldnames=ai4i.COLUMNS)
                w.writeheader()
                w.writerows(fixture_rows())
            before = raw.read_bytes()
            report = ai4i.prepare(raw, Path(d) / "processed", expected_sha256=None)
            self.assertEqual(raw.read_bytes(), before)
            self.assertEqual(report["rows"], 100)
            with (Path(d) / "processed" / "train.csv").open(newline="") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, [*ai4i.INPUTS, ai4i.TARGET])
                self.assertEqual(len(list(reader)), 70)
            self.assertEqual(json.loads((Path(d) / "processed" / "quality_report.json").read_text())["rows"], 100)

    def test_duplicate_feature_vector_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d) / "bad.csv"
            rows = fixture_rows()
            rows[1].update({c: rows[0][c] for c in ai4i.INPUTS})
            with raw.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=ai4i.COLUMNS)
                w.writeheader()
                w.writerows(rows)
            with self.assertRaisesRegex(ValueError, "Repeated feature vector"):
                ai4i.load_and_validate(raw)


if __name__ == "__main__":
    unittest.main()
