"""Integrate the three original sources into a reference catalog, never fabricate pairs.

Run from the existing project root. Original SCANIA series remain in the original
CSV files; the vehicle index points to those series and their native targets.
No SCANIA repair-proximity class is a physical failure mechanism.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'AI4I_Kaggle_corrected'))
from verify_published import verify
from validate_and_correct import csv_read, require, MODES, STRICT, EXPECTED

SCANIA_SHA = {
    'train_operational_readouts.csv': 'e01cb0bd87dfab4c9dbad215d51d81282fc0d413be96d6f819ea872fb7a3c715',
    'train_specifications.csv': '47cc9a67aee19d5e2ee8620fe8e467490b2125bacc7787ce781ce9f3c1f0c38f',
    'train_tte.csv': 'd8c2379ed7c95a575dd869730b2b3b96d660317f49e57de300518ff3b08d53a5',
    'validation_operational_readouts.csv': '1e1597eec866588c2ad95eb923555ad719c64b3697d9140f9cec6809349809af',
    'validation_specifications.csv': 'a31e832846538dd7a1829108b69420d9377dcd05d6446d8ac1270a974fc58ae2',
    'validation_labels.csv': 'ad876c95c3696f4cfca2d76212ad6bb3cac6b2d2950a4aeaf218ee8b1548d08c',
    'test_operational_readouts.csv': '81f2709cd339e0ff561f5fd3188d7f431680e32400bd788814880d7759615ba1',
    'test_specifications.csv': '40ac8a111f6d5b416107ec1786f639766ecf1293a1c9c0c0dbf24f14c1c5d0e7',
    'test_labels.csv': '60f923051d4ba1bef4c81166cf9e8ca01daf3b7a29c73016c6f48a23dcfa0223',
}
VEHICLES = {'train': 23550, 'validation': 5046, 'test': 5045}
READOUTS = {'train': 1122452, 'validation': 196227, 'test': 198140}
TARGETS = {'train': {'0': 21278, '1': 2272},
           'validation': {'0': 4910, '1': 16, '2': 14, '3': 30, '4': 76},
           'test': {'0': 4903, '1': 26, '2': 15, '3': 41, '4': 60}}
MODE_NAMES = {'TWF': 'Tool wear failure', 'HDF': 'Heat dissipation failure',
              'PWF': 'Power failure', 'OSF': 'Overstrain failure', 'RNF': 'Random failure'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def scania_index(root):
    for name, expected in SCANIA_SHA.items():
        require(digest(root / name) == expected, f'SCANIA original SHA mismatch: {name}')
    all_ids = set()
    all_rows = []
    schemas = {}
    for split in VEHICLES:
        target_file = f'{split}_tte.csv' if split == 'train' else f'{split}_labels.csv'
        fields, targets = csv_read(root / target_file)
        col = 'in_study_repair' if split == 'train' else 'class_label'
        expected_fields = {'vehicle_id', col} | ({'length_of_study_time_step'} if split == 'train' else set())
        require(set(fields) == expected_fields, f'SCANIA label schema changed: {split}')
        labels = {r['vehicle_id']: r for r in targets}
        require(len(labels) == len(targets) == VEHICLES[split], f'SCANIA vehicle count changed: {split}')
        require(not all_ids.intersection(labels), f'SCANIA split overlap: {split}')
        all_ids.update(labels)
        require(Counter(r[col] for r in targets) == TARGETS[split], f'SCANIA source target counts changed: {split}')
        src = f'{split}_operational_readouts.csv'
        histories = {}
        count = 0
        with (root / src).open(encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)
            require(len(header) == len(set(header)) == 107 and {'vehicle_id', 'time_step'}.issubset(header), f'SCANIA sensor schema changed: {split}')
            schemas[split] = [h for h in header if h not in ('vehicle_id', 'time_step')]
            vi, ti = header.index('vehicle_id'), header.index('time_step')
            for row in reader:
                count += 1
                require(len(row) == len(header), f'Malformed SCANIA source row: {split}:{count}')
                vehicle, time = row[vi], row[ti]
                require(vehicle in labels, f'SCANIA source vehicle missing target: {vehicle}')
                t = Decimal(time)
                require(t.is_finite() and t >= 0, f'Invalid SCANIA time: {vehicle}')
                # Record numbers count data rows, excluding the CSV header.
                if vehicle not in histories:
                    histories[vehicle] = [count, count, 1, time, time]
                else:
                    h = histories[vehicle]
                    require(t > Decimal(h[4]), f'Non-increasing SCANIA time: {vehicle}')
                    h[1], h[2], h[4] = count, h[2] + 1, time
        require(count == READOUTS[split] and histories.keys() == labels.keys(), f'SCANIA history population changed: {split}')
        for vid, h in histories.items():
            r = labels[vid]
            all_rows.append({
                'source_split': split, 'vehicle_id': vid, 'readout_file': src,
                'first_data_row': h[0], 'last_data_row': h[1], 'readout_count': h[2],
                'contiguous_data_rows': str(h[1] - h[0] + 1 == h[2]).lower(),
                'first_time_step': h[3], 'last_time_step': h[4],
                'target_file': target_file,
                'native_target_kind': 'REPAIR_EVENT_OR_RIGHT_CENSOR' if split == 'train' else 'REPAIR_PROXIMITY_AT_LAST_READOUT',
                'native_target_value': r[col],
                'original_study_endpoint_time_step': r.get('length_of_study_time_step', ''),
                'ai4i_failure_type': 'UNKNOWN', 'photo_link_status': 'NO_VERIFIED_ASSOCIATION',
                'same_event_pair': 'false',
            })
    require(len(all_rows) == len(all_ids) == 33641 and sum(int(r['readout_count']) for r in all_rows) == 1516819, 'SCANIA overall population changed')
    require(schemas['train'] == schemas['validation'] == schemas['test'], 'SCANIA sensor column order differs')
    return all_rows, schemas['train']


def photo_catalog(published):
    header, links = csv_read(published / 'class_photo_links.csv')
    _, photos = csv_read(published / 'photo_index.csv')
    require(len(photos) == 133 and len({r['image_id'] for r in photos}) == 133, 'Strict photo count changed')
    require(len(links) == 55 and len({(r['image_id'], r['failure_type']) for r in links}) == 55, 'Photo association count changed')
    require({m: sum(r['failure_type'] == m for r in links) for m in MODES} == STRICT, 'Photo coverage changed')
    for r in links:
        require(r['verified_target'] == 'UNKNOWN' and r['training_eligible'] == r['same_event_pair'] == 'false', 'Unsupported photo target')
    return header, links, photos


def build(project, scania, archive, root, published, out):
    require(not out.exists(), f'Refusing to overwrite existing integration: {out}')
    proof = verify(root, archive, project, published, False)
    require(proof['full_ai4i_rebuild_verified'] and proof['output_files_verified'] == 15, 'Full published view not verified')
    photo_fields, links, photos = photo_catalog(published)
    ai_rows = []
    ai_fields = None
    for split, n in [('train', 6981), ('validation', 1497), ('test', 1495)]:
        fields, rows = csv_read(published / 'eligible_ai4i' / f'{split}.csv')
        require(len(rows) == n and all(r['original_stage5_split'] == split for r in rows), 'AI4I split changed')
        if ai_fields is None:
            ai_fields = fields
        require(fields == ai_fields, 'AI4I split schema mismatch')
        ai_rows.extend(rows)
    require(len({r['UDI'] for r in ai_rows}) == 9973, 'AI4I duplicate/missing UDI')
    # Fail before creating any final output if any original SCANIA source is absent or changed.
    histories, sensor_columns = scania_index(scania)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='.three-source-', dir=out.parent))
    try:
        coverage = []
        for m in MODES:
            selected = [r for r in ai_rows if r[m] == '1']
            require(len(selected) == EXPECTED[m], 'AI4I mode count changed')
            photo_links = [r for r in links if r['failure_type'] == m]
            write_csv(tmp / m / 'ai4i_measurements.csv', ai_fields, selected)
            write_csv(tmp / m / 'photo_links.csv', photo_fields, photo_links)
            coverage.append({'failure_type': m, 'definition': MODE_NAMES[m], 'ai4i_records': len(selected),
                             'exploratory_photo_links': len(photo_links), 'scania_histories_retained': 0,
                             'scania_readouts_retained': 0, 'verified_scania_histories': 0,
                             'verified_timeseries_photo_pairs': 0, 'status': 'NO_SCANIA_MECHANISM_LABEL'})
        normal = [r for r in ai_rows if r['Machine failure'] == '0']
        require(len(normal) == 9643, 'AI4I normal count changed')
        write_csv(tmp / 'NO_FAILURE' / 'ai4i_measurements.csv', ai_fields, normal)
        write_csv(tmp / 'SCANIA_UNKNOWN' / 'vehicle_histories.csv', list(histories[0]), histories)
        _, pf = csv_read(published / 'photo_index.csv')
        write_csv(tmp / 'photo_index.csv', list(photos[0]), pf)
        coverage.append({'failure_type': 'UNKNOWN', 'definition': 'SCANIA mechanism not disclosed', 'ai4i_records': 0,
                         'exploratory_photo_links': 0, 'scania_histories_retained': len(histories),
                         'scania_readouts_retained': sum(r['readout_count'] for r in histories), 'verified_scania_histories': 0,
                         'verified_timeseries_photo_pairs': 0, 'status': '33641_SCANIA_HISTORIES_RETAINED_UNMAPPED'})
        write_csv(tmp / 'coverage.csv', list(coverage[0]), coverage)
        sources = {'scania_source_root': str(scania.resolve()), 'scania_source_hashes': SCANIA_SHA,
                   'scania_sensor_columns': sensor_columns, 'photo_paths_relative_to': str(root.resolve()),
                   'ai4i_published_root': str(published.resolve()), 'ai4i_and_kaggle_source_hashes': proof['source_sha256'],
                   'history_lookup': 'Filter original readout CSV by exact vehicle_id and source_split; preserve time_step order. Data row numbers exclude header; do not assume contiguous unless flag true.',
                   'native_target_policy': 'Source targets only. Train repair/censor is not val/test proximity. Never treat native labels, time endpoints, vehicle IDs or split as model predictors.',
                   'failure_type_join_policy': 'AI4I original mode flags to exploratory photo associations only; no SCANIA mode or pair inferred.'}
        (tmp / 'sources.json').write_text(json.dumps(sources, indent=2), encoding='utf-8')
        report = {'status': 'THREE_SOURCE_CATALOG_BUILT_FAILURE_TYPE_TIME_SERIES_JOIN_BLOCKED',
                  'ai4i_eligible_records': 9973, 'scania_source_files_verified': 9,
                  'scania_vehicles': len(histories), 'scania_readouts_referenced': sum(r['readout_count'] for r in histories),
                  'scania_unknown_mechanism_vehicles': len(histories), 'scania_native_target_counts': TARGETS,
                  'strict_photo_references': len(photos), 'exploratory_photo_associations': len(links),
                  'verified_scania_five_mode_labels': 0, 'verified_timeseries_photo_pairs': 0,
                  'class_level_timeseries_photo_merge_complete': False, 'supervised_multimodal_ready': False,
                  'source_data_modified': False, 'no_new_data_or_model': True, 'coverage': coverage,
                  'output_sha256': {p.relative_to(tmp).as_posix(): digest(p) for p in sorted(tmp.rglob('*')) if p.is_file()}}
        (tmp / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        tmp.rename(out)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path('.'))
    p.add_argument('--scania-data', type=Path)
    p.add_argument('--images-zip', type=Path, required=True)
    p.add_argument('--dataset', type=Path)
    p.add_argument('--published', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--photo-check-only', action='store_true', help='Verify genuine photo-only view; do not build full catalog.')
    a = p.parse_args()
    root = (a.dataset or a.project / 'data/processed/ai4i_kaggle_multimodal_canonical').resolve()
    published = a.published or root / 'corrected_review_v1'
    if a.photo_check_only:
        proof = verify(root, a.images_zip, a.project, published, True)
        _, links, photos = photo_catalog(published)
        result = {'status': 'PHOTO_CATALOG_CHECK_PASS_ONLY', 'strict_photo_references': len(photos),
                  'exploratory_links': len(links), 'verified_timeseries_photo_pairs': 0,
                  'full_integration_executed': False, 'source_verification': proof}
    else:
        if a.scania_data is None:
            p.error('--scania-data is required for full integration')
        result = build(a.project, a.scania_data, a.images_zip, root, published,
                       a.out or a.project / 'data/processed/three_source_catalog_v1')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
