"""Retrieve existing SCANIA histories, never infer failure mechanisms or expose labels as predictors."""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

from build_integration import SCANIA_SHA, VEHICLES, READOUTS, TARGETS, digest, require, csv_read

FIELDS = ('source_split', 'vehicle_id', 'readout_file', 'first_data_row', 'last_data_row',
          'readout_count', 'contiguous_data_rows', 'first_time_step', 'last_time_step',
          'target_file', 'native_target_kind', 'native_target_value',
          'original_study_endpoint_time_step', 'ai4i_failure_type', 'photo_link_status', 'same_event_pair')


def read_catalog(catalog):
    fields, rows = csv_read(catalog / 'SCANIA_UNKNOWN/vehicle_histories.csv')
    require(tuple(fields) == FIELDS, 'History schema changed')
    by_key = {}
    ids = set()
    for r in rows:
        key = (r['source_split'], r['vehicle_id'])
        require(key[0] in VEHICLES and bool(key[1]) and key[1] not in ids, 'Invalid or duplicate vehicle')
        ids.add(key[1])
        by_key[key] = r
        require(r['ai4i_failure_type'] == 'UNKNOWN' and r['photo_link_status'] == 'NO_VERIFIED_ASSOCIATION'
                and r['same_event_pair'] == 'false', 'Unsupported SCANIA association')
    require(len(by_key) == sum(VEHICLES.values()), 'History population changed')
    return by_key


def retrieve_many(scania, split, selected):
    """Stream exact source rows once per split; check chosen catalog rows against native sources."""
    require(split in VEHICLES and bool(selected), 'Invalid split or empty selection')
    require(all(r['source_split'] == split and r['vehicle_id'] == vid for vid, r in selected.items()), 'Selection mismatch')
    src = f'{split}_operational_readouts.csv'
    target = f'{split}_tte.csv' if split == 'train' else f'{split}_labels.csv'
    col = 'in_study_repair' if split == 'train' else 'class_label'
    for name in (src, target):
        require(digest(scania / name) == SCANIA_SHA[name], f'Original SCANIA SHA mismatch: {name}')
    headers, targets = csv_read(scania / target)
    require(set(headers) == ({'vehicle_id', col} | ({'length_of_study_time_step'} if split == 'train' else set())), 'Native target schema changed')
    labels = {r['vehicle_id']: r for r in targets}
    require(len(labels) == len(targets) == VEHICLES[split] and selected.keys() <= labels.keys(), 'Native target population mismatch')
    histories = {vid: [] for vid in selected}
    with (scania / src).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        require(len(header) == len(set(header)) == 107 and {'vehicle_id', 'time_step'} <= set(header), 'Readout schema changed')
        vi, ti = header.index('vehicle_id'), header.index('time_step')
        sensors = [h for h in header if h not in ('vehicle_id', 'time_step')]
        positions = [header.index(h) for h in sensors]
        count = 0
        for count, row in enumerate(reader, 1):
            require(len(row) == len(header), 'Malformed original SCANIA readout')
            vid = row[vi]
            if vid in histories:
                histories[vid].append({'original_data_row': count, 'time_step': row[ti],
                                       'sensor_values': [row[i] for i in positions]})
    require(count == READOUTS[split], 'Original readout population changed')
    results = {}
    for vid, readings in histories.items():
        require(bool(readings), f'No original readouts for {vid}')
        times = [Decimal(r['time_step']) for r in readings]
        require(all(t.is_finite() and t >= 0 for t in times) and all(a < b for a, b in zip(times, times[1:])), 'Invalid chronology')
        first, last = readings[0], readings[-1]
        native = labels[vid]
        expected = dict(zip(FIELDS, (split, vid, src, str(first['original_data_row']), str(last['original_data_row']),
                    str(len(readings)), str(last['original_data_row'] - first['original_data_row'] + 1 == len(readings)).lower(),
                    first['time_step'], last['time_step'], target,
                    'REPAIR_EVENT_OR_RIGHT_CENSOR' if split == 'train' else 'REPAIR_PROXIMITY_AT_LAST_READOUT',
                    native[col], native.get('length_of_study_time_step', ''), 'UNKNOWN', 'NO_VERIFIED_ASSOCIATION', 'false')))
        require(selected[vid] == expected, f'Catalog history or native target differs from original: {split}/{vid}')
        results[vid] = {'source_split': split, 'vehicle_id': vid, 'sensor_columns': sensors,
                        'readouts': readings, 'failure_mechanism': 'UNKNOWN', 'photo_association': None,
                        'sensor_encoding': 'Original CSV strings; empty strings remain missing; no imputation',
                        'usage': 'Complete observed history for inspection only; apply an as-of cutoff before any prediction.'}
    return results


def smoke_test(scania, catalog):
    rows = read_catalog(catalog)
    counts = {}
    for split in VEHICLES:
        candidates = [r for (s, _), r in rows.items() if s == split]
        require(len(candidates) == VEHICLES[split], 'Split history count changed')
        selected = {r['vehicle_id']: r for r in (candidates[0], candidates[-1])}
        noncontiguous = next((r for r in candidates if r['contiguous_data_rows'] == 'false'), None)
        if noncontiguous:
            selected[noncontiguous['vehicle_id']] = noncontiguous
        found = retrieve_many(scania, split, selected)
        counts[split] = {'histories_verified': len(found), 'readouts_verified': sum(len(r['readouts']) for r in found.values()),
                         'noncontiguous_history_tested': noncontiguous is not None}
    return counts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scania-data', type=Path, required=True)
    p.add_argument('--catalog', type=Path, default=Path('data/processed/three_source_catalog_v1'))
    p.add_argument('--split', choices=tuple(VEHICLES), required=True)
    p.add_argument('--vehicle-id', required=True)
    a = p.parse_args()
    rows = read_catalog(a.catalog)
    key = (a.split, a.vehicle_id)
    require(key in rows, 'Vehicle not found in requested source split')
    print(json.dumps(retrieve_many(a.scania_data, a.split, {a.vehicle_id: rows[key]})[a.vehicle_id], indent=2))


if __name__ == '__main__':
    main()
