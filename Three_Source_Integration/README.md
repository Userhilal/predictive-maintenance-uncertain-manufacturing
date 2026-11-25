# Three-source independent-evidence integration

Accepted scope: all three original sources contribute to one system, not to a synchronized physical event. AI4I supplies publisher-synthetic tabular failure flags; SCANIA v2 supplies observed operational histories and native repair/censor or repair-proximity outcomes; Kaggle supplies exploratory visual references subject to unresolved reuse rights. No MATWI, additional data, invented labels or pairs, or model development.

## Current catalog (already built successfully by owner)

`data/processed/three_source_catalog_v1/` contains 15 output files and a report, with 9,973 eligible AI4I rows (class tables can overlap), 33,641 SCANIA vehicle history references (1,516,819 original readouts), 133 strict photographic references and 55 exploratory associations. All SCANIA mechanisms remain UNKNOWN. Native targets are not predictors. Earlier AI4I-Kaggle corrected outputs remain authoritative for their own scope. The catalog does not duplicate the raw SCANIA measurements.

## Verify and test retrieval locally (PowerShell, project root)

```powershell
py -3.11 Three_Source_Integration/verify_integration.py --scania-data "$HOME\Documents\2024-34-2\data" --images-zip "$HOME\Downloads\archive.zip" --test-retrieval
```

The verifier rebuilds expected results only in an external temporary directory using the exact pinned raw files and validated AI4I-Kaggle view, checks the complete inventory, all 15 output hashes and the report itself. A forged report does not authorize changed outputs. No existing output is overwritten. Run using the original paths/platform: v1 embeds absolute source paths, and hashes are byte-level. If data moves, reproduce into a new versioned catalog and verify it rather than editing the old report. The expected success status is `THREE_SOURCE_CATALOG_VERIFIED_INDEPENDENT_EVIDENCE_ONLY`.

The optional retrieval test streams each original split and validates the first and last indexed vehicle in each, plus a noncontiguous history if one exists. It compares selected source rows, times, counts, native target metadata and original hashes, preserving all 105 raw sensor columns and missing strings. The compact result contains aggregate counts only. A full source run including retrieval is still pending locally.

For a specific real vehicle, select its exact ID and original split from `SCANIA_UNKNOWN/vehicle_histories.csv`, then run:

```powershell
py -3.11 Three_Source_Integration/load_history.py --scania-data "$HOME\Documents\2024-34-2\data" --split train --vehicle-id "<actual vehicle ID>"
```

This inspection utility rehashes the relevant source readout and native-target files and scans by ID (never assumes contiguous rows). It validates the selected catalog record against those sources. Its output keeps source row ordinal/time metadata separate from the ordered sensor values and does not emit native outcomes as predictors. Full histories are for inspection: any future predictor must use an explicit as-of cutoff and respect the original vehicle splits. This is not a training loader.

## Tests executed in development environment

`test_integrity.py` ran against the original Kaggle ZIP, independently reconstructed photo outputs, and deliberately corrupted isolated copies; 10/10 passed. It also tested missing source/catalog and invalid or empty retrieval inputs. `integrity_test_report.json` records that result. Syntax checks passed. The earlier photo-only `photo_check_report.json` remains historical evidence; the owner's prior full catalog build succeeded. The exact SCANIA/AI4I source files are not available in this development environment, so full post-generation verification and positive history retrieval are NOT yet independently executed here. The optional real-history smoke test above is required for final acceptance. No original data was altered.

Original SCANIA documentation: https://doi.org/10.1038/s41597-025-04802-6 and https://researchdata.se/en/catalogue/dataset/2024-34/2. Native proximity classes do not identify AI4I failure mechanisms. Never merge them as if they did. Future independent evidence outputs must preserve source identity, task, entity context, uncertainty and limitations; no joint per-machine diagnosis or combined probability from unrelated contexts.

## Owner-local final acceptance (2026-11-25)

The full verification command returned `THREE_SOURCE_CATALOG_VERIFIED_INDEPENDENT_EVIDENCE_ONLY`: 15 output files and report verified, nine SCANIA source files, 33,641 vehicles, 1,516,819 readouts, 9,973 eligible AI4I records, 133 strict photo references and 55 links. Retrieval passed for two histories per split (198/124/83 readouts, total 405). Noncontiguous histories were not exercised on real data. Original source and catalog files unchanged. All scientific and permission restrictions remain in force. This supplements earlier pending-execution wording. See [integration acceptance](../docs/datasets/three-source-integration.md).
