# Sujoy_Sarkar_AIML
# CS Revise — Stage 2, Track E: Auto-Marking

## Contents

| File | What it is |
|---|---|
| `Summary.docx` | 1-page submission summary (what was done, approach, assumptions) |
| `research_comparison.md` | Comparison of 3 auto-marking approaches for GCSE/11+ |
| `auto_marker.py` | The prototype: hybrid keyword + TF-IDF similarity marking engine |
| `sample_questions.json` | 2 mark schemes + 14 hand-written test answers (full/partial/wrong) |
| `run_tests.py` | Runs the prototype over all 14 test answers and scores its accuracy |
| `test_results.csv` | Raw per-answer output from the test run |
| `accuracy_report.md` | Honest accuracy numbers and analysis of where/why it fails |
| `design_note.md` | How this would plug into CS Revise's real marking flow |
| `risks_and_safeguards.md` | Where auto-marking can go wrong, and the human-review safeguards proposed |

## Quick start

```bash
pip install scikit-learn
python3 auto_marker.py      # demo: marks one sample answer, prints the breakdown
python3 run_tests.py        # runs the full 14-answer accuracy test
```

No API key or internet connection needed — the prototype is fully
self-contained (see `research_comparison.md` for why this approach was
chosen over an LLM-only or keyword-only approach, and `design_note.md` for
how an LLM would be layered in for an escalation path).

## Headline result

10/14 (71%) exact mark match, 100% within 1 mark, across a hand-written
test set of full/partial/wrong answers to 2 GCSE-style questions. Full
breakdown and honest discussion of the failure modes in `accuracy_report.md`.
