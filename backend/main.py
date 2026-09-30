import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.exceptions import BhuVistaarException
from backend.api.v1.router import api_router
from backend.schemas.common import ErrorEnvelope, ErrorDetail

# Configure server-side diagnostic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bhuvistaar")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Machine-assisted 3D Cadastral Intelligence & Validation Platform (Prototype)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BhuVistaarException)
async def domain_exception_handler(request: Request, exc: BhuVistaarException):
    req_id = f"req-{uuid.uuid4()}"
    logger.warning(f"Domain error [{exc.code}] on {request.method} {request.url.path}: {exc.message}")
    
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.code == "VALIDATION_BLOCKER_EXISTS":
        status_code = status.HTTP_409_CONFLICT
    elif exc.code in ("PARCEL_NOT_FOUND", "UNIT_NOT_FOUND", "EVIDENCE_NOT_FOUND"):
        status_code = status.HTTP_404_NOT_FOUND
    elif exc.code == "VUID_COLLISION":
        status_code = status.HTTP_409_CONFLICT

    return JSONResponse(
        status_code=status_code,
        content=ErrorEnvelope(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                request_id=req_id,
                details=exc.details
            )
        ).model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = f"req-{uuid.uuid4()}"
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    # Safe error response: never expose stack traces to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorEnvelope(
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please contact system administrator with the request ID.",
                request_id=req_id,
                details={}
            )
        ).model_dump()
    )


@app.get("/health/live", tags=["Health"])
def health_live():
    return {"status": "ALIVE", "version": "0.1.0"}


@app.get("/health/ready", tags=["Health"])
def health_ready():
    return {
        "status": "READY",
        "canonical_srid": settings.CANONICAL_STORAGE_SRID,
        "canonical_crs": settings.CANONICAL_STORAGE_CRS,
        "authorization_mode": settings.AUTHORIZATION_MODE
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
