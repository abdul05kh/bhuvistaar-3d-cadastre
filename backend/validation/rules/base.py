from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D


class BaseValidationRule(ABC):
    rule_code: str
    rule_family: str
    description: str
    rule_version: str = "1.0.0"
    ruleset_version: str = "1.0.0"

    @abstractmethod
    def evaluate(
        self,
        run_id: UUID,
        parcel: ParentParcel,
        units: Sequence[SpatialUnit3D]
    ) -> list[ValidationIssue]:
        """
        Evaluates the validation rule against the parent parcel and its child spatial units.
        Returns a list of structured ValidationIssue records.
        """
        pass
