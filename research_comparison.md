# Comparing Auto-Marking Approaches for GCSE / 11+ Short Answers

Three approaches were compared before choosing one to prototype.

## 1. Keyword / rubric matching

Checks whether specific words or phrases from the mark scheme appear in the
student's answer.

**Pros**
- Fully transparent — a teacher can see exactly why a mark was or wasn't
  given, which matters for a platform parents and students need to trust.
- Cheap, fast, works fully offline, trivial to audit or hand-correct.
- Matches how many real GCSE mark schemes are already written (lists of
  acceptable points/keywords).

**Cons**
- Brittle to rephrasing — a correct answer using an unlisted synonym scores
  zero unless someone maintains the keyword list.
- Can't tell a genuine explanation from keyword-stuffing.

**Fit for GCSE/11+:** Good baseline, especially for well-defined science/
maths mark points, but too rigid alone for answers with varied phrasing —
which is common at 11+ where children haven't yet learned "exam language."

## 2. Embedding / similarity-based matching

Compares the *meaning* of the student's answer to a model answer or
exemplar phrase, using a vector representation of the text (this ranges
from simple TF-IDF vectors up to modern transformer sentence embeddings).

**Pros**
- Tolerant of paraphrasing and vocabulary a keyword list didn't anticipate.
- Still relatively cheap and fast; can run without an internet connection
  if a local model is used (or free/near-free if using a hosted embeddings
  API).
- Middle ground between rigid keyword matching and a full LLM call.

**Cons**
- A similarity score is not the same as correctness — it can be fooled by
  answers that are topically close but factually wrong or missing the
  causal reasoning a mark point wants (this shows up directly in
  `accuracy_report.md`).
- Harder to explain to a teacher than "the answer contained the word X."

**Fit for GCSE/11+:** Strong complement to keyword matching — this is why
the prototype uses both together (see below) — but risky as the sole
method for marks that require an explanation, not just a topic mention.

## 3. LLM-based grading

Sends the question, mark scheme, and student answer to a large language
model and asks it to award marks and give feedback directly.

**Pros**
- Best at judging genuine understanding, reasoning chains, and partial
  credit — the exact weakness identified in the prototype's own test
  results (see `accuracy_report.md`, "partial-mark answers").
- Can generate natural, personalised feedback rather than a templated
  sentence.
- Adapts to new question types without hand-writing a new mark scheme
  structure for each one.

**Cons**
- Costs money and time per answer (an API call), and requires an internet
  connection and a paid API key — a real constraint for a schools platform
  marking answers at scale.
- Less transparent/deterministic: the same answer can occasionally get a
  slightly different mark or explanation on a re-run, which is a hard sell
  for something as high-stakes as a mark.
- Needs careful prompt design and spot-checking to avoid the model being
  too lenient (or too harsh) compared to the real mark scheme, and needs
  ongoing monitoring as models change.

**Fit for GCSE/11+:** The most accurate on reasoning-heavy questions, but
the cost, latency, and "black box" concerns make it best used selectively
rather than for every single answer submitted — see `design_note.md`.

## Why the prototype uses a hybrid of (1) and (2)

Given the 72-hour window, a hybrid of **keyword matching + TF-IDF
similarity** was the most honest choice to prototype and test properly:
it is free, runs instantly, is fully explainable to a teacher, and — as
the test results show — it is genuinely strong on clear-cut answers while
being honest about exactly where it struggles (partial credit, causal
reasoning). `design_note.md` proposes layering an LLM-based check on top of
this for the cases the hybrid engine itself flags as uncertain, rather than
using an LLM for every answer.
