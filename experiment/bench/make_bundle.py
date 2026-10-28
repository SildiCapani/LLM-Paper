"""Pack everything a platform needs into one ZIP (run on the laptop after prepare.py).

    python3 make_bundle.py            -> experiment/llm-energy-bundle.zip

Contents: the generated code, task runners/references/evaluators, the fixed test and
workload data, and the scripts. Not included: dataset test generators (never executed on
the platforms), raw CLI responses, credentials.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from common import DATA, ROOT

TOP = "llm-energy"
PATTERNS = [
    "bench/*.py", "bench/data/**/*",
    "measure/energy.py", "measure/measure.py",
    "tasks/*/task.json", "tasks/*/runner/*", "tasks/*/reference/*", "tasks/*/evaluator.py",
    "tasks/*/expected/*",
    "generated/*/*/*/s*/code.*", "generated/requests_log.csv",
    "LAUFEN_UND_MESSEN.md",
]


def main() -> None:
    if not (DATA / "manifest.json").exists():
        raise SystemExit("data/manifest.json missing: run prepare.py first")
    files = sorted({p for pat in PATTERNS for p in ROOT.glob(pat) if p.is_file()
                    and "__pycache__" not in p.parts})
    n_code = sum(1 for f in files if f.name.startswith("code.") and "generated" in f.parts)
    if n_code != 630:
        print(f"WARNING: {n_code} generated programs found (expected 630)")
    out = ROOT / "llm-energy-bundle.zip"
    listing = {}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            rel = f.relative_to(ROOT).as_posix()
            zf.write(f, f"{TOP}/{rel}")
            listing[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
        zf.writestr(f"{TOP}/bundle_manifest.json", json.dumps(listing, indent=1))
    print(f"Wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {len(files)} files, "
          f"{n_code} generated programs)")


if __name__ == "__main__":
    main()
