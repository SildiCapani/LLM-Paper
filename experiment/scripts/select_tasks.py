"""Reproducible, stratified selection of EffiBench-X tasks.

Pool:     functional LeetCode problems with a canonical solution, test runner and
          starter code for Python, Java and C++; difficulty Medium or Hard.
Strata:   five categories x {Medium, Hard}, one problem per cell (10 in total).
Order:    categories are filled in the fixed order below; a problem chosen for one
          category is removed from the pool for the following ones.
Seed:     SEED (fixed, reported in the paper).

Output:   data/selected_effibench_tasks.json
"""
import json
import random
from pathlib import Path

SEED = 20261025
LANGS = {"python3", "java", "cpp"}
DIFFICULTIES = ["Medium", "Hard"]

# Category -> LeetCode tags that make a problem eligible for it.
CATEGORIES = {
    "sorting_searching": {"sorting", "binary-search"},
    "mathematics": {"math", "number-theory", "combinatorics"},
    "string_processing": {"string", "string-matching"},
    "dynamic_programming_recursion": {"dynamic-programming", "memoization",
                                      "recursion", "backtracking"},
    "data_structures": {"heap-priority-queue", "graph", "tree", "segment-tree",
                        "union-find", "trie", "monotonic-stack", "binary-indexed-tree"},
}

DATA = Path(__file__).resolve().parents[1] / "data"


def load_pool() -> list[dict]:
    meta = [json.loads(l) for l in (DATA / "effibench_x_metadata.jsonl").open()]
    extras = [json.loads(l) for l in (DATA / "effibench_x_extras.jsonl").open()]
    pool = []
    for m, e in zip(meta, extras, strict=True):
        assert m["id"] == e["id"]
        if m["type"] != "functional" or m["difficulty"] not in DIFFICULTIES:
            continue
        if not LANGS <= set(e["solution_langs"]) & set(e["runner_langs"]):
            continue
        if not {"python3", "java", "cpp"} <= set(e["starter_langs"]):
            continue
        pool.append({**m, "release_timestamp": e["release_timestamp"]})
    # Deterministic base order independent of shard layout.
    return sorted(pool, key=lambda p: p["title_slug"])


def main() -> None:
    rng = random.Random(SEED)
    pool = load_pool()
    chosen, used = [], set()
    for category, tags in CATEGORIES.items():
        for difficulty in DIFFICULTIES:
            eligible = [p for p in pool
                        if p["difficulty"] == difficulty
                        and tags & set(p["tags"] or [])
                        and p["title_slug"] not in used]
            pick = rng.choice(eligible)
            used.add(pick["title_slug"])
            chosen.append({
                "task_id": f"EB{len(chosen) + 1:02d}",
                "category": category,
                "difficulty": difficulty,
                "title": pick["title"],
                "title_slug": pick["title_slug"],
                "effibench_id": pick["id"],
                "tags": pick["tags"],
                "url": pick["url"],
                "release_timestamp": pick["release_timestamp"],
                "eligible_pool_size": len(eligible),
            })
    out = DATA / "selected_effibench_tasks.json"
    out.write_text(json.dumps({"seed": SEED, "pool_size": len(pool), "tasks": chosen},
                              indent=2))
    print(f"pool={len(pool)}")
    for t in chosen:
        print(f"{t['task_id']} {t['category']:<30} {t['difficulty']:<6} "
              f"{t['title']}  (pool {t['eligible_pool_size']})")


if __name__ == "__main__":
    main()
