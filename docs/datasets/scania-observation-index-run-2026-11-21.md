# SCANIA Component X v2 — Original observation-index run (2026-11-21)

**Outcome: LOCAL ORIGINAL-DATA OBSERVATION INDEX CREATED.** The project owner executed `src/preprocessing/prepare_scania.py` on their locally downloaded, unmodified **nine original CSV files** from the [user-supplied SCANIA Component X version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2). The results below are copied from the owner's **actual `preparation_report.json` terminal output**, not from model-generated records. The raw files and generated index files remain on the owner's computer, not in GitHub.

## Commands completed successfully

From the project root, after [PR #12](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/pull/12) was merged:

```powershell
git pull origin main
py -3.11 src/preprocessing/prepare_scania.py --audit "data/processed/scania_audit.json" --check-audit-only
py -3.11 src/preprocessing/prepare_scania.py --audit "data/processed/scania_audit.json" --data-dir "PATH_TO_ORIGINAL_SCANIA_V2_CSV_FOLDER" --output-dir "data/processed/scania_observation_index"
```

The preflight returned `ORIGINAL_AUDIT_REPORT_ACCEPTED` (33,641 vehicles and 1,516,819 readouts). The complete run returned `REAL_SCANIA_V2_OBSERVATION_INDEX_CREATED`.

## Measured index results (from original records)

| Split | Source vehicles | Original readouts = index rows | Missing sensor cells | Existing readouts with ≥1 missing sensor | First observed readouts with no earlier gap |
|---|---:|---:|---:|---:|---:|
| Train | 23,550 | 1,122,452 | 354,634 | 22,481 | 23,550 |
| Validation | 5,046 | 196,227 | 60,339 | 3,937 | 5,046 |
| Test | 5,045 | 198,140 | 66,403 | 4,164 | 5,045 |
| **Total** | **33,641** | **1,516,819** | **481,376** | **30,582** | **33,641** |

Calculated from the reported genuine counts: **2.016% of readouts** have at least one missing sensor value. Across all 105 source sensor columns, **0.302% of sensor cells** are missing. These are different percentages; the original missing values were not filled.

## Safeguards confirmed by the reported execution

| Report property | Reported result |
|---|---|
| Local source file hashes match the owner's original audit | `true` |
| Official publisher hash comparison | `false` (not verified) |
| Artificial/synthetic observations added | `false` |
| New sensor values created | `false` |
| Imputation or row synthesis performed | `false` |
| Repair targets copied into input index or derived from outcome files | `false` |
| Source CSVs changed | `false` |
| Previous-observation gap derived only from recorded earlier readouts | `true` |
| Training-ready model dataset claimed | `false` |

This step writes **derived metadata about the original observations**, not a new source dataset or prediction targets. The index is one-to-one with the original operational readouts (as checked by script counts), records source line IDs and earlier observed time gaps, and preserves existing train/validation/test boundaries. The 105 source sensor feature values remain only in the original readout CSVs.

## Evidence limitations / acceptance decision

**PASS — Original SCANIA observation indexing completed for the implemented data-preparation checks.** The report's three source readout counts, vehicle counts and missing-value totals match the earlier real `scania_audit.json` report. No invented observation was introduced by the indexing script.

This is **not** approval to train a predictive model yet:

- The full generated index CSVs are **not uploaded**; observations above were reviewed from the user's terminal report. One-to-one integrity depends on the implemented script's checks, not an additional independent audit of every index line.
- The nine original file fingerprints match those recorded during the owner's real-data audit, but **publisher-verified checksums are still unavailable**.
- Missing sensor cells remain missing. Any subsequent model-specific imputation or transformation must be documented, fitted using training data only, and must not invent new source records.
- The appropriate time-to-event observation cutoff, repair/censoring target semantics, and evaluation protocol must be defined before any predictive model training to avoid look-ahead.
- SCANIA is **truck** data, not a real manufacturing process, and has no synchronized machine identifiers with the independent Mendeley AI4I or Kaggle image datasets.
- Image-source label review and provenance remain separate unresolved items in the full three-dataset project.

The [original dataset audit](scania-real-audit-results.md), [preprocessing policy](scania-preprocessing-policy.md), and [Issue #4](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/4) carry the remaining gates. **Use only the three original user-provided datasets; no fabricated test records, additional datasets or synthetic machine histories.**
