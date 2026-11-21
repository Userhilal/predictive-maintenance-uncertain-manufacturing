# SCANIA Component X v2 — Real training endpoint-time diagnostic (2026-11-21)

**Status: EXECUTED — original SCANIA training endpoint timing audit passed the implemented consistency checks.**

**Source:** https://researchdata.se/en/catalogue/dataset/2024-34/2 (one of the three user-provided datasets). Only original SCANIA v2 files were used. No additional dataset, synthetic vehicle, generated source row, fake sensor measurement or fabricated event was introduced.

## Evidence

The owner ran the merged `src/preprocessing/audit_scania_cutoffs.py` locally on **original unmodified SCANIA v2 CSVs** and the previously indexed real observations. The owner supplied the complete printed JSON and a second rendering of the saved `data/processed/scania_cutoff_audit.json` in their PowerShell log.

Command executed:

```powershell
py -3.11 src/preprocessing/audit_scania_cutoffs.py --audit "data/processed/scania_audit.json" --data-dir "PATH_TO_ORIGINAL_SCANIA_V2_DATA_FOLDER" --index-dir "data/processed/scania_observation_index" --output "data/processed/scania_cutoff_audit.json"
```

The preflight returned `ORIGINAL_SCANIA_AUDIT_VERIFIED_FOR_CUTOFF_DIAGNOSTIC`, and the full diagnostic returned `REAL_SCANIA_TRAIN_ENDPOINT_RELATION_AUDITED`.

## Measured original-data results

| Original SCANIA source group | Vehicles | Readouts strictly before endpoint | At endpoint | After endpoint | Vehicles with no pre-endpoint readout |
|---|---:|---:|---:|---:|---:|
| Component X repair observed | 2,272 | 105,852 | 0 | 0 | 0 |
| Right-censored (no repair observed during follow-up) | 21,278 | 1,016,600 | 0 | 0 | 0 |
| **Total** | **23,550** | **1,122,452** | **0** | **0** | **0** |

All 23,550 genuine training vehicles have at least one real operational readout strictly before their recorded endpoint. **Every one of the 1,122,452 existing training observations precedes its vehicle's repair/censoring endpoint.** The report found no original training observation exactly at or after its endpoint.

### Integrity safeguards returned by the real-data script

| Report field | Value |
|---|---|
| `source_hashes_match_original_local_audit` | `true` |
| `source_train_index_matches_original_preparation` | `true` |
| `new_rows_or_observations_created` | `false` |
| `repair_or_failure_labels_generated` | `false` |
| `prediction_cutoffs_selected` | `false` |
| `model_trained` | `false` |
| `raw_source_files_modified` | `false` |
| `publisher_hash_verification` | `false` |

These are the results reported by the *owner's executed script*; the raw CSVs and local output JSON were not copied into GitHub. Matching locally computed hashes to the owner's initial audit is a consistency check, not independent source-publisher integrity verification.

## Interpretation

**PASS — temporal endpoint relationship for the checked original training readouts.** The checked original records do not contain at-endpoint or post-endpoint operational readings, and real vehicle IDs and expected row counts match prior local reports.

**This is not full training-model clearance.** In particular:

1. A future training prediction point **must not be chosen because its remaining time to repair is known**. The endpoint may be used only to derive outcomes **after** a prediction timestamp has been selected independently.
2. A final-readout-per-train-vehicle scheme can depend on how many future readings were recorded, whereas the source validation and test readouts are *already truncated*. An as-of protocol must be specified and justified rather than assuming last training readout is equivalent to validation/test last provided readout.
3. No exact future repair time is supplied for validation/test; they provide original five-class proximity labels for the last provided readout.
4. Right-censored vehicles are not known never to require repairs. Censoring-aware target construction and evaluation are required.
5. Preserving original missing sensor cells and restricting model transforms to training only remain necessary. No imputation was performed by this audit.
6. Training observations of the same truck are correlated. Do not treat all readouts as independently labeled machines.
7. SCANIA is real **truck fleet component** data, not a factory time series. It shares no proven per-equipment identity with the user's original Kaggle fault images or Mendeley AI4I source.

## Remaining data and modeling-readiness gates

- [x] Original nine SCANIA files locally audited, with source versions and local SHA-256 fingerprints recorded.
- [x] Exactly the original 1,516,819 readouts indexed without fabrication.
- [x] Original train readouts verified against repair/censor endpoints: all strictly earlier.
- [ ] Compare publisher checksums from the **same supplied Researchdata source**, if published and accessible; otherwise disclose the provenance limitation.
- [ ] Define a reproducible, outcome-independent as-of observation selection rule before supervised feature/target construction.
- [ ] Define explicit right-censoring treatment, train-only transformations and a held-out evaluation protocol without leaking future repair times.
- [ ] Review separate Kaggle image labels/provenance; SCANIA verification alone does not certify the entire three-source dataset stage.

**Decision:** the original SCANIA data-preparation endpoint QA step is complete for its stated checks; the separate modeling-readiness policies above remain pending. Do not generate extra records to address them.
