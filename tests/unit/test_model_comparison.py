"""Unit tests for Model Comparison Service (Slice 4)."""
from unittest.mock import MagicMock
from backend.ai.services.model_comparison_service import ModelComparisonService


def test_model_comparison_honest_reporting():
    """Verifies empirical delta reporting without marketing claims."""
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [],  # candidates
        [],  # anomalies
        []   # disagreements
    ]

    service = ModelComparisonService(mock_db)
    res = service.compare_models(
        model_a_id="prismatic-candidate-001",
        model_b_id="cadastral-heuristic-baseline-001",
        parent_ulpin="12345678901234"
    )

    assert res.parent_ulpin == "12345678901234"
    assert len(res.metrics) >= 4
    for m in res.metrics:
        assert "Difference observed" in m.observation or "Model A links" in m.observation
    assert "No claim of statistical superiority" in res.limitations_disclaimer
