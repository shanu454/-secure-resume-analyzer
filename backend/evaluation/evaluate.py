"""Evaluate skill extraction and job-description classification.

Usage (from the backend/ folder):
    python -m evaluation.evaluate            # human-readable report
    python -m evaluation.evaluate --json     # machine-readable metrics

Metrics
  * Skill extraction: micro-averaged precision, recall and F1 over all resumes.
    TP = skill extracted and in gold, FP = extracted but not in gold, FN = in gold but missed.
  * JD classification: the same metrics, computed separately for the
    'required' and 'preferred' sets, plus the number of JDs classified exactly right.
"""

import argparse
import json
from pathlib import Path

from app.services.jd import classify_skills
from app.services.skills import extract_skills

DATASET = Path(__file__).with_name("dataset.json")


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3)}


def evaluate(dataset: dict) -> dict:
    tp = fp = fn = 0
    errors = []
    for item in dataset["resumes"]:
        predicted, gold = set(extract_skills(item["text"])), set(item["skills"])
        tp += len(predicted & gold)
        fp += len(predicted - gold)
        fn += len(gold - predicted)
        if predicted != gold:
            errors.append(
                {
                    "id": item["id"],
                    "false_positives": sorted(predicted - gold),
                    "false_negatives": sorted(gold - predicted),
                }
            )
    extraction = {**prf(tp, fp, fn), "tp": tp, "fp": fp, "fn": fn, "resumes": len(dataset["resumes"])}

    jd = {}
    exact = 0
    jd_errors = []
    for label in ("required", "preferred"):
        jd[label] = {"tp": 0, "fp": 0, "fn": 0}
    for item in dataset["job_descriptions"]:
        required, preferred = classify_skills(item["text"])
        got = {"required": set(required), "preferred": set(preferred)}
        gold = {"required": set(item["required"]), "preferred": set(item["preferred"])}
        for label in ("required", "preferred"):
            jd[label]["tp"] += len(got[label] & gold[label])
            jd[label]["fp"] += len(got[label] - gold[label])
            jd[label]["fn"] += len(gold[label] - got[label])
        if got == gold:
            exact += 1
        else:
            jd_errors.append(
                {
                    "id": item["id"],
                    "got": {k: sorted(v) for k, v in got.items()},
                    "gold": {k: sorted(v) for k, v in gold.items()},
                }
            )
    classification = {label: {**prf(c["tp"], c["fp"], c["fn"]), **c} for label, c in jd.items()}
    classification["exact_matches"] = f"{exact}/{len(dataset['job_descriptions'])}"
    return {
        "extraction": extraction,
        "classification": classification,
        "extraction_errors": errors,
        "classification_errors": jd_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(json.loads(DATASET.read_text(encoding="utf-8")))
    if args.json:
        print(json.dumps(result, indent=2))
        return
    e = result["extraction"]
    print(f"Skill extraction over {e['resumes']} resumes")
    print(f"  precision {e['precision']:.3f}  recall {e['recall']:.3f}  F1 {e['f1']:.3f}")
    print(f"  true positives {e['tp']}, false positives {e['fp']}, false negatives {e['fn']}")
    for err in result["extraction_errors"]:
        print(f"  {err['id']}: false positives {err['false_positives']}")
        print(f"  {err['id']}: false negatives {err['false_negatives']}")
    c = result["classification"]
    print("\nJob-description classification")
    for label in ("required", "preferred"):
        m = c[label]
        print(f"  {label:9s} precision {m['precision']:.3f}  recall {m['recall']:.3f}  F1 {m['f1']:.3f}")
    print(f"  JDs classified exactly right: {c['exact_matches']}")
    for err in result["classification_errors"]:
        print(f"  {err['id']}: got {err['got']}  gold {err['gold']}")


if __name__ == "__main__":
    main()
