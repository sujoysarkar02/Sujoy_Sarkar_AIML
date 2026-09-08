# Accuracy Report

Test set: 14 answers across 2 GCSE/11+ style short-answer questions
(5 full-mark, 5 partial-mark, 4 wrong answers — see `sample_questions.json`).
Full per-answer results: `test_results.csv`. Reproduce with `python3 run_tests.py`.

## Headline numbers

| Metric | Result |
|---|---|
| Exact mark match | 10/14 (71%) |
| Within 1 mark | 14/14 (100%) |
| Mean absolute error | 0.29 marks |
| Flagged for human review | 2/14 |

## Accuracy by answer type

| Category | Exact match |
|---|---|
| Full-mark answers | 5/5 (100%) |
| Partial-mark answers | 2/5 (40%) |
| Wrong answers | 3/4 (75%) |

## What this actually shows

**Strength — full-mark answers are reliable.** Every full-mark answer was
marked correctly, even when phrased quite differently from the exemplar
(e.g. "sugar" instead of "glucose" was still picked up by the TF-IDF
similarity check). This is the highest-stakes failure mode in practice —
a system that under-marks a correct answer erodes student trust fastest —
so it's the right place for this prototype to be strongest.

**Weakness — partial-mark answers are the hardest.** This is where the
model's real limitation shows: 3 of 4 mismatches happened here, and every
one of them was an **over-award** (predicted mark higher than the true
mark), not an under-award. The keyword/semantic checks look at each mark
point in isolation, so an answer that mentions two relevant *words* without
actually making the *causal link* the mark scheme wants (e.g. saying
"friction" and "steady speed" separately, without explaining *why* less
force is needed once moving) still gets credit it shouldn't. A human marker
reads for the connecting logic; this prototype currently doesn't.

**Wrong answers are mostly caught, with one leak.** One wrong answer
("plants get bigger because they drink water and grow towards the sun")
was given 1 mark because it happens to use the word "water" in a context
that superficially resembles the water/CO2 mark point. This is the same
root cause as above — the system rewards keyword/topic overlap, not
correct reasoning.

## Honest limitations

1. **No real language understanding.** TF-IDF is a bag-of-words method — it
   has no concept of negation, causality, or word order. "Friction slows
   the car down" and "the car has no friction" would score similarly, since
   both discuss friction.
2. **Mark points are scored independently.** The engine can't currently
   check that a student linked two ideas correctly, which is exactly where
   GCSE mark schemes often award marks for "explanation" rather than
   "statement of fact."
3. **Small, hand-built test set.** 14 answers across 2 questions is enough
   to sanity-check the approach and surface a real failure mode, but far
   too small to certify accuracy at the level needed for unsupervised
   grading.
4. **Synonym list is manually curated.** It will miss valid phrasing outside
   the list (e.g. a student writing "makes food using sunlight" without the
   word "glucose" anywhere).

These limitations are exactly why the design note proposes this system as a
**first-pass marker with mandatory human review of borderline and
partial-mark cases**, not a fully autonomous grader — see
`risks_and_safeguards.md`.
