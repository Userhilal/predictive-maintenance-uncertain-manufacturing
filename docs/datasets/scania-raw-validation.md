# SCANIA Component X — Phase 2 raw-file audit and data preparation

**Current status: RAW-DATA AUDIT PENDING.** The official nine CSVs have not been acquired or inspected in this environment. This branch provides an executable, fixture-tested validation workflow, **not** a certification of the SCANIA source files. Do not claim measured missingness, key consistency, or RUL performance until the original CSVs have been audited.

## Sources and license

- Version 3: https://researchdata.se/en/catalogue/dataset/2024-34/3
- DOI: https://doi.org/10.5878/bnh5-ka77
- Scientific paper: https://doi.org/10.1038/s41597-025-04802-6
- Published license: CC BY 4.0 with attribution.
- Nine original CSVs, about 1.54 GiB total. Do not commit raw CSVs to GitHub.
- Fingerprint references in the source code are transcribed from the public pdmdata/datasets/scania_x/metadata.json file: https://github.com/kokikwbt/predictive-maintenance . These are third-party transcriptions of source SHA-256 checksums, **not yet independently verified against original files in this workspace**.

## Published dataset characteristics — not independently measured

| Split | Vehicles | Operational readings | Supervision |
|---|---:|---:|---|
| Train | 23,550 | 1,122,452 | repair event/censoring + study duration |
| Validation | 5,046 | 196,227 | five-class repair-proximity labels |
| Test | 5,045 | 198,140 | five-class repair-proximity labels |

Operational readouts have vehicle_id, time_step and 105 anonymized counter/histogram columns (107 columns total). Specifications have a vehicle ID and eight categorical columns, Spec_0 through Spec_7. Training event records provide length_of_study_time_step and in_study_repair; validation and test provide class_label.

The paper reports 2,272 recorded Component X repairs and 21,278 right-censored vehicles in training. A repair event is not automatically a physical breakdown. Time steps are anonymized, not confirmed hours or days.

## Reproduce on a machine with download access

Requirements: Python 3.11+ and enough disk space to keep the original nine CSVs. No extra Python packages.

Download and check all original files:

~~~powershell
py -3.11 scripts/download_scania.py --output data/raw/scania
~~~

You can download through the official website instead if the API blocks automated downloads. If a file already exists but fails the expected SHA-256, the downloader refuses to overwrite it.

Run the complete streaming audit:

~~~powershell
py -3.11 src/preprocessing/audit_scania.py --data-dir data/raw/scania --output data/processed/scania_audit.json
py -3.11 -m unittest discover -s tests -v
~~~

The report is written only to an ignored local location; source files are not modified. The auditor checks:

1. Presence and hash of all nine filenames.
2. Published row counts, vehicle populations, schema and numeric values.
3. Vehicle-ID joins across operational readouts, specifications and targets, and disjoint IDs across splits.
4. Per-feature missingness, nonnumeric and non-finite observations.
5. Readout time-step validity, ordering warnings, repeated adjacent times, variable sequence lengths.
6. Training repairs and right-censoring labels, test/validation class distribution, events outside study endpoint.
7. Machine-readable JSON output for review.

**Acceptance gate:** only a full successful original-file audit allows the data-preparation phase to be marked complete. Investigate warnings before deriving features or training models.

## Tests actually completed

Four Python unit tests passed locally against **synthetic miniature fixtures**: valid nine-file example, broken vehicle join, invalid time step and missing source file. These verify basic program behavior. They **do not prove** original SCANIA passes the checks.

## Constraints in the project architecture

- SCANIA describes real trucks, not an actual manufacturing production line.
- SCANIA, AI4I and the fault-image set describe different machines and cannot be merged as simultaneous sensor/image readings.
- Never expose future outcome timestamps as past-time predictive features.
- A right-censored vehicle (in_study_repair = 0) is not guaranteed never to fail.
- Future time-to-event modeling must specify cutoffs, valid labels, train-only transformations and censoring-aware evaluation.
- Manufacturing downtime, production dependencies, detailed manuals and repair-versus-replacement purchasing costs require additional evidence or openly labeled simulations.

Open issue: https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/4
