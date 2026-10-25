"""Download full task data for the selected EffiBench-X problems.

Writes one directory per task to tasks/<task_id>/ with:
  task.json          metadata + description (markdown) + time/memory limits
  starter/<lang>     starter code given to the LLM
  reference/<lang>   canonical solution (not shown to the LLM)
  runner/<lang>      EffiBench-X test runner template
  test_generator.py  EffiBench-X test-case generator (run later, sandboxed)
  evaluator.py       EffiBench-X output evaluator
Generated tests are fetched separately by the correctness pipeline.
"""
import json
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

REPO = "datasets/EffiBench/effibench-x"
ROOT = Path(__file__).resolve().parents[1]
LANGS = {"python3": "py", "java": "java", "cpp": "cpp"}
COLUMNS = ["id", "title", "title_slug", "difficulty", "tags", "url", "description_md",
           "time_limit_nanos", "memory_limit_bytes", "starter_code", "solutions",
           "test_case_generator", "evaluator", "test_runners"]


def as_dict(value):
    if isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, list):
        value = dict(value)
    return value or {}


def code_of(entry):
    return entry["code"] if isinstance(entry, dict) and "code" in entry else entry


def main() -> None:
    selection = json.loads((ROOT / "data" / "selected_effibench_tasks.json").read_text())
    wanted = {t["title_slug"]: t for t in selection["tasks"]}
    fs = HfFileSystem()
    for shard in sorted(fs.glob(f"{REPO}/data/test-*.parquet")):
        with fs.open(shard, "rb", block_size=2**20) as f:
            table = pq.read_table(f, columns=COLUMNS)
        for row in table.to_pylist():
            sel = wanted.get(row["title_slug"])
            if not sel or row["id"] != sel["effibench_id"]:
                continue
            d = ROOT / "tasks" / sel["task_id"]
            for sub in ("starter", "reference", "runner"):
                (d / sub).mkdir(parents=True, exist_ok=True)
            starter, solutions, runners = (as_dict(row[k]) for k in
                                           ("starter_code", "solutions", "test_runners"))
            for lang, ext in LANGS.items():
                (d / "starter" / f"{lang}.{ext}").write_text(code_of(starter[lang]))
                (d / "reference" / f"{lang}.{ext}").write_text(code_of(solutions[lang]))
                (d / "runner" / f"{lang}.{ext}").write_text(code_of(runners[lang]))
            (d / "test_generator.py").write_text(row["test_case_generator"])
            (d / "evaluator.py").write_text(row["evaluator"])
            (d / "task.json").write_text(json.dumps({
                **sel,
                "description_md": row["description_md"],
                "time_limit_nanos": row["time_limit_nanos"],
                "memory_limit_bytes": row["memory_limit_bytes"],
                "source": "EffiBench-X (Apache-2.0), originally LeetCode",
            }, indent=2))
            print(f"{sel['task_id']}: {row['title']}")


if __name__ == "__main__":
    main()
