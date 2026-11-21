"""Run: python -m unittest discover -s tests -v (requires Pillow)."""
import csv
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "preprocessing" / "prepare_fault_images.py"
spec = importlib.util.spec_from_file_location("prepare_fault_images", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def sample(fmt="PNG", color="red"):
    buf = io.BytesIO()
    Image.new("RGB", (80, 70), color=color).save(buf, fmt)
    return buf.getvalue()

class TestFaultImages(unittest.TestCase):
    def fixture(self, root):
        archive = root / "images.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for class_idx, category in enumerate(mod.CLASSES):
                for i in range(6):
                    z.writestr(f"Dataset/{category}/{i}.png",
                               sample(color=(i*25, 30+15*class_idx, 100)))
            z.writestr("Dataset/Crack/repeat.png", sample(color=(25, 30, 100)))
            z.writestr("Dataset/Wear/conflict.png", sample(color=(0, 30, 100)))
            z.writestr("Dataset/Wear/photo.png", sample("JPEG", color="green"))
        manual = root / "manual.csv"
        manual.write_text(
            "path,reason,review_status\nDataset/Normal condition/2.png,ambiguous,pending\n",
            encoding="utf-8")
        return archive, manual

    def test_exact_duplicates_conflicts_and_review(self):
        with tempfile.TemporaryDirectory() as d:
            archive, manual = self.fixture(Path(d))
            rows, _ = mod.read_images(archive, None)
            mod.assign_review_status(rows, mod.read_review_queue(manual))
            by_path = {r["path"]: r for r in rows}
            self.assertEqual(by_path["Dataset/Crack/0.png"]["status"],
                             "quarantine_conflicting_labels")
            self.assertEqual(by_path["Dataset/Wear/conflict.png"]["status"],
                             "quarantine_conflicting_labels")
            self.assertEqual(by_path["Dataset/Crack/repeat.png"]["status"],
                             "exclude_same_class_duplicate")
            self.assertEqual(by_path["Dataset/Normal condition/2.png"]["status"],
                             "quarantine_manual_review")
            self.assertEqual(by_path["Dataset/Wear/photo.png"]["image_format"], "JPEG")
            self.assertTrue(by_path["Dataset/Wear/photo.png"]["extension_mismatch"])

    def test_deterministic_source_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive, manual = self.fixture(root)
            raw = archive.read_bytes()
            a = mod.prepare(archive, root/"one", manual, expected_sha256=None)
            b = mod.prepare(archive, root/"two", manual, expected_sha256=None)
            self.assertEqual(archive.read_bytes(), raw)
            self.assertEqual((root/"one"/"provisional_splits.csv").read_bytes(),
                             (root/"two"/"provisional_splits.csv").read_bytes())
            self.assertEqual(a["status_counts"], b["status_counts"])
            self.assertEqual(json.loads((root/"one"/"quality_report.json").read_text())["total_images"], 33)

    def test_unsafe_path_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d)/"unsafe.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("Dataset/Crack/../../evil.png", sample())
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                mod.read_images(archive, None)

    def test_wrong_archive_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            archive, _ = self.fixture(Path(d))
            with self.assertRaisesRegex(ValueError, "Unexpected ZIP SHA-256"):
                mod.read_images(archive, "0"*64)

if __name__ == "__main__":
    unittest.main()
