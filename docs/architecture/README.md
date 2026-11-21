# Architecture notes (proposed, not implemented)

1. **Data layer:** independently versioned SCANIA, AI4I, image sources, and later authorized manuals/cost information.
2. **Predictive layer:** model-specific failure and time-to-event outputs, each with its uncertainty and evaluation data.
3. **Retrieval layer:** document parsing, retrieval, citations and visual evidence; evidence must not be invented or confused across machine types.
4. **Impact layer:** explicit production-relationship graph and documented costs or simulation assumptions.
5. **Decision layer:** compare inspection, repair, and replacement subject to safety, costs, lead times, and uncertainty.
6. **Interface:** a transparent dashboard showing source, confidence, limits, and recommended action.

Critical design rule: the three source datasets are not aligned at machine level. Cross-source fusion is not automatically valid. A demonstration may compare independently trained modules, but must not claim they observed the same machine.
