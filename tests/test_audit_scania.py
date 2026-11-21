"""Fixture-only checks for SCANIA CSV audit; not evidence about the real dataset."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'src' / 'preprocessing' / 'audit_scania.py'
spec = importlib.util.spec_from_file_location('audit_scania', MODULE)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

def write(path, keys, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

def make_fixture(directory: Path):
    keys = ['vehicle_id', 'time_step'] + [f'feature_{i}' for i in range(105)]
    for split, ids in [('train', ('1', '2')), ('validation', ('3', '4')), ('test', ('5', '6'))]:
        items = []
        for vid in ids:
            for step in ['0.0', '3.0', '12.0']:
                item = dict.fromkeys(keys[2:], '1.1')
                item.update(vehicle_id=vid, time_step=step)
                items.append(item)
        items[0]['feature_0'] = ''
        write(directory / f'{split}_operational_readouts.csv', keys, items)
        write(directory / f'{split}_specifications.csv', ['vehicle_id'] + [f'Spec_{i}' for i in range(8)],
              [{'vehicle_id': vid, **{f'Spec_{i}': 'Cat0' for i in range(8)}} for vid in ids])
        if split == 'train':
            write(directory / 'train_tte.csv', ['vehicle_id', 'length_of_study_time_step', 'in_study_repair'],
                  [{'vehicle_id': vid, 'length_of_study_time_step': '15',
                    'in_study_repair': '1' if vid == '1' else '0'} for vid in ids])
        else:
            write(directory / f'{split}_labels.csv', ['vehicle_id', 'class_label'],
                  [{'vehicle_id': vid, 'class_label': str(n)} for n, vid in enumerate(ids)])

class TestScaniaAudit(unittest.TestCase):
    def test_complete_fixture_and_no_source_changes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            make_fixture(p)
            old = {file.name: file.read_bytes() for file in p.glob('*.csv')}
            report = sc.audit_folder(p, verify_hashes=False, expect_published_counts=False)
            self.assertEqual(report['status'], 'RAW_CSV_AUDIT_EXECUTED')
            self.assertEqual(report['overall']['vehicles'], 6)
            self.assertEqual(report['overall']['readouts'], 18)
            self.assertEqual(report['splits']['train']['target_counts'], {'0': 1, '1': 1})
            self.assertAlmostEqual(report['splits']['train']['max_feature_missing_fraction'], 1/6)
            self.assertEqual(old, {file.name: file.read_bytes() for file in p.glob('*.csv')})

    def test_catches_cross_split_leakage(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            make_fixture(p)
            target = p / 'test_specifications.csv'
            text = target.read_text(encoding='utf-8')
            target.write_text(text.replace('5,Cat0', '1,Cat0'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'vehicle IDs do not align'):
                sc.audit_folder(p, verify_hashes=False, expect_published_counts=False)

    def test_catches_invalid_time_step(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            make_fixture(p)
            target = p / 'train_operational_readouts.csv'
            target.write_text(target.read_text().replace('1,0.0', '1,-3.0', 1), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid time_step'):
                sc.audit_folder(p, verify_hashes=False, expect_published_counts=False)

    def test_catches_missing_original_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            make_fixture(p)
            (p / 'test_labels.csv').unlink()
            with self.assertRaisesRegex(FileNotFoundError, 'Missing required CSVs'):
                sc.audit_folder(p, verify_hashes=False, expect_published_counts=False)

if __name__ == '__main__':
    unittest.main()
