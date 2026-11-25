"""Read-only catalog verification against a new reconstruction from original sources."""
import argparse
import json
import tempfile
from pathlib import Path

from build_integration import build, digest, require
from load_history import smoke_test


def inventory(root):
    require(root.is_dir() and not root.is_symlink(), f'Invalid catalog directory: {root}')
    files, dirs = set(), set()
    for p in root.rglob('*'):
        require(not p.is_symlink(), f'Symlink forbidden: {p}')
        rel = p.relative_to(root).as_posix()
        if p.is_file():
            files.add(rel)
        elif p.is_dir():
            dirs.add(rel)
        else:
            raise ValueError(f'Unexpected filesystem object: {p}')
    return files, dirs


def compare(published, expected, report):
    require(inventory(published) == inventory(expected), 'Catalog inventory differs from reconstruction')
    observed = json.loads((published / 'report.json').read_text(encoding='utf-8'))
    require(observed == report, 'Catalog report differs from trusted reconstruction')
    require(set(report['output_sha256']) == inventory(expected)[0] - {'report.json'}, 'Incomplete output hash inventory')
    for name, h in report['output_sha256'].items():
        require(digest(expected / name) == h and digest(published / name) == h, f'Catalog output hash mismatch: {name}')
    require(digest(published / 'report.json') == digest(expected / 'report.json'), 'Catalog report bytes differ')


def verify(project, scania, archive, root, published, catalog, retrieval=False):
    inventory(catalog)
    with tempfile.TemporaryDirectory(prefix='three-source-readonly-') as t:
        expected = Path(t) / 'expected'
        report = build(project, scania, archive, root, published, expected)
        require(len(report['output_sha256']) == 15, 'Unexpected full catalog output count')
        compare(catalog, expected, report)
    result = {'status': 'THREE_SOURCE_CATALOG_VERIFIED_INDEPENDENT_EVIDENCE_ONLY',
              'output_files_verified': 15, 'report_verified': True,
              'scania_source_files_verified': report['scania_source_files_verified'],
              'scania_vehicles': report['scania_vehicles'], 'scania_readouts_referenced': report['scania_readouts_referenced'],
              'ai4i_eligible_records': report['ai4i_eligible_records'], 'strict_photo_references': report['strict_photo_references'],
              'exploratory_photo_associations': report['exploratory_photo_associations'],
              'verified_scania_five_mode_labels': 0, 'verified_timeseries_photo_pairs': 0,
              'supervised_multimodal_ready': False, 'source_and_catalog_files_modified': False}
    if retrieval:
        result['history_retrieval_tests'] = smoke_test(scania, catalog)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path('.'))
    p.add_argument('--scania-data', type=Path, required=True)
    p.add_argument('--images-zip', type=Path, required=True)
    p.add_argument('--dataset', type=Path)
    p.add_argument('--published', type=Path)
    p.add_argument('--catalog', type=Path)
    p.add_argument('--test-retrieval', action='store_true')
    a = p.parse_args()
    root = (a.dataset or a.project / 'data/processed/ai4i_kaggle_multimodal_canonical').resolve()
    print(json.dumps(verify(a.project, a.scania_data, a.images_zip, root, a.published or root / 'corrected_review_v1',
                            a.catalog or a.project / 'data/processed/three_source_catalog_v1', a.test_retrieval), indent=2))


if __name__ == '__main__':
    main()
