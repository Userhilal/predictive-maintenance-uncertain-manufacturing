# Architecture notes (proposed, not implemented)

The owner has accepted [three-source independent-evidence integration](../datasets/three-source-integration.md). The original sources are not synchronized or interchangeable.

| Planned module | Source and purpose | Explicit boundary |
|---|---|---|
| Tabular mechanism analysis | AI4I eligible internal benchmark | Publisher-synthetic; five native failure flags, with RNF held-out evaluation unsupported |
| Temporal analysis | Original SCANIA histories and native repair/censor outcomes | Separate source/entity and task, preserve as-of cutoff; do not infer five AI4I mechanisms |
| Visual references | Original Kaggle strict photo view | Exploratory associations; no confirmed AI4I visual labels, no permission-dependent use without verified rights |
| Evidence integration | Source-specific outputs | Each output includes source, entity/context ID, task, target semantics, provenance, uncertainty and eligibility; display independently, no combined diagnosis/probability of unrelated entities |
| Document retrieval | Not established | No approved additional corpus; do not invent documents or citations |
| Impact and decisions | Design only | Real production-loss, cost, repair-versus-replace evidence insufficient; no fabricated values |
| Interface | Proposed dashboard | Show independent contexts, uncertainty, limitations and blocked functions |

The integration catalog is a reference/index layer, not a training set containing paired images and telemetry. The history loader is for complete observed-history inspection; future modeling must enforce an as-of cutoff and preserve vehicle grouping. Model development, RAG and decision implementation are not authorized by the integration audit. No new sources or MATWI.
