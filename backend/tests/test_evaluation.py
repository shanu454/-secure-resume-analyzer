import json

from evaluation.evaluate import DATASET, evaluate


def test_extraction_quality_does_not_regress():
    result = evaluate(json.loads(DATASET.read_text(encoding="utf-8")))
    assert result["extraction"]["f1"] >= 0.9
    assert result["extraction"]["recall"] >= 0.9
    assert result["classification"]["required"]["f1"] >= 0.9
