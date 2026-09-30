from fastapi import Header
from backend.schemas.common import PrototypeActorContext


def get_prototype_actor(
    x_officer_id: str = Header(default="DEMO-OFFICER-01", alias="X-Officer-ID"),
    x_officer_role: str = Header(default="SURVEY_OFFICER", alias="X-Officer-Role")
) -> PrototypeActorContext:
    """
    Extracts simulated prototype actor context for demonstration and audit recording.
    Explicitly designated as SIMULATED_PROTOTYPE.
    """
    return PrototypeActorContext(
        actor_id=x_officer_id,
        role=x_officer_role,
        authorization_mode="SIMULATED_PROTOTYPE",
        notes="Prototype simulation context - does not constitute official legal authority"
    )
