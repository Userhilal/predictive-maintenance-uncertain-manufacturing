"""Regression tests on actual original photo data; modify isolated copies only."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from finalise import build
from validate_and_correct import run, csv_read, write, sha
from verify_published import verify


def main(archive):
    tests = []
    with tempfile.TemporaryDirectory(prefix='published-tests-') as t:
        p = Path(t)
        root = p / 'canonical'
        build(archive, root, p, photos_only=True)
        good = p / 'published'
        run(root, archive, p, good, True)
        before = {f.relative_to(good).as_posix(): sha(f) for f in good.rglob('*') if f.is_file()}
        result = verify(root, archive, p, good, True)
        assert result['output_files_verified'] == 12
        assert before == {f.relative_to(good).as_posix(): sha(f) for f in good.rglob('*') if f.is_file()}
        tests.append('clean published view, read-only')

        def corrupt(name, mutation):
            bad = p / 'bad'
            shutil.copytree(good, bad)
            try:
                mutation(bad)
                try:
                    verify(root, archive, p, bad, True)
                except (ValueError, FileNotFoundError):
                    tests.append(name)
                else:
                    raise AssertionError('Accepted corruption: ' + name)
            finally:
                shutil.rmtree(bad)

        def change_link(bad, forge_report=False):
            f = bad / 'class_photo_links.csv'
            fields, rows = csv_read(f)
            rows[0]['verified_target'] = 'TWF'
            f.unlink()
            write(f, fields, rows)
            if forge_report:
                r = bad / 'report.json'
                obj = json.loads(r.read_text(encoding='utf-8'))
                obj['output_sha256']['class_photo_links.csv'] = sha(f)
                r.write_text(json.dumps(obj, indent=2), encoding='utf-8')

        def change_policy(bad):
            f = bad / 'data_policy.json'
            obj = json.loads(f.read_text(encoding='utf-8'))
            obj['photo_training_eligible'] = True
            f.write_text(json.dumps(obj, indent=2), encoding='utf-8')

        def change_report(bad):
            f = bad / 'report.json'
            obj = json.loads(f.read_text(encoding='utf-8'))
            obj['supervised_multimodal_ready'] = True
            f.write_text(json.dumps(obj, indent=2), encoding='utf-8')

        corrupt('modified link', change_link)
        corrupt('modified link with forged checksum', lambda b: change_link(b, True))
        corrupt('changed eligibility policy', change_policy)
        corrupt('changed report', change_report)
        corrupt('missing output', lambda b: (b / 'coverage.csv').unlink())
        corrupt('extra file', lambda b: (b / 'unexpected.txt').write_text('test', encoding='utf-8'))
        corrupt('extra directory', lambda b: (b / 'unexpected').mkdir())
        try:
            verify(root, archive, p, good, False)
        except FileNotFoundError:
            tests.append('missing full AI4I source rejected')
        else:
            raise AssertionError('Full audit accepted missing AI4I source')
    return {'passed': len(tests), 'failed': 0, 'scope': 'actual original photo side; missing AI4I negative test', 'tests': tests}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--images-zip', type=Path, required=True)
    print(json.dumps(main(ap.parse_args().images_zip), indent=2))
