# Risks and Human-Review Safeguards

## Where auto-marking is most likely to get it wrong

1. **Over-crediting partial/topical answers.** The prototype's own test
   results show its main failure mode is awarding marks for an answer that
   mentions the right topic words without making the actual explanation or
   causal link the mark scheme wants. This is the single biggest risk for
   any keyword/similarity-based approach.
2. **Penalising unusual but valid phrasing.** A student who reasons
   correctly but in an unexpected way (different vocabulary, different
   structure) may be under-marked if their phrasing wasn't anticipated —
   this is a fairness risk that would fall disproportionately on students
   who don't already know "exam language," which is exactly the group a
   tutoring platform is meant to help.
3. **Mark scheme quality determines everything.** If the keywords/exemplars
   for a question are poorly written, every answer to that question inherits
   the mistake, silently and at scale — unlike a single human marker's
   error, which is contained to the papers they personally marked.
4. **Drift over time.** If questions, curricula, or common student phrasing
   change and the mark scheme/keyword list isn't updated, accuracy will
   quietly degrade without an obvious trigger.
5. **Overconfidence in the number.** A mark presented as a plain number
   (e.g. "2/3") can look more authoritative than it is, especially to a
   parent, if there's no visible indication of how confident the system
   actually was.
6. **LLM-specific risks (for the escalation path).** Inconsistent marks
   between near-identical answers on re-runs, susceptibility to answers
   that "sound" confident/academic without being correct, and the cost of
   monitoring an external model that can change behaviour when the
   provider updates it.

## Safeguards this design proposes

- **Human review queue is mandatory, not optional**, for: anything the
  engine itself flags as borderline (`needs_human_review`), all
  first-time uses of a new mark scheme, and a random sample of "confident"
  results, so silent drift can be caught.
- **Never present a mark as final without a visible confidence/flag
  signal** the student or parent can see (e.g. "provisional mark, being
  checked") when the system was uncertain — matching the
  `confidence`/`flagged` fields already produced by `auto_marker.py`.
- **Right to appeal / re-mark by a human** should always be available and
  easy to find, not buried in settings.
- **Every human override of an auto-mark is logged** and reviewed
  periodically in batches, specifically to catch systematic over- or
  under-marking on particular question types — this is the direct fix for
  the "over-credits partial answers" failure mode identified above.
- **Shadow-mode rollout**: run the system alongside existing human marking
  for a trial period on any new question type before it marks unsupervised,
  as suggested in `design_note.md`.
- **Mark scheme changes are versioned**, so a later fix to a bad keyword
  list doesn't retroactively make past results unexplainable.
- **Escalate rather than guess**: when the fast hybrid engine is unsure, the
  design routes to a stronger (LLM) check or a human, rather than the
  system silently picking the more generous or more punitive interpretation.

The honest goal of this design is not a fully autonomous marker on day one
— it's a system that is fast and free for the clear-cut majority of
answers, transparent about when it's unsure, and structured so a human is
always the backstop for the cases most likely to be wrong.
