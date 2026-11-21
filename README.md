# Predictive Maintenance in an Uncertain Manufacturing Process

An academic project exploring **failure prediction, time-to-event estimation, uncertainty-aware maintenance planning, multimodal retrieval, and decision support** in industrial settings.

> **Project status:** Dataset understanding is underway; cleaning and preparation are next. No predictive model, multimodal RAG, or decision-support engine is implemented yet.

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
| [SCANIA Component X](https://researchdata.se/en/catalogue/dataset/2024-34/2) | Real operational histories and repair/time-to-event data | Collected from trucks; raw-file audit remains pending |
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
src/preprocessing/      # Planned data quality & preprocessing code
src/prediction/         # Planned failure and time-to-event models
src/rag/                # Planned evidence retrieval
src/decision_support/   # Planned impact and maintenance decisions
dashboard/              # Planned UI
tests/                  # Planned automated checks
```

## Collaboration

Work on short-lived task branches, open pull requests into `main`, and request review from a teammate. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Data-source restriction

Only the three user-provided dataset sources (Kaggle industrial machinery fault images, SCANIA Component X Researchdata version 2, and Mendeley AI4I 2020) are permitted as data inputs. Do not create artificial training records, fabricated faults, sensor measurements, simulated maintenance histories, fake documents, or synthetic image examples. AI4I itself is already synthetic **in the original Mendeley publication**; that is source data, not material we generate. The project must state this distinction. Never replace missing SCANIA source files with mock observations or test fixtures. If original files are not available, leave validation pending.

## Data and reproducibility policy

Do **not** commit large raw CSVs, ZIPs, image collections, private documents, API keys, or model outputs. Keep links, download instructions, licenses, checksums, data dictionaries, audit results, and reproducible scripts in the repository. Respect each source's terms and image rights.

## Current priorities

- Finalize SCANIA raw-file access and complete its file-level validation.
- Resolve the image dataset's duplicate/label conflicts before any vision evaluation.
- Document AI4I target inconsistencies without silently editing the original labels.
- Agree upon project-specific acceptance criteria before modeling.

## License

No license has been selected for this project repository yet. Third-party datasets and documents keep their own licenses and attribution requirements.
