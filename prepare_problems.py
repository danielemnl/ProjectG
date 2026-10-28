"""Run in the INTERNET notebook. pip install evalplus. Writes problems.jsonl (inputs stored as repr strings)."""
import ast, json
from evalplus.data import get_mbpp_plus
N_VISIBLE = 3  # ASSUMPTION: first 3 base inputs = original MBPP tests. Check one problem by eye (see README).
rows = []
for tid, p in get_mbpp_plus().items():
    ins = list(p["base_input"]) + list(p["plus_input"])
    try:
        reps = [repr(x) for x in ins]
        assert all(ast.literal_eval(r) == x for r, x in zip(reps, ins))
    except Exception:
        continue  # skip inputs that don't round-trip through repr
    rows.append({"task_id": tid, "prompt": p["prompt"], "entry_point": p["entry_point"],
                 "canonical_solution": p["canonical_solution"], "inputs": reps,
                 "n_visible": N_VISIBLE, "atol": p.get("atol", 0)})
with open("problems.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print(len(rows), "problems")
