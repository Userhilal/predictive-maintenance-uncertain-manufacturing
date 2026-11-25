# AI4I + Kaggle — audit correction package

This package supersedes the earlier photo filter for **exploratory class-reference integration only**. No original CSV, image ZIP, canonical data, or existing filtered output is modified. No additional dataset, fabricated pair, new failure target, or model is introduced. SCANIA remains separate; MATWI is excluded.

## Run from the project root (Windows PowerShell)

```powershell
Expand-Archive -Path "$HOME\Downloads\AI4I_Kaggle_corrected.zip" -DestinationPath "." -Force
py -3.11 AI4I_Kaggle_corrected/validate_and_correct.py --images-zip "$HOME\Downloads\archive.zip"
```

Use the actual original archive filename if different. Required original files: `data/raw/ai4i2020.csv` and `data/processed/five_mode_image_annotation/original_ai4i_9973_eligible_five_mode_source_index.csv`. The existing canonical dataset must be at `data/processed/ai4i_kaggle_multimodal_canonical` unless `--dataset` is supplied. Requires Python 3.10+; standard library only. The exact original archive, raw CSV, source index, and annotation file SHA-256 values are checked. Any mismatch stops the run before publishing output. Do not replace hashes to bypass checks.

## What is corrected

- Reconstructs the canonical dataset in a temporary directory from pinned sources, compares exact CSV schemas and rows (including all class-specific tables), and verifies all 225 original distinct image contents. In a full run, checks AI4I raw/index, every canonical measurement and target, exclusions, derived values, source metadata, split membership, and canonical report against the clean reconstruction.
- Checks unique keys, allowed mode/kind pairs, canonical path, safe path resolution, same-event and training flags, rights status, media eligibility, quarantine, all 55 semantic decisions and any existing filtered CSVs. Rejects extra/missing image files. No partial output on validation failure.
- Writes `image_formats_225.csv` with actual JPEG/PNG/WebP signature and recommended extension. Original suffixes and bytes remain untouched; use the actual encoding for downstream decoding.
- Writes `eligible_ai4i/train.csv`, `validation.csv`, and `test.csv` only after successful full verification, preserving 6,981/1,497/1,495 Stage 5 memberships. The older 10,000-row Phase 2 splits must not be consumed. No new random splits. `data_policy.json` specifies an explicit six-field base predictor allowlist; IDs, split metadata and all target columns are excluded from predictors. No feature/model development is authorized.
- Final `coverage.csv` records strict 55 links, not the historical 79-link bridge. `semantic_decisions_55.csv` preserves existing decisions. Photo training eligibility remains false.

## Output

`data/processed/ai4i_kaggle_multimodal_canonical/corrected_review_v1/`

Successful full run status: `CORRECTED_FULL_TECHNICAL_PASS_EXPLORATORY_ONLY`. `report.json` includes source/output hashes, split counts, per-split RNF counts, format mismatches and remaining scientific restrictions. Paths of photos in all manifests are relative to the original canonical dataset root, not the correction output folder. Output will not overwrite an existing correction view. If the validator rejects a file, retain it and inspect the error rather than bypassing the check.

## Tests and limitations

18 regression checks passed in the development environment using the actual original Kaggle ZIP, including clean reconstruction and corruption cases. Re-run if desired: `py -3.11 AI4I_Kaggle_corrected/test_corrections.py --images-zip "$HOME\Downloads\archive.zip"`. The included report is the actual result of those tests. Exact AI4I raw/index files were not available in the development environment, so the full combined run remains to be executed on the owner's machine; missing originals were tested and correctly rejected. No confirmed photo targets, no event pairs, no real AI4I time series, no rights verification. RNF has one eligible tabular positive and no photograph; PWF photos provide context only. A technical pass does not establish scientific or supervised multimodal readiness.

Repository documentation PR #60 is separate. After successful full local verification, the source-only package (no photo bytes or raw datasets) may be versioned in Git; do not commit the actual raw/processed data. The repository documentation alone does not publish the local correction scripts.
