# Dataset sources and audit status

This page records **current evidence**, not a certificate that all data is production-ready.

## 1. AI4I 2020

- Source: https://archive.ics.uci.edu/dataset/601/ai4i
- Shared copy: https://data.mendeley.com/datasets/5ww3zv87y7/1
- Type: synthetic manufacturing-style observations; binary machine failure and separate failure-mode flags.
- Preliminary file audit in the project discussion found strong class imbalance and label disagreements between the global failure flag and individual mode flags. These exceptions must be reviewed, not silently repaired.
- Intended use: baseline failure classification, class-imbalance handling, uncertainty calibration.
- Preparation workflow, verified data-quality counts, and local execution: [AI4I phase 2 preparation](ai4i-preparation.md).
- Limitation: no trustworthy per-machine run-to-failure trajectories.

## 2. SCANIA Component X

- Source: https://researchdata.se/en/catalogue/dataset/2024-34/3
- Type: real operational sequences, vehicle characteristics, repair/event and label files.
- Intended use: time-to-event / survival modeling, censored data, failure-proximity classification, uncertainty analysis.
- Limitation: trucks rather than manufacturing equipment; sensor meanings anonymized.
- **Open item:** original CSV contents were not independently audited in this repository. Obtain data and check keys, missingness, sequence order, leakage, and class counts before training.

## 3. Industrial Machinery Fault Image Dataset

- Source: https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data
- Type: separate image classification collection.
- Preliminary audit in the project discussion reported duplicates, conflicting category labels, and provenance concerns. Reconfirm against the original download and preserve its hash.
- Intended use: experimental image classification only, after relabeling/review.
- Limitation: no demonstrated links to AI4I or SCANIA machines, sensor histories, or repair outcomes.

## Requirements before modeling

- Maintain separate source-specific identifiers and split boundaries.
- Record source version, license, download URL, and hashes.
- Exclude leakage (including exact/near-duplicate image overlap and time-series history overlap).
- Preserve anomalous labels in the raw archive; document any exclusions or corrections.
- Use metrics appropriate to failures (recall, precision, PR-AUC, calibration, cost-aware metrics), not accuracy alone.
- Document what cannot be inferred: real plant downtime, production connectivity, and equipment-specific replacement economics.
