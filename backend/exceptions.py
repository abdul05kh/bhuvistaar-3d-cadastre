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


class DuplicateEvidenceError(BhuVistaarException):
    def __init__(self, evidence_id: str, checksum: str, original_id: str):
        super().__init__(
            message=f"Duplicate evidence detected: Checksum '{checksum}' already registered as '{original_id}'.",
            code="DUPLICATE_EVIDENCE",
            details={"evidence_id": evidence_id, "checksum": checksum, "original_id": original_id}
        )
        self.evidence_id = evidence_id
        self.checksum = checksum
        self.original_id = original_id


class EvidenceConflictError(BhuVistaarException):
    def __init__(self, message: str, source_a: str, source_b: str, discrepancy: dict[str, Any]):
        super().__init__(
            message=message,
            code="EVIDENCE_CONFLICT",
            details={"source_a": source_a, "source_b": source_b, "discrepancy": discrepancy}
        )


class StaleEvidenceError(BhuVistaarException):
    def __init__(self, message: str, candidate_id: str, original_hash: str, current_hash: str):
        super().__init__(
            message=message,
            code="STALE_EVIDENCE",
            details={"candidate_id": candidate_id, "original_hash": original_hash, "current_hash": current_hash}
        )


class StaleValidationError(BhuVistaarException):
    def __init__(self, message: str, revision_id: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="STALE_VALIDATION",
            details={"revision_id": str(revision_id), **(details or {})}
        )


class EvidenceQualityError(BhuVistaarException):
    def __init__(self, message: str, issues: list[str]):
        super().__init__(
            message=message,
            code="EVIDENCE_QUALITY_FAILED",
            details={"issues": issues}
        )


class DataIntegrityError(BhuVistaarException):
    def __init__(self, message: str, issues: list[dict[str, Any]]):
        super().__init__(
            message=message,
            code="DATA_INTEGRITY_VIOLATION",
            details={"issues": issues}
        )


class InteroperabilityExportError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="EXPORT_FAILED", details=details)


class InteroperabilityImportError(BhuVistaarException):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="IMPORT_FAILED", details=details)


class UnauthorizedActionError(BhuVistaarException):
    def __init__(self, role: str, action: str):
        super().__init__(
            message=f"Role '{role}' is not authorized to perform action '{action}' under simulated governance rules.",
            code="UNAUTHORIZED_ACTION",
            details={"role": role, "action": action}
        )

