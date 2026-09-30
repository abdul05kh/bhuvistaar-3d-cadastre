import hashlib
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.provenance import ProvenanceRecord
from backend.domain.revision import SpatialUnitRevision
from backend.domain.evidence import EvidenceSource
from backend.repository.provenance_repository import ProvenanceRepository
from backend.repository.evidence_repository import EvidenceRepository
from backend.exceptions import EvidenceIntegrityError, EvidenceNotFoundError


class ProvenanceService:
    def __init__(self, db: Session, evidence_repo: Optional[EvidenceRepository] = None):
        self.db = db
        self.prov_repo = ProvenanceRepository(db)
        self.ev_repo = evidence_repo or EvidenceRepository(db)


    def create_provenance(
        self,
        revision: SpatialUnitRevision,
        evidence_ids: list[str],
        generation_method: str = "PRISMATIC_EXTRUSION",
        generation_method_version: str = "1.0.0",
        vuid_algorithm_version: str = "v1",
        predecessor_vuid: Optional[str] = None
    ) -> ProvenanceRecord:
        # Build evidence summaries
        evidence_records = []
        all_verified = True
        
        for eid in evidence_ids:
            ev = self.ev_repo.find_by_id(eid)
            if not ev:
                all_verified = False
                continue
            
            # Verify checksum format (SHA-256 is 64 hex chars)
            checksum_valid = bool(len(ev.checksum) == 64 and all(c in "0123456789abcdefABCDEF" for c in ev.checksum))
            if not checksum_valid:
                all_verified = False

            evidence_records.append({
                "id": ev.id,
                "evidence_type": ev.evidence_type.value,
                "provider": ev.provider,
                "source_reference": ev.source_reference,
                "checksum": ev.checksum,
                "checksum_algorithm": "SHA-256",
                "checksum_valid": checksum_valid
            })

        record = ProvenanceRecord(
            revision_id=revision.id,
            parent_ulpin=revision.parent_ulpin,
            generation_method=generation_method,
            generation_method_version=generation_method_version,
            vuid_algorithm_version=vuid_algorithm_version,
            predecessor_vuid=predecessor_vuid,
            evidence_sources=evidence_records,
            is_verified=all_verified and len(evidence_records) > 0
        )
        return self.prov_repo.save(record)

    def verify_evidence_content(self, evidence_id: str, raw_content: bytes) -> bool:
        ev = self.ev_repo.find_by_id(evidence_id)
        if not ev:
            raise EvidenceNotFoundError(evidence_id)
        
        calculated_hash = hashlib.sha256(raw_content).hexdigest()
        if calculated_hash.lower() != ev.checksum.lower():
            raise EvidenceIntegrityError(
                f"Evidence checksum mismatch for '{evidence_id}': calculated {calculated_hash} != registered {ev.checksum}",
                details={"evidence_id": evidence_id, "calculated": calculated_hash, "registered": ev.checksum}
            )
        return True

    def get_provenance_for_revision(self, revision_id: UUID) -> Optional[ProvenanceRecord]:
        return self.prov_repo.find_by_revision_id(revision_id)
