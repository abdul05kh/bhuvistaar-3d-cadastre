from fastapi import APIRouter
from backend.api.v1.endpoints_parcels import router as parcels_router
from backend.api.v1.endpoints_evidence import router as evidence_router
from backend.api.v1.endpoints_generation import router as generation_router
from backend.api.v1.endpoints_validation import router as validation_router
from backend.api.v1.endpoints_units import router as units_router
from backend.api.v1.endpoints_review import router as review_router
from backend.api.v1.endpoints_correction import router as correction_router
from backend.api.v1.endpoints_approval import router as approval_router
from backend.api.v1.endpoints_audit import router as audit_router
from backend.api.v1.endpoints_export import router as export_router
from backend.api.v1.endpoints_demo import router as demo_router
from backend.api.v1.endpoints_ai import router as ai_router
from backend.api.v1.endpoints_system import router as system_router


api_router = APIRouter()
api_router.include_router(parcels_router)
api_router.include_router(evidence_router)
api_router.include_router(generation_router)
api_router.include_router(validation_router)
api_router.include_router(units_router)
api_router.include_router(review_router)
api_router.include_router(correction_router)
api_router.include_router(approval_router)
api_router.include_router(audit_router)
api_router.include_router(export_router)
api_router.include_router(demo_router)
api_router.include_router(ai_router)
api_router.include_router(system_router)


