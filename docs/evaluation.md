# Evaluation method

The question: **does the rule-based matcher find the right skills and the right required/preferred split?**

## Data
`backend/evaluation/dataset.json`:
- 15 short resumes with a gold list of skills (including hard cases: ambiguous words, abbreviations, `Java` vs `JavaScript`, `C++`/`C#`).
- 6 job descriptions with gold `required` and `preferred` skill lists (headings, bullets, "a plus", "desirable", all-caps headings).

Labelling rule: a skill is gold only if the text **names it or one of its aliases** in `skills.json`. Implied skills are not labelled. The data is synthetic and was also used while building the matcher, so treat the scores as an upper bound.

## Metrics
Micro-averaged over all items:
- precision = TP / (TP + FP), recall = TP / (TP + FN), F1 = harmonic mean
- for job descriptions, the same numbers separately for `required` and `preferred`, plus the count of JDs classified exactly right.

## Run
```bash
cd backend
python -m evaluation.evaluate          # readable report with every error
python -m evaluation.evaluate --json   # for scripts
```

## Results (last run)

| Task | Precision | Recall | F1 |
|---|---|---|---|
| Skill extraction (81 TP, 2 FP, 0 FN) | 0.976 | 1.000 | 0.988 |
| JD "required" | 1.000 | 1.000 | 1.000 |
| JD "preferred" | 1.000 | 1.000 | 1.000 |

JDs classified exactly right: 6/6.

## What the evaluation found (and what changed)
First run: F1 0.970 for extraction, 4/6 JDs exactly right. Errors led to three changes, each with a regression test:
1. An all-caps skill line such as `AWS` was read as a section heading, resetting "nice to have" to "required".
2. One "desirable" in a sentence demoted every skill on that line; markers now apply per sentence.
3. `ML` was missed; added as a case-sensitive alias (lowercase `ml` is ambiguous).

Two gold labels were also corrected where the label asked for a skill the text never named.

Remaining error: `Express` and `React` match the lowercase verbs in "react quickly to incidents and express complex ideas".

## How to make it more convincing
- Add 50+ anonymised real resumes and job posts, labelled by someone who did not write the matcher; keep a held-out test split.
- Compare against an embedding or NER baseline on the same split and report the difference.
- Add a human-rated check of whether the final score ranks resumes in a sensible order for one job.
