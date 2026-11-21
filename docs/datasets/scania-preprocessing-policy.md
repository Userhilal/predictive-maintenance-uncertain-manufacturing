# SCANIA Phase 2 — Original-observation preprocessing (no synthetic data)

**Scope:** only the original SCANIA Component X data from the [user's Researchdata version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2). The original raw files are not in GitHub.

## Data evidence

The owner has executed the genuine full-data audit and uploaded its report (SHA-256 of the audit JSON: `b597798721d7e457855be4e927c131c6303cbed28de9fa8a825dac0c181aa512`). See [measured audit findings](scania-real-audit-results.md).

- 33,641 vehicles; 1,516,819 original operational readouts.
- 481,376 sensor-value cells missing out of 159,265,995 (0.302%).
- 2,272 observed training repairs; 21,278 right-censored training vehicles.
- Validated original vehicle IDs are separate between train, validation and test.
- SHA-256 values of each source CSV were computed locally, **not** independently compared with publisher checksums.

## Cleaning rules — strictly original data only

1. **No imputation now.** Keep missing sensor measurements missing in the original raw CSV; do not use zeros, invented averages, fake nearest neighbors, SMOTE, generated images, or synthetic machine histories to replace them. The derived index merely counts how many values were present/missing for each existing observation.
2. **No synthetic rows.** The script outputs exactly one metadata row for every *real* operational readout, retaining its real vehicle ID, real `time_step`, and original CSV row number.
3. **No look-ahead.** The derived observation number, previous observed time and gap use only **earlier recorded observations for the same vehicle**. The first observation has a blank preceding time and blank gap because no earlier original observation exists.
4. **No targets as features.** Original `train_tte.csv`, `validation_labels.csv`, and `test_labels.csv` remain separate and are not used in the derived input index. This avoids attaching future repair or censoring information to earlier predictor rows.
5. **Preserve source partition boundaries.** Never combine vehicle observations from train, validation and test. No reshuffling is done.
6. **Source integrity gate.** Before preparing, all nine current raw CSVs must have identical SHA-256 hashes to those recorded in the actual `scania_audit.json`. The script refuses changed or missing source files. This is local consistency checking, **not publisher hash verification**.
7. **Do not overwrite derived output silently.** The script requires a new destination and writes via a temporary staging directory.

## Run on the computer where original CSVs exist

From the cloned GitHub repository root, first check the existing genuine audit:

```powershell
git pull origin main
py -3.11 src/preprocessing/prepare_scania.py --audit "data/processed/scania_audit.json" --check-audit-only
```

Then create observation-index metadata using the original files already on the owner's laptop:

```powershell
py -3.11 src/preprocessing/prepare_scania.py `
    --audit "data/processed/scania_audit.json" `
    --data-dir "C:\Users\hindh\Documents\2024-34-2\data" `
    --output-dir "data/processed/scania_observation_index"
```

**Only run the second command after merging the pull request adding this script.** If the output folder already exists, the script stops rather than overwriting it.

Outputs (ignored by Git):

- `train_observed_index.csv` — one row per genuine training operational readout.
- `validation_observed_index.csv` — one row per genuine validation readout.
- `test_observed_index.csv` — one row per genuine test readout.
- `preparation_report.json` — counts and strict provenance safeguards.

Each index has exactly eight columns: `vehicle_id`, `time_step`, `original_csv_row`, `observation_index`, `previous_observed_time_step`, `gap_since_previous_time_step`, `available_sensor_values`, and `missing_sensor_values`. These are **metadata derived from existing observations**, not fabricated observations or sensor replacements. The 105 original sensor columns stay in the source files.

## Remaining checks and limitations

- The original SCANIA CSVs are available **only on the user's local computer** in this workflow. The new extraction script was syntax-checked and the actual audit JSON was used for preflight, but a full real-CSV extraction has **not yet been executed or accepted**.
- The source audit found strictly ordered per-vehicle time steps; the extraction checks them again.
- Do not treat a right-censored training vehicle as a confirmed never-fails case.
- For future survival modeling, define **a real as-of prediction cutoff and train-only feature transformations**, avoiding the repair date and any future readings as inputs. No RUL labels or numeric imputation are produced at this step.
- SCANIA is truck-fleet component data, not a manufacturing production line. There is **no matching machine ID** in the independent Mendeley AI4I and Kaggle image datasets.
- The original published AI4I is already synthetic; this project does **not** synthesize extra AI4I/SCANIA/image data.

**Decision:** observation indexing is an implementation proposal. To sign off, run it against the nine original SCANIA v2 files and verify the exported `preparation_report.json` counts match the genuine dataset audit before moving toward training.
