"""
auto_marker.py
--------------
A hybrid auto-marking engine for short written answers (GCSE / 11+ style).

Approach: "Rubric-Anchored Hybrid Scoring"
  1. Keyword / concept matching  -> checks whether the specific idea a mark
     point is looking for is present, using a small synonym list so that
     answers don't need to use the exact wording of the mark scheme.
  2. TF-IDF cosine similarity    -> a lightweight semantic check between the
     student's answer and a short exemplar phrase for each mark point, to
     catch correct ideas phrased in a way the keyword list didn't predict.
  3. A mark point is awarded if EITHER signal clears its threshold, and the
     "confidence" of that decision is recorded. Low-confidence / borderline
     decisions are flagged for human review rather than silently marked.

This intentionally avoids calling an external LLM API so it runs fully
offline and free of cost -- see research_comparison.md for why, and
design_note.md for how this would be swapped for an LLM-based grader in a
production CS Revise integration.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Text normalisation helpers
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-z0-9']+")


def normalise(text: str) -> str:
    return text.lower().strip()


def tokenise(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


# A tiny hand-built synonym map so keyword matching survives common
# rephrasings seen in GCSE/11+ answers. In production this would be
# expanded (or replaced by embeddings) -- see research_comparison.md.
SYNONYMS = {
    "increase": {"increase", "increases", "increasing", "rise", "rises", "grow", "grows", "higher"},
    "decrease": {"decrease", "decreases", "decreasing", "fall", "falls", "drop", "drops", "lower", "reduce", "reduces"},
    "photosynthesis": {"photosynthesis", "photosynthesise", "photosynthesising"},
    "carbon dioxide": {"carbon dioxide", "co2"},
    "glucose": {"glucose", "sugar"},
    "chlorophyll": {"chlorophyll", "chloroplast", "chloroplasts"},
    "force": {"force", "forces"},
    "friction": {"friction", "frictional"},
    "evaporate": {"evaporate", "evaporates", "evaporation", "evaporating"},
    "condense": {"condense", "condenses", "condensation", "condensing"},
}


def expand_keyword(keyword: str) -> set:
    key = keyword.lower().strip()
    return SYNONYMS.get(key, {key})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MarkPoint:
    id: str
    description: str          # what the marker is looking for (human readable)
    keywords: List[str]       # any-of these (each expanded via SYNONYMS) counts as a keyword hit
    exemplar: str              # a short model phrase used for the semantic similarity check
    marks: int = 1


@dataclass
class MarkScheme:
    question: str
    max_marks: int
    points: List[MarkPoint]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "MarkScheme":
        points = [MarkPoint(**p) for p in d["points"]]
        return MarkScheme(question=d["question"], max_marks=d["max_marks"], points=points)


@dataclass
class PointResult:
    id: str
    description: str
    awarded: bool
    marks: int
    max_marks: int
    method: str            # "keyword", "semantic", "both", or "none"
    confidence: float      # 0-1, how sure the engine is
    flagged: bool          # True if this decision should go to human review


@dataclass
class MarkingResult:
    total_marks: int
    max_marks: int
    point_results: List[PointResult]
    feedback: str
    needs_human_review: bool


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class AutoMarker:
    """
    Usage:
        marker = AutoMarker()
        result = marker.mark(student_answer, mark_scheme)
    """

    def __init__(self, semantic_threshold: float = 0.35, review_band: float = 0.15):
        # semantic_threshold: min cosine similarity to count as a semantic hit
        # review_band: how close to the threshold counts as "borderline" -> flag for a human
        self.semantic_threshold = semantic_threshold
        self.review_band = review_band

    # -- keyword pass ------------------------------------------------------
    def _keyword_hit(self, answer_tokens: List[str], answer_text: str, keywords: List[str]) -> bool:
        for kw in keywords:
            variants = expand_keyword(kw)
            for v in variants:
                if " " in v:  # multi-word phrase -> substring check
                    if v in answer_text:
                        return True
                elif v in answer_tokens:
                    return True
        return False

    # -- semantic pass -------------------------------------------------------
    def _semantic_score(self, answer_text: str, exemplar: str) -> float:
        if not answer_text.strip():
            return 0.0
        vec = TfidfVectorizer().fit([answer_text, exemplar])
        matrix = vec.transform([answer_text, exemplar])
        sim = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(sim)

    def mark(self, student_answer: str, mark_scheme: MarkScheme) -> MarkingResult:
        answer_text = normalise(student_answer)
        answer_tokens = tokenise(student_answer)

        point_results: List[PointResult] = []
        total = 0
        any_flagged = False

        for point in mark_scheme.points:
            kw_hit = self._keyword_hit(answer_tokens, answer_text, point.keywords)
            sim = self._semantic_score(answer_text, point.exemplar)
            sem_hit = sim >= self.semantic_threshold

            if kw_hit and sem_hit:
                method, confidence = "both", min(1.0, 0.7 + sim * 0.3)
            elif kw_hit:
                method, confidence = "keyword", 0.75
            elif sem_hit:
                method, confidence = "semantic", 0.5 + (sim - self.semantic_threshold)
            else:
                method, confidence = "none", 1.0 - sim  # confident it's absent if sim is low

            awarded = kw_hit or sem_hit
            # Flag borderline semantic-only calls, or near-miss non-awards, for a human to check
            near_threshold = abs(sim - self.semantic_threshold) <= self.review_band
            flagged = (method == "semantic" and near_threshold) or (method == "none" and near_threshold)
            if flagged:
                any_flagged = True

            marks = point.marks if awarded else 0
            total += marks

            point_results.append(PointResult(
                id=point.id, description=point.description, awarded=awarded,
                marks=marks, max_marks=point.marks, method=method,
                confidence=round(confidence, 2), flagged=flagged,
            ))

        feedback = self._build_feedback(point_results, total, mark_scheme.max_marks)

        return MarkingResult(
            total_marks=total,
            max_marks=mark_scheme.max_marks,
            point_results=point_results,
            feedback=feedback,
            needs_human_review=any_flagged,
        )

    @staticmethod
    def _build_feedback(point_results: List[PointResult], total: int, max_marks: int) -> str:
        hit = [p for p in point_results if p.awarded]
        missed = [p for p in point_results if not p.awarded]
        lines = [f"Score: {total}/{max_marks}."]
        if hit:
            lines.append("Credit given for: " + "; ".join(p.description for p in hit) + ".")
        if missed:
            lines.append("Missing / not credited: " + "; ".join(p.description for p in missed) + ".")
        flagged = [p for p in point_results if p.flagged]
        if flagged:
            lines.append(f"Note: {len(flagged)} mark point(s) were borderline and flagged for teacher review.")
        return " ".join(lines)


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with open("sample_questions.json") as f:
        data = json.load(f)

    q = data["questions"][0]
    scheme = MarkScheme.from_dict(q)
    marker = AutoMarker()

    demo_answer = q["demo_answers"][0]["text"]
    result = marker.mark(demo_answer, scheme)

    print("QUESTION:", scheme.question)
    print("ANSWER:", demo_answer)
    print()
    print(result.feedback)
    print("Needs human review:", result.needs_human_review)
    for p in result.point_results:
        print(f"  [{p.marks}/{p.max_marks}] {p.description} (method={p.method}, conf={p.confidence})")
