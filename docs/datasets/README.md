# Dataset sources and audit status

**Strict source-only policy:** Use only the user-provided Kaggle fault-image dataset, Researchdata SCANIA Component X version 2, and Mendeley AI4I 2020 records. No assistant-generated fake records or synthetic test fixtures. AI4I is synthetic by design in the published original source; never represent it as measured factory data. Source-inaccessible data remains unverified.

This page records **current evidence**, not a certificate that all data is production-ready.

- **Stage 1 Collection closure in progress:** [original-only local collection inventory and acceptance checklist](stage1-collection-closure.md) verifies nine real SCANIA CSVs, two official SCANIA documentation PDFs, the unchanged AI4I source CSV and the original Kaggle ZIP. The image source's license/per-image rights remain explicitly unverified; no collection sign-off is claimed until the owner runs this inventory. Stages 2–6 are handled separately, one at a time.


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
- **First SCANIA NaN-native model input contract executed successfully locally (2026-11-21):** checked the previously executed real-source manifest, full 105-feature profile and 105-sensor review; status `ORIGINAL_SCANIA_MODEL_INPUT_CONTRACT_PREPARED`. Original 737,995 known-fit / 162,292 unknown-fit and 182,063 known-holdout / 40,102 unknown-holdout retained. No scaling, clipping, imputation, matrix or trained model. See [real contract execution results](scania-model-input-contract-results-2026-11-21.md) and [input policy](scania-model-input-contract-policy.md).
- **Real original-SCANIA 105-feature quality review completed locally (2026-11-21):** 77,263,458 observed plus 226,017 missing original known-fit sensor values (0.291674% missing); zero all-missing/constant or >=1%-missing original features; 95 large standardized-range **review flags, not proven bad source values**. The second invocation simply refused to overwrite the valid first report. See [actual review results](scania-sensor-quality-results-2026-11-21.md) and [quality review policy](scania-sensor-feature-quality-review-policy.md). Train-fit-only model transformations remain to be selected; no model trained.
- **Original-only SCANIA 105-sensor feature profiler executed successfully locally:** 1,122,452 original readouts verified, 737,995 known-outcome training-fit readouts used for observed-value statistics and 162,292 short-censored training-fit readouts excluded; 354,634 original missing training sensor cells verified. See [owner-run profile summary](scania-source-feature-profile-results-2026-11-21.md) and [source-only profiling policy](scania-source-feature-profile-policy.md). The detailed 105-feature JSON has not yet been reviewed; no imputation, synthetic data or model training.
- **Original SCANIA training manifest executed successfully locally (2026-11-21):** 23,550 original vehicles split by vehicle ID into 18,869 internal fit and 4,681 internal holdout; all 1,122,452 genuine train readouts referenced. The outcome-observability totals remain 25,758 known near-repair, 894,300 known no repair within horizon, and 202,394 short-censored UNKNOWN. The script confirmed local source hashes/missingness; no synthetic rows or sensor values. See [measured execution results](scania-training-manifest-results-2026-11-21.md) and [data policy](scania-training-manifest-policy.md). No model has been trained.
- **48-step observed-outcome audit completed on genuine SCANIA v2 training CSVs:** among 1,122,452 existing readouts, 25,758 have known repair within 48 source steps, 894,300 have confirmed no repair *within that horizon*, and **202,394 remain unknown due to short-censored follow-up**. See [measured 48-step results](scania-horizon48-audit-results-2026-11-21.md) and [safety policy](scania-horizon48-protocol.md). Counts are for observations, not independent vehicles; no fake rows, sensor values or training labels created.
- **Real SCANIA train endpoint-time QA completed locally (2026-11-21):** all 1,122,452 original training readouts strictly precede their repair/censoring endpoint; no readings at or after endpoint. See [measured cutoff audit](scania-cutoff-audit-results-2026-11-21.md) and [safety policy](scania-event-cutoff-policy.md). Prediction-time selection and censoring-aware model protocol are still to be defined; no labels or synthetic rows generated.
- **Original SCANIA observation indexing completed locally:** owner-reported 1,516,819 original readouts indexed, 33,641 vehicles, 481,376 original missing sensor cells preserved and 30,582 real readouts containing at least one missing sensor. See [executed observation-index results](scania-observation-index-run-2026-11-21.md) and the [source-only preprocessing policy](scania-preprocessing-policy.md). No synthetic measurements, row synthesis, imputation, or future repair labels introduced.
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
