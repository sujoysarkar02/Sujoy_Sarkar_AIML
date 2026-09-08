# Design Note: Plugging This Into CS Revise's Marking Flow

This is a plan, not a built integration (as the brief allows) — but it's
scoped to be genuinely buildable, not aspirational.

## Proposed flow

![Alt text describing the diagram](path/to/pipeline_flow.png)

## Why hybrid-first, LLM-second

- Most answers to well-defined short questions are either clearly full-mark
  or clearly wrong — the free, instant hybrid engine handles these well (see
  `accuracy_report.md`: 100% exact match on full-mark and strong on wrong
  answers). There's no need to pay for an LLM call on every single answer.
- The hybrid engine's own `needs_human_review` flag becomes the trigger for
  when to spend the extra cost/latency of an LLM call — the system uses its
  own uncertainty to decide when to escalate, rather than escalating
  everything or nothing.
- This keeps day-to-day marking costs low and fast while still getting
  LLM-quality judgement exactly where the cheap engine is known to be weak
  (partial credit, causal reasoning — see `research_comparison.md`).

## Practical components needed to actually build this

1. **Mark scheme authoring tool** — a simple form for CS Revise staff to
   enter mark points, keywords, and an exemplar phrase per question (the
   JSON structure in `sample_questions.json` maps directly to form fields).
2. **Cloud function** (e.g. Google Cloud Function / AWS Lambda) wrapping
   `AutoMarker.mark()`, callable from the existing student-facing app.
3. **LLM marking endpoint** for the escalation path — a second, smaller
   cloud function that only fires when the hybrid engine flags a case.
4. **A review queue** (even a simple spreadsheet or admin dashboard to start)
   where flagged/escalated answers land for a teacher to confirm, edit, or
   override the mark. Every override should be logged and periodically
   reviewed to retune the keyword lists and similarity threshold.
5. **Versioned mark schemes** — if a mark scheme is edited after some
   students have already been marked, keep the old version so past results
   stay explainable.

## Rollout suggestion

Start on a single low-stakes topic (e.g. practice questions rather than
mock exam scores that go on a report), running the hybrid engine
in "shadow mode" next to existing human marking for a few weeks to compare
before it's trusted to mark unsupervised — see `risks_and_safeguards.md`.
