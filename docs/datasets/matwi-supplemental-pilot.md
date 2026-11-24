# MATWI supplemental pilot — data preparation only

Owner approved adding MATWI as a supplemental source, keeping AI4I, SCANIA and the original Kaggle archive intact. Do not treat this as full four-source readiness or authorize modeling.

## Source and acquisition

De Pauw, Jacobs and Goedemé (2025), MATWI replication data, V1, DOI https://doi.org/10.48804/GK6LHH, CC BY-SA 4.0. Publisher describes 17 tool runs and 1,663 measurements; image/sensor filename links, expert wear measurements in micrometers, and occasional synchronization errors: https://iiw.kuleuven.be/onderzoek/eavise/MATWI/MATWI.

Full download 17.7 GB. Start with only original files:
- labels.csv (534.8 KB): https://rdr.kuleuven.be/file.xhtml?fileId=269912&version=1.0 ; MD5 314fa8c1ff769a3e3c745945e31e1bc8.
- Set1.zip (1.0 GB): https://rdr.kuleuven.be/file.xhtml?fileId=269921&version=1.0 ; MD5 a2146e24541dfad50a1bb5e04c27189e.

Save both unchanged in data/raw/matwi (do not commit data). Run from project root:

```powershell
py -3.11 src/preprocessing/audit_matwi_set1_pilot.py --source-dir "data/raw/matwi" --output-dir "data/processed/matwi_set1_pilot"
```

The script checks both published MD5s, records SHA-256, checks source schema and unique archive basename matches, preserves missing/repeated links and source fields, and writes a local review CSV/report. It refuses overwrites. It does not establish exact timestamp alignment, decode images, inspect waveform contents or certify failure endpoints. Actual source files were not accessible to this implementation session, so real-data execution is pending; schema/path assumptions may need adjustment.

## Taxonomy contract

- MATWI provides a TWF-related wear trajectory, not original AI4I TWF flags. Expert wear quantity is not elapsed tool-wear time. Do not label all images TWF; adjudicate failure endpoints using actual experiment documentation and evidence. Normal/unknown are separate.
- AI4I original five flags stay targets, not inputs; the 27 disputed original records stay excluded. AI4I is publisher-synthetic and does not have physical event links to MATWI.
- Existing Kaggle images retain individual review hypotheses, not verified diagnosis; original rights/quarantine restrictions stay.
- SCANIA original anonymized features and temporal targets stay source-specific; no invented five-mode mapping.
- Separate class-level associations from verified same-event links. MATWI within-source publisher links are not evidence of a shared AI4I or SCANIA machine.
- HDF, PWF, OSF and RNF image-level evidence remains unresolved; random independent failures have no inherent visual signature. Do not invent labels.
- Retain run IDs for eventual group-based partitioning; no training yet.

## Exit gates

Actual pilot download and source audit, timestamp/membership and waveform/image inspection, documented failure endpoint annotation, remaining class evidence, source-compatible mapping and final validation. Full multimodal five-mode dataset readiness remains false.
