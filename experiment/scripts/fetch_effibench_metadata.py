"""Fetch lightweight metadata of all EffiBench-X problems (no test data).

Reads only the needed columns from the Hugging Face parquet shards via
HTTP range requests and writes data/effibench_x_metadata.jsonl.
"""
import json
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

REPO = "datasets/EffiBench/effibench-x"
COLUMNS = ["id", "title", "title_slug", "difficulty", "tags", "source", "url",
           "type", "release_date", "time_limit_nanos", "memory_limit_bytes",
           "description"]
OUT = Path(__file__).resolve().parents[1] / "data" / "effibench_x_metadata.jsonl"


def main() -> None:
    fs = HfFileSystem()
    shards = sorted(fs.glob(f"{REPO}/data/test-*.parquet"))
    with OUT.open("w") as out:
        for shard in shards:
            with fs.open(shard, "rb", block_size=2**20) as f:
                table = pq.read_table(f, columns=COLUMNS)
            for row in table.to_pylist():
                row["release_date"] = str(row["release_date"]) if row["release_date"] else None
                out.write(json.dumps(row) + "\n")
            print(f"{shard}: {table.num_rows} rows")


if __name__ == "__main__":
    main()
