# SCANIA Component X — Original-source-only validation

**Status: ORIGINAL SCANIA CSV AUDIT NOT RUN.** This page describes checks to execute against the original research data. No fabricated measurements, example trucks, mock sensor values, or synthetic fixture records are included.

## Only permitted SCANIA data source

https://researchdata.se/en/catalogue/dataset/2024-34/2

Use the nine original CSVs under **Data files**, and the two documentation PDFs listed by that dataset. Downloaded CSVs must not be edited in place or replaced with guessed data. The files have not been successfully downloaded into our execution environment.

**Important provenance:** The scripts compute SHA-256 values for each downloaded CSV so the user can track its exact bytes. No trusted official checksums were retrieved from the user-supplied source, so the scripts **do not claim** that a computed hash is verified against an official reference. Previous third-party checksum references have been removed.

## Published data structure (not independently validated in the original files)

| Partition | Vehicles | Operational readings | Accompanying target data |
|---|---:|---:|---|
| Training | 23,550 | 1,122,452 | length_of_study_time_step, in_study_repair |
| Validation | 5,046 | 196,227 | class_label |
| Test | 5,045 | 198,140 | class_label |

Readout fields: vehicle_id, time_step and 105 anonymized operational counters/histogram values. Specification files: vehicle_id plus Spec_0 through Spec_7. The number of repairs reported for training is 2,272; other vehicles are observed without a recorded repair event in the study window (right-censored). A repair record is not the same as a guaranteed physical breakdown. The time-step unit is anonymized.

All these numbers are from the original dataset's documentation or published description. They must be **checked against the actual CSV files** before being treated as audited values.

## Optional GitHub Actions audit (original files only)

After merging the workflow into main, open **Actions → Validate original SCANIA Component X files → Run workflow**.
The workflow is **manual only**: it does not run automatically and will consume a GitHub-hosted runner only when explicitly started.
It downloads the nine CSVs **only from the user-provided Researchdata SCANIA version 2 link**, validates their actual contents and uploads **only the JSON quality report** as an Actions artifact (kept for 30 days).
The raw source CSVs are not added to the repository or uploaded as artifacts.
If Researchdata blocks downloads from GitHub-hosted runners too, the workflow will fail honestly and no dataset will be fabricated.
GitHub Actions must be enabled for the repository. Keep the issue open until a successful run has been reviewed.
## Run validation on original files

Requirements: Python 3.11+, free disk space, and direct access to the official Researchdata host.

```powershell
py -3.11 scripts/download_scania.py --output data/raw/scania
py -3.11 src/preprocessing/audit_scania.py --data-dir data/raw/scania --output data/processed/scania_audit.json
```

Both commands work with the research-data files only. The downloader will keep any existing file unchanged rather than overwrite it. The CSV auditor examines the actual rows and checks:

1. Presence of all nine expected source CSVs, computing a SHA-256 fingerprint of each.
2. Exact schema and published vehicle/readout counts.
3. Vehicle ID matching across readouts, specifications, and event/label files.
4. Train/validation/test vehicle-ID separation.
5. Missing, invalid, or non-finite sensor values.
6. Time-step sequences, ordering, and repeated adjacent time steps.
7. Repair and censoring indicators, validation/test label distributions, and study-end boundaries.

A missing CSV should stop the audit. Do **not** invent missing SCANIA rows or mark the dataset validated when the original source is unavailable.

## Unresolved gates

- [ ] Download all nine original CSVs from the supplied version-2 repository.
- [ ] Inspect complete CSVs, record their computed fingerprints and compare their schemas and counts to the publisher documentation.
- [ ] Review audit warnings and document any scientifically justified exclusions or transformations.
- [ ] Obtain direct provider checksums, if supplied through the permitted repository, for stronger byte-level provenance.
- [ ] Approve censoring-aware time-to-event modeling only after the raw-file audit is complete.

There are no source-created test fixtures or pretend SCANIA evaluation results in this project. SCANIA truck histories remain **independent** from the Kaggle photographs and Mendeley AI4I manufacturing-style records.
