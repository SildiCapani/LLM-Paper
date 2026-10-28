"""One-time preparation on the reference machine (Linux laptop). Run before bundling.

    python3 prepare.py [--target 1.0]

1. tests      run each EffiBench-X test generator once (isolated, python -I) -> data/tests/
2. workloads  build the large measurement inputs (workloads.py)               -> data/workloads/
3. references build the canonical solutions, check them against the tests, and compute
              the expected workload output (C++ reference, cross-checked with Java/Python)
4. calibrate  choose per task the in-process repetitions R (EB) or the input size N (CLBG)
              so that the C++ program runs about --target seconds on this machine, but
              the slowest reference (usually Python) at most --max-slow seconds
              (EB: C++ reference; CLBG: median of the generated C++ programs passing the
              check, since the CLBG reference exists in Python only)

Everything ends up in data/manifest.json (paths relative to experiment/), which run_platform.py uses on every platform.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from common import (DATA, EXT, GENERATED, LANGS, REF_FILE, TASKS, detect_tools, evaluator,
                    run_proc, task_format, task_ids)
from harness import build, clbg_sources, eb_sources
from workloads import make as make_workload

GEN_WRAPPER = """import json, sys, runpy, threading
sys.setrecursionlimit(1_000_000)
threading.stack_size(512 * 1024 * 1024)
res = {}
def main():
    ns = runpy.run_path(sys.argv[1])
    res["cases"] = ns["generate_test_cases"](int(sys.argv[2]), int(sys.argv[3]))
t = threading.Thread(target=main); t.start(); t.join()
json.dump(res["cases"], sys.stdout)
"""

# Candidate input sizes for CLBG calibration (ascending).
CLBG_LADDER = {
    "CLBG01": [1_000_000, 2_000_000, 3_000_000, 5_000_000, 7_000_000, 10_000_000, 20_000_000],
    "CLBG02": [1000, 1500, 2000, 2500, 3000, 4000, 5500],
    "CLBG03": [16, 17, 18, 19, 20],
    "CLBG04": [9, 10, 11, 12],
}


PROBLEMS: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_tests(n_cases: int, seed: int) -> None:
    out = DATA / "tests"
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wrapper = Path(tmp, "run_gen.py")
        wrapper.write_text(GEN_WRAPPER)
        for task in task_ids():
            gen = TASKS / task / "test_generator.py"
            if not gen.exists():
                continue
            p = subprocess.run([sys.executable, "-I", str(wrapper), str(gen), str(n_cases),
                                str(seed)], capture_output=True, text=True, cwd=tmp,
                               timeout=900)
            if p.returncode != 0:
                sys.exit(f"{task}: test generator failed\n{p.stderr[-2000:]}")
            cases = json.loads(p.stdout)
            (out / f"{task}.json").write_text(json.dumps(cases))
            print(f"  tests {task}: {len(cases)} cases")


def make_workloads() -> None:
    out = DATA / "workloads"
    out.mkdir(parents=True, exist_ok=True)
    for task in task_ids():
        if task_format(task) == "function":
            (out / f"{task}.txt").write_text(make_workload(task))
            print(f"  workload {task}: {(out / f'{task}.txt').stat().st_size / 1e6:.2f} MB")


def per_iteration(cmd: list[str], stdin: bytes, timeout: float) -> float:
    """Seconds per repetition from t(R) = a + b*R: R grows until t(R) - t(1) >= 0.5 s."""
    t1 = min(run_proc(cmd + ["1"], stdin, timeout)["wall_s"] for _ in range(3))
    r = 4
    while True:
        tr = min(run_proc(cmd + [str(r)], stdin, timeout)["wall_s"] for _ in range(2))
        if tr - t1 >= 0.5 or r >= 10**8:
            return max((tr - t1) / (r - 1), 1e-9)
        r = r * 4 if tr - t1 < 0.05 else int(r * 0.6 / max(tr - t1, 1e-3)) + 1


def prepare_eb(task: str, tools: dict, build_root: Path, target: float,
               max_slow: float) -> dict:
    tests = json.loads((DATA / "tests" / f"{task}.json").read_text())
    wl_path = DATA / "workloads" / f"{task}.txt"
    wl = wl_path.read_bytes()
    evaluate = evaluator(task)
    runs, outputs, ref_iter = {}, {}, {}
    for lang in LANGS:
        runner = (TASKS / task / "runner" / REF_FILE[lang]).read_text()
        code = (TASKS / task / "reference" / REF_FILE[lang]).read_text()
        ok, cmd, msg = build(lang, eb_sources(lang, runner, code),
                             build_root / task / lang, tools["paths"])
        if not ok:
            sys.exit(f"{task}/{lang}: reference does not compile\n{msg}")
        runs[lang] = cmd
        failed = [i for i, c in enumerate(tests)
                  if not evaluate(c["output"], run_proc(cmd + ["1"], c["input"].encode(),
                                                        60)["out"].decode(errors="replace"))]
        if failed:
            print(f"  WARNING {task}/{lang}: reference fails tests {failed}")
            PROBLEMS.append(f"{task}/{lang}: reference fails {len(failed)} tests")
        r = run_proc(cmd + ["1"], wl, 600)
        if r["rc"] != 0 or r["timed_out"]:
            sys.exit(f"{task}/{lang}: reference fails on workload: {r['err'][-500:]!r}")
        outputs[lang] = r["out"].decode()
    expected = outputs["cpp"]
    for lang in ("java", "python"):
        if not evaluate(expected, outputs[lang]):
            print(f"  WARNING {task}: workload output of cpp and {lang} reference differ")
            PROBLEMS.append(f"{task}: workload output cpp vs {lang} differ")
    exp_path = DATA / "workloads" / f"{task}.expected.txt"
    exp_path.write_text(expected)

    for lang in LANGS:
        ref_iter[lang] = per_iteration(runs[lang], wl, 3600)
    # C++ about `target` seconds, but no reference language above `max_python` seconds.
    reps = max(1, min(math.ceil(target / ref_iter["cpp"]),
                      math.floor(max_slow / max(ref_iter.values()))))
    print(f"  {task}: R={reps}  per call cpp={ref_iter['cpp'] * 1e3:.2f} ms  "
          f"java={ref_iter['java'] * 1e3:.2f} ms  python={ref_iter['python'] * 1e3:.2f} ms  "
          f"-> est. python {reps * ref_iter['python']:.1f} s")
    return {"format": "function", "tests": f"bench/data/tests/{task}.json",
            "tests_sha256": sha(DATA / "tests" / f"{task}.json"),
            "workload": f"bench/data/workloads/{task}.txt", "workload_sha256": sha(wl_path),
            "workload_expected": f"bench/data/workloads/{task}.expected.txt",
            "arg": reps, "arg_kind": "repetitions",
            "ref_seconds_per_call_laptop": ref_iter,
            "est_ref_seconds_laptop": {l: reps * ref_iter[l] for l in LANGS}}


def prepare_clbg(task: str, tools: dict, build_root: Path, target: float,
                 max_slow: float) -> dict:
    meta = json.loads((TASKS / task / "task.json").read_text())
    check_n = meta["check_input_n"]
    exp_check = (TASKS / task / "expected" / f"n{check_n}.txt").read_text()
    evaluate = evaluator(task)
    ref_cmd = [tools["paths"]["python"], "-I", str(TASKS / task / "reference" / "python3.py")]
    if not evaluate(exp_check, run_proc(ref_cmd + [str(check_n)], None, 600)["out"].decode()):
        sys.exit(f"{task}: python reference fails the check input")
    # Generated C++ programs that pass the check input serve as calibration probes.
    probes = []
    for code in sorted(GENERATED.glob(f"*/{task}/cpp/s*/code.cpp")):
        d = build_root / task / "probe" / f"{code.parts[-5]}_{code.parts[-2]}"
        ok, cmd, _ = build("cpp", clbg_sources("cpp", code.read_text()), d, tools["paths"])
        if ok and evaluate(exp_check, run_proc(cmd + [str(check_n)], None, 120)["out"]
                           .decode(errors="replace")):
            probes.append(cmd)
    if len(probes) < 3:
        sys.exit(f"{task}: fewer than 3 generated C++ programs pass the check")
    # Largest N with the Python reference <= max_slow, stopping once C++ reaches target.
    chosen = None
    for n in CLBG_LADDER[task]:
        median = statistics.median(run_proc(cmd + [str(n)], None, 300)["wall_s"]
                                   for cmd in probes)
        ref = run_proc(ref_cmd + [str(n)], None, 3 * max_slow)
        print(f"  {task}: N={n} median C++ {median:.2f} s ({len(probes)} programs), "
              f"python reference {ref['wall_s']:.1f} s")
        if ref["timed_out"] or ref["wall_s"] > max_slow:
            break
        if ref["rc"] != 0:
            sys.exit(f"{task}: python reference failed at N={n}")
        chosen = (n, median, ref)
        if median >= target:
            break
    if chosen is None:
        sys.exit(f"{task}: even the smallest N exceeds the time limit")
    chosen, median, ref = chosen
    exp_path = DATA / "workloads" / f"{task}.n{chosen}.expected.txt"
    exp_path.write_bytes(ref["out"])
    print(f"  {task}: chosen N={chosen}")
    return {"format": "program", "check_n": check_n,
            "check_expected": f"tasks/{task}/expected/n{check_n}.txt",
            "arg": chosen, "arg_kind": "N",
            "workload_expected": f"bench/data/workloads/{task}.n{chosen}.expected.txt",
            "est_ref_seconds_laptop": {"cpp_generated_median": median,
                                       "python": ref["wall_s"]}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=float, default=1.0,
                    help="seconds the C++ program should run on this machine")
    ap.add_argument("--max-slow", type=float, default=60.0,
                    help="upper limit in seconds for the slowest reference language")
    ap.add_argument("--cases", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--only", nargs="+", help="restrict calibration to these tasks")
    args = ap.parse_args()
    tools = detect_tools()
    for w in tools["warnings"]:
        print("WARNING:", w)
    print("1/4 test cases"); make_tests(args.cases, args.seed)
    print("2/4 workloads"); make_workloads()
    print("3+4/4 references and calibration")
    manifest_path = DATA / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    with tempfile.TemporaryDirectory() as tmp:
        for task in args.only or task_ids():
            fn = prepare_eb if task_format(task) == "function" else prepare_clbg
            manifest[task] = fn(task, tools, Path(tmp), args.target, args.max_slow)
            manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["_meta"] = {"target_seconds_cpp_laptop": args.target,
                         "max_seconds_slowest_reference": args.max_slow, "tools": tools,
                         "test_cases": args.cases, "test_seed": args.seed}
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {manifest_path}")
    if PROBLEMS:
        print("PROBLEMS (fix before bundling):\n  " + "\n  ".join(PROBLEMS))
        sys.exit(1)


if __name__ == "__main__":
    main()
