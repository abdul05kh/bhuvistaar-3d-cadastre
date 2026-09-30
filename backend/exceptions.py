from typing import Any, Optional


class BhuVistaarException(Exception):
    def __init__(self, message: str, code: str = "BHUVISTAAR_ERROR", details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class InvalidGeometryError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="INVALID_GEOMETRY", details=details)


class InvalidCRSError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="INVALID_CRS", details=details)


class VUIDCollisionError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="VUID_COLLISION", details=details)


class ValidationBlockerError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="VALIDATION_BLOCKER_EXISTS", details=details)


class ParcelNotFoundError(BhuVistaarException):
    def __init__(self, ulpin: str):
        super().__init__(message=f"Parent parcel with ULPIN '{ulpin}' not found.", code="PARCEL_NOT_FOUND", details={"ulpin": ulpin})


class UnitNotFoundError(BhuVistaarException):
    def __init__(self, vuid: str):
        super().__init__(message=f"Spatial unit with VUID '{vuid}' not found.", code="UNIT_NOT_FOUND", details={"vuid": vuid})


class EvidenceNotFoundError(BhuVistaarException):
    def __init__(self, evidence_id: str):
        super().__init__(message=f"Evidence source with ID '{evidence_id}' not found.", code="EVIDENCE_NOT_FOUND", details={"evidence_id": evidence_id})


class RevisionNotFoundError(BhuVistaarException):
    def __init__(self, revision_id: str):
        super().__init__(message=f"Spatial unit revision '{revision_id}' not found.", code="REVISION_NOT_FOUND", details={"revision_id": str(revision_id)})


class ApprovalBlockedError(BhuVistaarException):
    def __init__(self, reason: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=f"Approval blocked: {reason}", code="APPROVAL_BLOCKED", details=details)


class EvidenceIntegrityError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="EVIDENCE_INTEGRITY_MISMATCH", details=details)


class AICandidateNotFoundError(BhuVistaarException):
    def __init__(self, candidate_id: str):
        super().__init__(message=f"AI Candidate with ID '{candidate_id}' not found.", code="AI_CANDIDATE_NOT_FOUND", details={"candidate_id": candidate_id})


class AIOutputValidationError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="AI_OUTPUT_VALIDATION_FAILED", details=details)


class AIInferenceError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="AI_INFERENCE_ERROR", details=details)


class AIServiceDisabledError(BhuVistaarException):
    def __init__(self):
        super().__init__(message="AI assistance service is disabled by configuration (AI_ASSISTANCE_ENABLED=false). Core deterministic engine remains available.", code="AI_SERVICE_DISABLED")

