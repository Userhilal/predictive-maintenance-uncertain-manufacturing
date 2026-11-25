# Predictive Maintenance in an Uncertain Manufacturing Process

An academic project exploring **failure prediction, time-to-event estimation, uncertainty-aware maintenance planning, multimodal retrieval, and decision support** in industrial settings.

> **Project status (2026-11-25):** AI4I–Kaggle exploratory integration passed full owner-local technical validation. SCANIA remains separate; repository-wide Stage 7 source validation and verification of the published corrected view remain pending owner execution. No confirmed photo failure labels, paired physical events, or supervised multimodal readiness. No models, RAG or decision engine implemented.

## Objectives

- Predict failures and estimate time to relevant maintenance events where the data supports it.
- Quantify uncertainty and avoid overconfident maintenance recommendations.
- Investigate visually observable faults using images and technical evidence.
- Assess production impact and compare inspection, repair, and replacement options using explicitly documented assumptions or real cost data.
- Produce an explainable interface for maintainers and decision-makers.

## Datasets

| Dataset | Intended contribution | Limitation |
|---|---|---|
| [AI4I 2020 (user-supplied Mendeley data)](https://data.mendeley.com/datasets/5ww3zv87y7/1) | Synthetic manufacturing-style failure classification | Not a longitudinal per-machine RUL dataset |
| [SCANIA Component X](https://researchdata.se/en/catalogue/dataset/2024-34/2) | Real operational histories and repair/time-to-event data | Collected from trucks; earlier owner-local raw-file audit passed, final Stage 7 recheck pending |
| [Industrial Machinery Fault Images](https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data) | Experimental visual fault classification | Small and mixed-quality image set; labeling and reuse require review |

**These datasets are independent.** No shared machine identifiers link the images, AI4I observations, and SCANIA time series. Do not represent outputs from separate models as synchronized observations of one machine.

See [dataset notes](docs/datasets/README.md) for audit status and data handling guidance.

## Planned system

1. Data understanding, quality audit, and preparation
2. Predictive AI (failure and time-to-event modeling with uncertainty estimates)
3. Multimodal document/image retrieval grounded in evidence
4. Failure impact and maintenance decision support
5. Dashboard, integration, and evaluation

Not all capabilities are directly supported by existing datasets: production links, downtime/costs, and equipment-specific repair-versus-replace decisions need separate evidence or clearly labeled demonstrations.

## Project layout

```text
data/                   # Data download instructions (raw data not committed)
docs/datasets/          # Data provenance and quality notes
docs/architecture/      # System design and evidence boundaries
notebooks/             # Exploratory work once the data phase is approved
AI4I_Kaggle_corrected/  # Authoritative exploratory integration and verification
src/preprocessing/      # Original-source preparation and historical utilities
src/prediction/         # Planned failure and time-to-event models
src/rag/                # Planned evidence retrieval
src/decision_support/   # Planned impact and maintenance decisions
dashboard/              # Planned UI
tests/                  # Test documentation
```

## Collaboration

Work on short-lived task branches, open pull requests into `main`, and request review from a teammate. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Data-source restriction

Only the three user-provided dataset sources (Kaggle industrial machinery fault images, SCANIA Component X Researchdata version 2, and Mendeley AI4I 2020) are permitted as data inputs. Do not create artificial training records, fabricated faults, sensor measurements, simulated maintenance histories, fake documents, or synthetic image examples. AI4I itself is already synthetic **in the original Mendeley publication**; that is source data, not material we generate. The project must state this distinction. Never replace missing SCANIA source files with mock observations or test fixtures. If original files are not available, leave validation pending.

## Data and reproducibility policy

Do **not** commit large raw CSVs, ZIPs, image collections, private documents, API keys, or model outputs. Keep links, download instructions, licenses, checksums, data dictionaries, audit results, and reproducible scripts in the repository. Respect each source's terms and image rights.

## Current priorities

- Verify the existing corrected view with `AI4I_Kaggle_corrected/verify_published.py` on original local sources.
- Execute the independent Stage 7 original-source audit; this is not a SCANIA/image fusion.
- Keep the obsolete Phase 2 10,000-row splits and folder-name proxies historical; use `corrected_review_v1` for the qualified exploratory view.
- Retain image label/rights and SCANIA target-semantics blockers. RNF cannot be evaluated on held-out AI4I splits.
- See [current integration instructions](AI4I_Kaggle_corrected/README.md) before using any generated data.

## License

No license has been selected for this project repository yet. Third-party datasets and documents keep their own licenses and attribution requirements.
