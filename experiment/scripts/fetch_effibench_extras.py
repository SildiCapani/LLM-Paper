"""Fetch per-problem solution languages, runner languages and starter code."""
import json
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

REPO = "datasets/EffiBench/effibench-x"
OUT = Path(__file__).resolve().parents[1] / "data" / "effibench_x_extras.jsonl"


def keys(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    if isinstance(value, dict):
        return sorted(k for k, v in value.items() if v)
    if isinstance(value, list):  # pyarrow map type
        return sorted(k for k, v in value if v)
    return []


def main() -> None:
    fs = HfFileSystem()
    with OUT.open("w") as out:
        for shard in sorted(fs.glob(f"{REPO}/data/test-*.parquet")):
            with fs.open(shard, "rb", block_size=2**20) as f:
                t = pq.read_table(f, columns=["id", "release_timestamp", "starter_code",
                                              "solutions", "test_runners"])
            for r in t.to_pylist():
                out.write(json.dumps({
                    "id": r["id"],
                    "release_timestamp": r["release_timestamp"],
                    "solution_langs": keys(r["solutions"]),
                    "runner_langs": keys(r["test_runners"]),
                    "starter_langs": keys(r["starter_code"]),
                }) + "\n")


if __name__ == "__main__":
    main()
