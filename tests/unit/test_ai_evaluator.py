"""Unit test for AI Evaluation Harness."""
from backend.ai.evaluators.evaluator import AIEvaluationHarness


def test_ai_benchmark_evaluation():
    report = AIEvaluationHarness.run_benchmark_evaluation()
    assert report["total_scenarios_evaluated"] >= 7
    metrics = report["metrics"]
    assert "candidate_detection" in metrics
    assert "anomaly_detection" in metrics
    assert "baseline_comparison" in metrics

    cand_det = metrics["candidate_detection"]
    assert cand_det["precision"] > 0.80
    assert cand_det["recall"] > 0.80
    assert cand_det["f1_score"] > 0.80

    anom_det = metrics["anomaly_detection"]
    assert anom_det["true_positives"] >= 4

    baseline = metrics["baseline_comparison"]
    assert baseline["model_f1"] > baseline["baseline_f1"]
    assert "SYNTHETIC_CADASTRE_V1" in report["benchmark_dataset"]
