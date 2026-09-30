from fastapi import APIRouter
from backend.api.v1.endpoints_parcels import router as parcels_router
from backend.api.v1.endpoints_evidence import router as evidence_router
from backend.api.v1.endpoints_generation import router as generation_router
from backend.api.v1.endpoints_validation import router as validation_router
from backend.api.v1.endpoints_units import router as units_router


api_router = APIRouter()
api_router.include_router(parcels_router)
api_router.include_router(evidence_router)
api_router.include_router(generation_router)
api_router.include_router(validation_router)
api_router.include_router(units_router)
