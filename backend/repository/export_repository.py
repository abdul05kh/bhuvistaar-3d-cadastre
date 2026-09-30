from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.db.models import ExportRecordModel
from backend.domain.export import ExportRecord


class ExportRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, record: ExportRecord) -> ExportRecord:
        model = ExportRecordModel(
            id=record.id,
            revision_id=record.revision_id,
            export_format=record.export_format,
            checksum=record.checksum,
            exported_by=record.exported_by,
            content_json=record.content,
            created_at=record.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_latest_for_revision(self, revision_id: UUID) -> Optional[ExportRecord]:
        model = (
            self.db.query(ExportRecordModel)
            .filter_by(revision_id=revision_id)
            .order_by(ExportRecordModel.created_at.desc())
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: ExportRecordModel) -> ExportRecord:
        return ExportRecord(
            id=model.id,
            revision_id=model.revision_id,
            export_format=model.export_format,
            checksum=model.checksum,
            exported_by=model.exported_by,
            content=model.content_json,
            created_at=model.created_at
        )
