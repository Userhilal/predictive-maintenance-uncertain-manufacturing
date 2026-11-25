"""Read-only verification of the existing corrected view against pinned originals."""
import argparse
import json
import tempfile
from pathlib import Path

from validate_and_correct import HERE, PINS, require, run, sha


def verify_assets():
    for name, digest in PINS.items():
        require(sha(HERE / name) == digest, f'Pinned annotation changed: {name}')
    return {'status': 'PINNED_ANNOTATIONS_PASS', 'checked': len(PINS)}


def inventory(root):
    require(root.is_dir() and not root.is_symlink(), f'Invalid output root: {root}')
    files, directories = set(), set()
    for p in root.rglob('*'):
        require(not p.is_symlink(), f'Symlink in published view: {p}')
        rel = p.relative_to(root).as_posix()
        if p.is_file():
            files.add(rel)
        elif p.is_dir():
            directories.add(rel)
        else:
            raise ValueError(f'Unexpected filesystem object: {p}')
    return files, directories


def verify(root, archive, project, published, photos_only=False):
    verify_assets()
    root = root.resolve()
    actual = inventory(published)
    with tempfile.TemporaryDirectory(prefix='published-verification-') as scratch:
        expected = Path(scratch) / 'expected'
        report = run(root, archive, project, expected, photos_only)
        require(actual == inventory(expected), 'Published file or directory set differs from reconstruction')
        # The report itself is not trusted: compare with an independent reconstruction.
        observed = json.loads((published / 'report.json').read_text(encoding='utf-8'))
        require(observed == report, 'Published report differs from reconstruction')
        for name, digest in report['output_sha256'].items():
            require(sha(published / name) == digest, f'Published output hash mismatch: {name}')
        require(sha(published / 'report.json') == sha(expected / 'report.json'), 'Published report bytes differ')
    return {
        'status': 'PUBLISHED_PHOTO_SIDE_PASS_ONLY' if photos_only else 'PUBLISHED_FULL_TECHNICAL_PASS_EXPLORATORY_ONLY',
        'full_ai4i_rebuild_verified': not photos_only,
        'output_files_verified': len(report['output_sha256']),
        'report_verified': True,
        'source_sha256': report['source_sha256'],
        'split_counts': report['split_counts'],
        'rnf_positive_by_split': report['rnf_positive_by_split'],
        'verified_image_hashes': report['verified_image_hashes'],
        'strict_photo_references': report['strict_photo_references'],
        'strict_links': report['strict_links'],
        'confirmed_photo_labels': 0,
        'verified_event_pairs': 0,
        'supervised_multimodal_ready': False,
        'source_and_published_files_modified': False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=Path, default=Path('.'))
    ap.add_argument('--dataset', type=Path)
    ap.add_argument('--published', type=Path)
    ap.add_argument('--images-zip', type=Path)
    ap.add_argument('--photos-only', action='store_true')
    ap.add_argument('--check-assets-only', action='store_true')
    a = ap.parse_args()
    if a.check_assets_only:
        if a.images_zip or a.dataset or a.published or a.photos_only:
            ap.error('--check-assets-only cannot be combined with dataset options')
        result = verify_assets()
    else:
        if a.images_zip is None:
            ap.error('--images-zip is required for source verification')
        root = (a.dataset or a.project / 'data/processed/ai4i_kaggle_multimodal_canonical').resolve()
        result = verify(root, a.images_zip, a.project, a.published or root / 'corrected_review_v1', a.photos_only)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
