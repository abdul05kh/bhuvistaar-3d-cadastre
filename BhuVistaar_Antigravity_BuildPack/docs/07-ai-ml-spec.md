# AI/ML Specification

Do not add AI merely because the PS mentions AI/ML.

MVP critical path is deterministic.

Potential future AI:
- building footprint extraction
- floor count estimation
- floor segmentation
- candidate vertical delineation

Every prediction contains model version, evidence IDs, prediction, confidence, uncertainty/quality flag and timestamp.

If labelled data is unavailable, use synthetic data for pipeline tests and clearly label it. Never fabricate accuracy.

AI output is always a candidate. It cannot infer legal ownership and cannot bypass deterministic validation.
