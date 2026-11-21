# SCANIA Component X — Original-source-only validation

**Status: ORIGINAL SCANIA CSV AUDIT COMPLETED LOCALLY — DETAILED ACCEPTANCE REVIEW OPEN.** The owner ran the validator against nine original CSVs and reported 33,641 vehicles, 1,516,819 readouts, disjoint vehicle splits, and verified vehicle-target linkage. See the [measured audit findings](scania-audit-results-2026-11-21.md) for per-split checks, actual target distributions, and limits. No fabricated measurements, example trucks, mock sensor values, or synthetic fixture records are included.

## Only permitted SCANIA data source

https://researchdata.se/en/catalogue/dataset/2024-34/2

Use the nine original CSVs under **Data files**, and the two documentation PDFs listed by that dataset. Downloaded CSVs must not be edited in place or replaced with guessed data. The owner obtained the original files locally and successfully executed the repository audit. This hosted execution environment still has not inspected the original CSV bytes directly.

**Important provenance:** The scripts compute SHA-256 values for each downloaded CSV so the user can track its exact bytes. No trusted official checksums were retrieved from the user-supplied source, so the scripts **do not claim** that a computed hash is verified against an official reference. Previous third-party checksum references have been removed.

## Published data structure (not independently validated in the original files)

| Partition | Vehicles | Operational readings | Accompanying target data |
|---|---:|---:|---|
| Training | 23,550 | 1,122,452 | length_of_study_time_step, in_study_repair |
| Validation | 5,046 | 196,227 | class_label |
| Test | 5,045 | 198,140 | class_label |

Readout fields: vehicle_id, time_step and 105 anonymized operational counters/histogram values. Specification files: vehicle_id plus Spec_0 through Spec_7. The number of repairs reported for training is 2,272; other vehicles are observed without a recorded repair event in the study window (right-censored). A repair record is not the same as a guaranteed physical breakdown. The time-step unit is anonymized.

The population and readout counts in this table were subsequently matched by the owner's actual-file audit, as documented in the [audit results](scania-audit-results-2026-11-21.md). Other detailed checks and source-hash comparison remain open.

## Optional GitHub Actions audit (original files only)

After merging the workflow into main, open **Actions → Validate original SCANIA Component X files → Run workflow**.
The workflow is **manual only**: it does not run automatically and will consume a GitHub-hosted runner only when explicitly started.
It downloads the nine CSVs **only from the user-provided Researchdata SCANIA version 2 link**, validates their actual contents and uploads **only the JSON quality report** as an Actions artifact (kept for 30 days).
The raw source CSVs are not added to the repository or uploaded as artifacts.
If Researchdata blocks downloads from GitHub-hosted runners too, the workflow will fail honestly and no dataset will be fabricated.
GitHub Actions must be enabled for the repository. Keep the issue open until a successful run has been reviewed.
## November 21, 2026: failed workflow run and corrected procedure

- GitHub Actions [run #1](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/actions/runs/44891907761) stopped with **HTTP 404** while downloading the first original CSV. All subsequent CSV validation steps were skipped; there is no verified raw-data report.
- The download tool now tries two routes operated by the **same user-supplied SCANIA version-2 source**: the Researchdata `filePath` link, then SND's version-2 catalogue download path. Both could still fail if the upstream servers reject automated requests.
- The workflow first attempts the small original train_tte.csv file, then the other original files. No mock observations are created to fill gaps.
- If the download fails again, visit [the original dataset page](https://researchdata.se/en/catalogue/dataset/2024-34/2), download the exact listed CSVs using your browser into data/raw/scania, and run the audit locally. If browser links also fail, contact Researchdata/SND; do not replace the data with another dataset.
- The original published data descriptor lists train_tte.csv with two data columns and specifications with eight categorical columns. The audit now supports these small-file tables with **or without vehicle_id**. When IDs are absent, it checks row totals but **does not invent a row-to-vehicle alignment** and explicitly reports that linkage remains unverified.
- A passing CSV syntax/count audit without verifiable row-to-vehicle target correspondence must **not** be interpreted as approved training-ready RUL data.
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

A missing CSV should stop the audit. Do **not** invent missing SCANIA rows. The owner has completed an original-file audit; inspect the full output and unresolved warnings before signing off final acceptance.

## Unresolved gates

- [x] Obtain all nine original CSVs from the supplied version-2 repository locally.
- [x] Run the original-file audit and confirm population and readout counts match the publisher documentation.
- [ ] Review the complete local JSON report, including all per-feature missing counts and computed fingerprints.
- [ ] Review audit warnings and document any scientifically justified exclusions or transformations.
- [ ] Obtain direct provider checksums, if supplied through the permitted repository, for stronger byte-level provenance.
- [ ] Approve censoring-aware time-to-event modeling after review of the full raw-file report and valid prediction cutoffs.

There are no source-created test fixtures or pretend SCANIA evaluation results in this project. SCANIA truck histories remain **independent** from the Kaggle photographs and Mendeley AI4I manufacturing-style records.
