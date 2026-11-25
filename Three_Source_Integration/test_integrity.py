"""Exercise the new comparison guard on real photo outputs; SCANIA retrieval needs original local CSVs."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from build_integration import digest, scania_index, photo_catalog
from load_history import retrieve_many, read_catalog
from verify_integration import compare
from validate_and_correct import run
from finalise import build as build_photos


def main(archive):
    passed = []
    with tempfile.TemporaryDirectory(prefix='three-source-tests-') as t:
        p = Path(t)
        root = p / 'canonical'
        build_photos(archive, root, p, photos_only=True)
        expected, good = p / 'expected', p / 'good'
        report = run(root, archive, p, expected, True)
        run(root, archive, p, good, True)
        _, links, photos = photo_catalog(good)
        assert len(links) == 55 and len(photos) == 133 and len(report['output_sha256']) == 12
        before = {f.relative_to(good).as_posix(): digest(f) for f in good.rglob('*') if f.is_file()}
        compare(good, expected, report)
        assert before == {f.relative_to(good).as_posix(): digest(f) for f in good.rglob('*') if f.is_file()}
        passed.append('real photo reconstruction comparison, read-only')

        def rejected(name, action):
            try:
                action()
            except (ValueError, FileNotFoundError):
                passed.append(name)
            else:
                raise AssertionError('Accepted invalid input: ' + name)

        def mutate(name, change):
            bad = p / 'bad'
            shutil.copytree(good, bad)
            try:
                change(bad)
                rejected(name, lambda: compare(bad, expected, report))
            finally:
                shutil.rmtree(bad)

        def forged(bad):
            f = bad / 'class_photo_links.csv'
            f.write_bytes(f.read_bytes() + b'\n')
            r = bad / 'report.json'
            obj = json.loads(r.read_text(encoding='utf-8'))
            obj['output_sha256']['class_photo_links.csv'] = digest(f)
            r.write_text(json.dumps(obj, indent=2), encoding='utf-8')

        mutate('modified existing photo output', lambda b: (b / 'coverage.csv').write_bytes(b'corrupted test copy'))
        mutate('forged checksum rejected', forged)
        mutate('missing output rejected', lambda b: (b / 'coverage.csv').unlink())
        mutate('extra file rejected', lambda b: (b / 'extra.txt').write_text('test', encoding='utf-8'))
        mutate('extra directory rejected', lambda b: (b / 'extra').mkdir())
        rejected('missing SCANIA source rejected', lambda: scania_index(p / 'missing'))
        rejected('missing history catalog rejected', lambda: read_catalog(p / 'missing'))
        rejected('invalid retrieval split rejected', lambda: retrieve_many(p, 'invalid', {}))
        rejected('empty retrieval selection rejected', lambda: retrieve_many(p, 'train', {}))
    return {'passed': len(passed), 'failed': 0, 'tests': passed,
            'scope': 'Actual original photo-side comparison and fail-closed input tests only; full catalog and real SCANIA retrieval require owner originals.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images-zip', type=Path, required=True)
    print(json.dumps(main(p.parse_args().images_zip), indent=2))
