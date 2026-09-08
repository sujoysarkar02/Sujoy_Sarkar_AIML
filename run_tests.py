import csv
import json
from statistics import mean
from auto_marker import AutoMarker, MarkScheme

def main():
    with open("sample_questions.json") as f:
        data = json.load(f)

    marker = AutoMarker()
    rows = []

    for q in data["questions"]:
        scheme = MarkScheme.from_dict(q)
        for ans in q["test_answers"]:
            result = marker.mark(ans["text"], scheme)
            predicted = result.total_marks
            true_mark = ans["true_mark"]
            error = predicted - true_mark
            rows.append({
                "question_id": q["id"],
                "category": ans["category"],
                "answer": ans["text"],
                "true_mark": true_mark,
                "predicted_mark": predicted,
                "max_marks": scheme.max_marks,
                "error": error,
                "exact_match": error == 0,
                "within_1": abs(error) <= 1,
                "flagged_for_review": result.needs_human_review,
            })

    #write CSV
    with open("test_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    #summary stats
    n = len(rows)
    exact = sum(r["exact_match"] for r in rows)
    within1 = sum(r["within_1"] for r in rows)
    mae = mean(abs(r["error"]) for r in rows)
    flagged = sum(r["flagged_for_review"] for r in rows)

    by_category = {}
    for r in rows:
        by_category.setdefault(r["category"], []).append(r["exact_match"])

    print(f"Total answers tested: {n}")
    print(f"Exact mark match:     {exact}/{n}  ({exact/n:.0%})")
    print(f"Within 1 mark:        {within1}/{n}  ({within1/n:.0%})")
    print(f"Mean absolute error:  {mae:.2f} marks")
    print(f"Flagged for human review: {flagged}/{n}")
    print()
    print("Accuracy by answer category:")
    for cat, matches in by_category.items():
        print(f"  {cat:8s}: {sum(matches)}/{len(matches)} exact ({sum(matches)/len(matches):.0%})")

    #print the mismatches so limitations can be reported honestly
    print()
    print("Mismatches (predicted != true):")
    for r in rows:
        if not r["exact_match"]:
            print(f"  [{r['question_id']}] true={r['true_mark']} pred={r['predicted_mark']} "
                  f"({r['category']}): \"{r['answer'][:70]}...\"" if len(r['answer']) > 70
                  else f"  [{r['question_id']}] true={r['true_mark']} pred={r['predicted_mark']} "
                       f"({r['category']}): \"{r['answer']}\"")


if __name__ == "__main__":
    main()
