"""Model Comparison Schemas (Slice 4)."""
from typing import Any
from pydantic import BaseModel, Field


class ModelComparisonRequest(BaseModel):
    model_a_id: str = "prismatic-candidate-001"
    model_b_id: str = "cadastral-heuristic-baseline-001"
    parent_ulpin: str = "12345678901234"


class ModelComparisonMetric(BaseModel):
    metric_name: str
    model_a_value: Any
    model_b_value: Any
    delta: Any
    observation: str


class ModelComparisonResponse(BaseModel):
    parent_ulpin: str
    model_a: dict[str, Any]
    model_b: dict[str, Any]
    metrics: list[ModelComparisonMetric]
    summary_notes: str
    limitations_disclaimer: str = (
        "Empirical differences observed on controlled synthetic fixture. "
        "No claim of statistical superiority or production suitability without authorized benchmark."
    )
