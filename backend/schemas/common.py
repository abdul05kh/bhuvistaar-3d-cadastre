from typing import Any, Optional, Literal
from pydantic import BaseModel, Field


class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(
        ...,
        description="GeoJSON RFC 7946 coordinates: array of linear rings (exterior, followed by optional holes)"
    )


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class PrototypeActorContext(BaseModel):
    actor_id: str = Field(default="DEMO-OFFICER-01", description="Identifier of the executing user")
    role: str = Field(default="SURVEY_OFFICER", description="Simulated prototype role")
    authorization_mode: Literal["SIMULATED_PROTOTYPE"] = "SIMULATED_PROTOTYPE"
    notes: str = "Prototype authorization only - not an official government credential"
