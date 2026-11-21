# Dataset sources and audit status

**Strict source-only policy:** Use only the user-provided Kaggle fault-image dataset, Researchdata SCANIA Component X version 2, and Mendeley AI4I 2020 records. No assistant-generated fake records or synthetic test fixtures. AI4I is synthetic by design in the published original source; never represent it as measured factory data. Source-inaccessible data remains unverified.

This page records **current evidence**, not a certificate that all data is production-ready.

## 1. AI4I 2020

- Source: https://data.mendeley.com/datasets/5ww3zv87y7/1
- Type: synthetic manufacturing-style observations; binary machine failure and separate failure-mode flags.
- Preliminary file audit in the project discussion found strong class imbalance and label disagreements between the global failure flag and individual mode flags. These exceptions must be reviewed, not silently repaired.
- Intended use: baseline failure classification, class-imbalance handling, uncertainty calibration.
- Preparation workflow, verified data-quality counts, and local execution: [AI4I phase 2 preparation](ai4i-preparation.md).
- Limitation: no trustworthy per-machine run-to-failure trajectories.

## 2. SCANIA Component X

- Source: https://researchdata.se/en/catalogue/dataset/2024-34/2
- Type: real operational sequences, vehicle characteristics, repair/event and label files.
- Intended use: time-to-event / survival modeling, censored data, failure-proximity classification, uncertainty analysis.
- Limitation: trucks rather than manufacturing equipment; sensor meanings anonymized.
- **Actual-file audit executed locally (2026-11-21):** 33,641 vehicles, 1,516,819 readouts, valid split separation and reported vehicle-target linkage. No malformed numeric values or backward/repeated adjacent timestamps were found. Highest observed per-feature missing rate was under 1% for each split. Provider hash comparison and full JSON/report acceptance remain open. [See measured results](scania-audit-results-2026-11-21.md).
- File acquisition, integrity validation, executable audit and documented open gates: [SCANIA raw-file audit workflow](scania-raw-validation.md).
- **Real-data audit executed on the original nine CSVs (2026-11-21):** 33,641 vehicles, 1,516,819 operational readouts, ~0.302% aggregate missing sensor cells, with ID disjointness and target linkage verified by the implemented audit. See [SCANIA real audit results](scania-real-audit-results.md). Provider-hash verification and preprocessing policy review remain open.

## 3. Industrial Machinery Fault Image Dataset

- Source: https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data
- Type: separate image classification collection.
- Preliminary audit in the project discussion reported duplicates, conflicting category labels, and provenance concerns. Reconfirm against the original download and preserve its hash.
- Intended use: experimental image classification only, after relabeling/review.
- Reproducible Phase 2 image audit, provisional candidate splits and source review queue: [fault image preparation](fault-images-preparation.md).
- Limitation: no demonstrated links to AI4I or SCANIA machines, sensor histories, or repair outcomes.

## Requirements before modeling

- Maintain separate source-specific identifiers and split boundaries.
- Record source version, license, download URL, and hashes.
- Exclude leakage (including exact/near-duplicate image overlap and time-series history overlap).
- Preserve anomalous labels in the raw archive; document any exclusions or corrections.
- Use metrics appropriate to failures (recall, precision, PR-AUC, calibration, cost-aware metrics), not accuracy alone.
- Document what cannot be inferred: real plant downtime, production connectivity, and equipment-specific replacement economics.
