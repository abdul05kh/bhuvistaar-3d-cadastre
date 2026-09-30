from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class ModelCard(BaseModel):
    model_id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Human-readable model name")
    version: str = Field(..., description="Semantic version string")
    task: str = Field(..., description="Designated machine intelligence task")
    status: str = Field(default="PROTOTYPE", description="Deployment status: PROTOTYPE, EXPERIMENTAL, BENCHMARKED")
    description: str = Field(..., description="High-level summary of model purpose")
    architecture: str = Field(..., description="Underlying algorithmic architecture")
    inputs: list[str] = Field(..., description="Allowed input modalities and data formats")
    outputs: list[str] = Field(..., description="Output candidate schemas generated")
    training_data_disclosure: str = Field(..., description="Explicit disclosure of training data origin")
    known_limitations: list[str] = Field(..., description="Known edge cases and operational constraints")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Empirical benchmark scores where available")
    intended_use: str = Field(..., description="Legitimate assistance role")
    prohibited_use: str = Field(..., description="Prohibited or unsupported operations")
    license: str = Field(default="Proprietary Prototype / MIT Research", description="Licensing term")
    disclaimer: str = Field(
        default="AI assistance does not constitute legal title adjudication or official 3D ULPIN issuance. Prototype model performance not yet statistically benchmarked for operational field deployment.",
        description="Mandatory model card disclaimer"
    )
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRegistryResponse(BaseModel):
    registered_models: list[ModelCard] = Field(default_factory=list)
    total_models: int = Field(default=0)
