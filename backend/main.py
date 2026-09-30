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


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID") or f"req-{uuid.uuid4()}"
    request.state.correlation_id = corr_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = corr_id
    return response


@app.exception_handler(BhuVistaarException)
async def domain_exception_handler(request: Request, exc: BhuVistaarException):
    req_id = getattr(request.state, "correlation_id", f"req-{uuid.uuid4()}")
    logger.warning(f"Domain error [{exc.code}] on {request.method} {request.url.path}: {exc.message}")
    
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.code in ("VALIDATION_BLOCKER_EXISTS", "APPROVAL_BLOCKED", "VUID_COLLISION", "DUPLICATE_EVIDENCE", "EVIDENCE_CONFLICT", "STALE_EVIDENCE", "STALE_VALIDATION"):
        status_code = status.HTTP_409_CONFLICT
    elif exc.code in ("PARCEL_NOT_FOUND", "UNIT_NOT_FOUND", "EVIDENCE_NOT_FOUND", "REVISION_NOT_FOUND", "AI_CANDIDATE_NOT_FOUND"):
        status_code = status.HTTP_404_NOT_FOUND
    elif exc.code in ("EVIDENCE_INTEGRITY_MISMATCH", "INVALID_GEOMETRY", "INVALID_CRS", "AI_OUTPUT_VALIDATION_FAILED", "EVIDENCE_QUALITY_FAILED", "DATA_INTEGRITY_VIOLATION"):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif exc.code == "UNAUTHORIZED_ACTION":
        status_code = status.HTTP_403_FORBIDDEN
    elif exc.code == "AI_SERVICE_DISABLED":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif exc.code in ("EXPORT_FAILED", "IMPORT_FAILED"):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

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
    req_id = getattr(request.state, "correlation_id", f"req-{uuid.uuid4()}")
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


def check_subsystem_health() -> dict:
    from sqlalchemy import text
    from backend.db.session import SessionLocal

    db_status = "unavailable"
    postgis_status = "unavailable"
    migration_status = "unknown"
    
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1;"))
            db_status = "ok"
            
            res = db.execute(text("SELECT PostGIS_Version();")).fetchone()
            if res:
                postgis_status = f"ok (PostGIS {res[0]})"
                
            rev_res = db.execute(text("SELECT version_num FROM alembic_version;")).fetchone()
            if rev_res:
                migration_status = f"current ({rev_res[0]})"
    except Exception as e:
        logger.warning(f"Health check DB probe failure: {e}")

    ai_status = "available" if settings.AI_ASSISTANCE_ENABLED else "disabled"
    if settings.AI_MODE == "DETERMINISTIC":
        ai_status = "deterministic_fallback"
    elif settings.AI_MODE == "DISABLED" or not settings.AI_ASSISTANCE_ENABLED:
        ai_status = "disabled"

    is_ready = (db_status == "ok" and "ok" in postgis_status)

    return {
        "status": "ready" if is_ready else "degraded",
        "application": "ok",
        "database": db_status,
        "postgis": postgis_status,
        "migrations": migration_status,
        "ai": ai_status,
        "ai_mode": settings.AI_MODE,
        "authorization_mode": settings.AUTHORIZATION_MODE,
        "canonical_srid": settings.CANONICAL_STORAGE_SRID,
        "canonical_crs": settings.CANONICAL_STORAGE_CRS,
        "environment": settings.APP_ENV,
        "version": settings.VALIDATOR_VERSION,
        "ruleset_version": settings.RULESET_VERSION,
        "validator_version": settings.VALIDATOR_VERSION
    }


@app.get("/health", tags=["Health"])
def health_overview():
    return check_subsystem_health()


@app.get("/health/live", tags=["Health"])
def health_live():
    return {"status": "ALIVE", "version": "0.1.0"}


@app.get("/health/ready", tags=["Health"])
def health_ready():
    health = check_subsystem_health()
    if health["status"] != "ready":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health)
    return health


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

