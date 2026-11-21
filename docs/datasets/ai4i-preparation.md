# AI4I 2020 — Phase 2 data preparation

**Scope:** auditable preprocessing and a binary machine-failure benchmark split. **No model training or model performance is claimed.**

## Source and provenance

- User-provided file: Predictive maintenance dataset.zip → nested AI4I ZIP → ai4i2020.csv.
- Reference: https://archive.ics.uci.edu/dataset/601/ai4i
- SHA-256 of the provided unmodified CSV: **dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e**
- Keep raw and processed CSVs locally. Neither belongs in GitHub.

## Reproduced file-level findings

| Check | Count |
|---|---:|
| Rows / columns | 10,000 / 14 |
| Missing cells | 0 |
| Unique UDI and Product ID | 10,000 each |
| Duplicate input-feature vectors | 0 |
| Machine failure = 0 / 1 | 9,661 / 339 |
| Product Type L / M / H | 6,000 / 2,997 / 1,003 |
| TWF / HDF / PWF / OSF / RNF positive flags | 46 / 115 / 95 / 98 / 19 |
| Rows with multiple positive failure-mode flags | 24 |
| Binary failure target vs. failure-mode flags inconsistent | 27 |
| Mode positive but overall failure negative | 18 |
| Overall failure positive with no mode flag | 9 |

**Do not automatically correct the 27 disagreements.** The original binary target is retained and conflicting source rows are written to a separate, local label_conflicts.csv for review.

## Predictors and leakage controls

- Inputs: **Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min]**
- Target: **Machine failure** (original binary target).
- Never use **UDI** or **Product ID** as predictors (identifiers).
- Never use **TWF, HDF, PWF, OSF, RNF** to predict Machine failure (outcome-derived labels create target leakage).
- No missing-value imputation, normalization, one-hot encoding, resampling, synthetic oversampling, or scaling is done at this stage. Any fitted transformations must be learned from **training data only** during the modeling phase.

## Stratified split, fixed seed 42

| Split | Total | Normal | Failure |
|---|---:|---:|---:|
| Train | 7,000 | 6,763 | 237 |
| Validation | 1,500 | 1,449 | 51 |
| Test | 1,500 | 1,449 | 51 |

Rows are independently shuffled within original binary target classes (70% / 15% / 15%) and written in UDI order for readability. The local split_index.csv records row provenance; each UDI is assigned to exactly one split. Outputs are restricted to the six predictor columns and the binary target.

**This is an IID synthetic benchmark split, not a true time-based, future-machine, or external-factory split.** AI4I does not contain longitudinal observations for individual machines. The UDI 4001–5000 segment contains **134 failures per 1,000 rows**, versus much fewer in other segments; a future generalization assessment should separately test sensitivity to this source-data concentration.

## Run locally (Windows PowerShell)

1. Extract the nested downloaded archive and put the original file at data/raw/ai4i2020.csv inside the cloned repository.
2. From the repository root, run:

~~~powershell
py -3.11 src/preprocessing/prepare_ai4i.py --input data/raw/ai4i2020.csv --output data/processed/ai4i
py -3.11 -m unittest discover -s tests -v
~~~

The script uses only the Python standard library. It verifies the source SHA by default (use --no-hash-check for a separately documented variant), checks the schema and values, leaves raw input unchanged, and produces ignored local files:

- train.csv, validation.csv, test.csv — six features and original binary target.
- split_index.csv — original UDI-to-split lookup for traceability.
- label_conflicts.csv — all 27 binary-vs-mode flag disagreements.
- quality_report.json — validation counts, source hash, and limitations.

## Phase 2 acceptance checklist

- [x] Verified features, schema, missingness, uniqueness, class balance, source exceptions and SHA.
- [x] Preserved source and documented label conflicts without rewriting targets.
- [x] Deterministic, leakage-aware synthetic benchmark split generator.
- [x] Automated regression tests for split reproducibility, uniqueness, target exceptions, and source preservation.
- [ ] Get independent review of unclear source labels, when available.
- [ ] Add distribution-shift validation before claiming performance beyond this synthetic benchmark.

**Status:** data-preparation implementation tested locally; teammate review and future evaluation still open. SCANIA and Kaggle are separate datasets.
