"""Run the whole experiment on one platform: build, test, measure, pack.

    python3 run_platform.py check                 # toolchain, energy reader, time estimate
    python3 run_platform.py run --name laptop     # everything; resumable after Ctrl+C

Phases (each one is skipped when its result file is complete):
  1. build        all generated programs (630) and the reference solutions
  2. correctness  small test cases + one workload run per program (parallel, not measured)
  3. measure      every correct program x --reps on the workload, in a fixed random order,
                  with idle baselines; one CSV row per run, appended immediately
  4. pack         results/<name>/ -> results_<name>.zip (send this file back)

Absolute energy values are platform-specific; compare rankings and ratios only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import shutil
import statistics
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from common import (DATA, EXT, GENERATED, LANGS, REF_FILE, ROOT, TASKS, detect_tools,
                    evaluator, load_manifest, run_proc, task_ids)
from harness import build, clbg_sources, eb_sources

sys.path.insert(0, str(ROOT / "measure"))
from energy import cpu_temperature, detect_reader, platform_info  # noqa: E402
from measure import measure_idle, run_once  # noqa: E402

RESULTS = ROOT / "results"
SEED = 20261025


def log(msg: str, out: Path | None = None) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    if out:
        with (out / "log.txt").open("a") as f:
            f.write(line + "\n")


# --------------------------------------------------------------------------- programs

def programs() -> list[dict]:
    """All generated programs plus the reference solutions."""
    progs = []
    for code in sorted(GENERATED.glob("*/*/*/s*/code.*")):
        llm, task, lang, sample = code.parts[-5:-1]
        progs.append({"id": f"{llm}-{task}-{lang}-{sample}", "llm": llm, "task": task,
                      "lang": lang, "sample": sample[1:], "source": "generated",
                      "code": code})
    for task in task_ids():
        for lang in LANGS:
            ref = TASKS / task / "reference" / REF_FILE[lang]
            if ref.exists():
                progs.append({"id": f"reference-{task}-{lang}", "llm": "reference",
                              "task": task, "lang": lang, "sample": "", "source": "reference",
                              "code": ref})
    return progs


def sources(p: dict) -> dict[str, str]:
    code = p["code"].read_text(encoding="utf-8")
    if (TASKS / p["task"] / "runner").exists():
        runner = (TASKS / p["task"] / "runner" / REF_FILE[p["lang"]]).read_text()
        return eb_sources(p["lang"], runner, code)
    return clbg_sources(p["lang"], code)


def est_seconds(m: dict, lang: str) -> float:
    """Expected run time of a typical program on the laptop (for timeouts/estimates)."""
    e = m["est_ref_seconds_laptop"]
    if m["format"] == "function":
        return e[lang]
    return e["python"] if lang == "python" else 2 * e["cpp_generated_median"]


# --------------------------------------------------------------------------- csv state

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


class Appender:
    def __init__(self, path: Path, fields: list[str]):
        new = not path.exists()
        self.f = path.open("a", newline="")
        self.w = csv.DictWriter(self.f, fieldnames=fields, extrasaction="ignore")
        if new:
            self.w.writeheader()

    def add(self, row: dict) -> None:
        self.w.writerow(row)
        self.f.flush()


# --------------------------------------------------------------------------- phases

def phase_build(progs, tools, out, work, workers) -> dict[str, dict]:
    path = out / "build.csv"
    done = {r["program_id"]: r for r in read_csv(path)}
    todo = [p for p in progs if p["id"] not in done]
    log(f"Phase 1/4 build: {len(done)} done, {len(todo)} to build", out)
    app = Appender(path, ["program_id", "llm", "task", "lang", "sample", "source",
                          "compiled", "code_sha256", "run_cmd", "message"])

    def one(p):
        ok, cmd, msg = build(p["lang"], sources(p), work / p["id"], tools["paths"])
        return p, ok, cmd, msg

    with ThreadPoolExecutor(workers) as ex:
        for i, (p, ok, cmd, msg) in enumerate(ex.map(one, todo), 1):
            row = {"program_id": p["id"], "llm": p["llm"], "task": p["task"],
                   "lang": p["lang"], "sample": p["sample"], "source": p["source"],
                   "compiled": int(ok),
                   "code_sha256": hashlib.sha256(p["code"].read_bytes()).hexdigest(),
                   "run_cmd": json.dumps(cmd), "message": "" if ok else msg[-600:]}
            app.add(row)
            done[p["id"]] = row
            if i % 50 == 0 or i == len(todo):
                log(f"  built {i}/{len(todo)}")
    return done


def phase_correctness(built, manifest, out, workers, factor) -> dict[str, dict]:
    path = out / "correctness.csv"
    done = {r["program_id"]: r for r in read_csv(path)}
    todo = [b for b in built.values() if b["program_id"] not in done]
    log(f"Phase 2/4 correctness: {len(done)} done, {len(todo)} to check", out)
    app = Appender(path, ["program_id", "status", "tests_passed", "tests_total",
                          "workload_ok", "workload_wall_s", "workload_out_sha256", "detail"])

    def one(b):
        task, lang = b["task"], b["lang"]
        m = manifest[task]
        row = {"program_id": b["program_id"], "tests_passed": 0, "tests_total": 0,
               "workload_ok": 0, "workload_wall_s": "", "workload_out_sha256": "",
               "detail": ""}
        if b["compiled"] != "1":
            return {**row, "status": "compile_error", "detail": b["message"][-300:]}
        cmd = json.loads(b["run_cmd"])
        evaluate = evaluator(task)
        if m["format"] == "function":
            tests = json.loads((ROOT / m["tests"]).read_text())
            cases = [(c["input"].encode(), c["output"], ["1"]) for c in tests]
            wl_in = (ROOT / m["workload"]).read_bytes()
            wl_args = ["1"]
        else:
            cases = [(None, (ROOT / m["check_expected"]).read_text(), [str(m["check_n"])])]
            wl_in, wl_args = None, [str(m["arg"])]
        row["tests_total"] = len(cases)
        for stdin, expected, args in cases:
            r = run_proc(cmd + args, stdin, 30 * factor)
            if not r["timed_out"] and r["rc"] == 0 and \
                    evaluate(expected, r["out"].decode(errors="replace")):
                row["tests_passed"] += 1
            elif not row["detail"]:
                row["detail"] = ("timeout" if r["timed_out"] else
                                 f"rc={r['rc']} {r['err'][-200:].decode(errors='replace')}")
        if row["tests_passed"] < row["tests_total"]:
            return {**row, "status": "wrong"}
        limit = max(60.0, 10 * est_seconds(m, lang) / (m["arg"] if m["format"] == "function"
                                                         else 1)) * factor
        r = run_proc(cmd + wl_args, wl_in, limit)
        row["workload_wall_s"] = round(r["wall_s"], 3)
        if r["timed_out"]:
            return {**row, "status": "too_slow", "detail": f"workload > {limit:.0f} s"}
        expected = (ROOT / m["workload_expected"]).read_text()
        if r["rc"] != 0 or not evaluate(expected, r["out"].decode(errors="replace")):
            return {**row, "status": "wrong_workload",
                    "detail": r["err"][-200:].decode(errors="replace")}
        return {**row, "status": "pass", "workload_ok": 1}

    with ThreadPoolExecutor(workers) as ex:
        for i, row in enumerate(ex.map(one, todo), 1):
            app.add(row)
            done[row["program_id"]] = row
            if i % 50 == 0 or i == len(todo):
                log(f"  checked {i}/{len(todo)}")
    counts: dict[str, int] = {}
    for r in done.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    log(f"  correctness: {counts}", out)
    return done


def phase_measure(built, correct, manifest, out, args, reader, factor) -> None:
    path = out / "runs.csv"
    passing = [b for b in built.values() if correct[b["program_id"]]["status"] == "pass"]
    schedule = [(b, rep) for b in passing for rep in range(1, args.reps + 1)]
    random.Random(SEED).shuffle(schedule)
    prev = read_csv(path)
    done = {(r["program_id"], r["rep"]) for r in prev}
    skipped = {r["program_id"] for r in prev if r["timed_out"] == "True"}
    todo = [(b, rep) for b, rep in schedule if (b["program_id"], str(rep)) not in done]
    log(f"Phase 3/4 measure: {len(passing)} programs x {args.reps} reps, "
        f"{len(done)} runs done, {len(todo)} to go", out)
    domains = reader.domains
    app = Appender(path, ["run_utc", "program_id", "llm", "task", "lang", "sample", "source",
                          "rep", "arg", "exit_code", "timed_out", "wall_s", "user_s",
                          "sys_s", "maxrss_mb", "temp_before_c", "output_same"]
                   + [f"energy_{d}_j" for d in domains]
                   + [f"net_energy_{d}_j" for d in domains] + ["idle_ref_utc"])
    idle_app = Appender(out / "idle.csv", ["utc", "seconds"]
                        + [f"power_{d}_w" for d in domains])

    def idle(seconds: float) -> dict:
        p = measure_idle(reader, seconds)
        idle_app.add({"utc": datetime.now(timezone.utc).isoformat(), "seconds": seconds,
                      **{f"power_{d}_w": p.get(d) for d in domains}})
        return p

    if not todo:
        return
    log(f"  idle baseline {args.idle} s ...", out)
    idle_power, idle_utc, last_idle = idle(args.idle), datetime.now(timezone.utc), time.time()
    t_start, durations = time.time(), []
    for i, (b, rep) in enumerate(todo, 1):
        if b["program_id"] in skipped:
            continue
        if time.time() - last_idle > args.idle_every * 60:
            idle_power, idle_utc, last_idle = idle(args.idle / 2), datetime.now(
                timezone.utc), time.time()
        m = manifest[b["task"]]
        cmd = json.loads(b["run_cmd"]) + [str(m["arg"])]
        stdin = str(ROOT / m["workload"]) if m["format"] == "function" else None
        limit = max(60.0, 10 * est_seconds(m, b["lang"])) * factor
        r = run_once({"cmd": cmd, "stdin": stdin}, ROOT, reader, args.cpus, limit)
        same = r["stdout_sha256"] == correct[b["program_id"]]["workload_out_sha256"]
        row = {"run_utc": datetime.now(timezone.utc).isoformat(), "program_id": b["program_id"],
               "llm": b["llm"], "task": b["task"], "lang": b["lang"], "sample": b["sample"],
               "source": b["source"], "rep": rep, "arg": m["arg"],
               **{k: r[k] for k in ("exit_code", "timed_out", "wall_s", "user_s", "sys_s",
                                    "maxrss_mb", "temp_before_c")},
               "output_same": int(same), "idle_ref_utc": idle_utc.isoformat()}
        for d in domains:
            row[f"energy_{d}_j"] = r["energy"].get(d)
            row[f"net_energy_{d}_j"] = r["energy"].get(d, 0) - idle_power.get(d, 0) * r["wall_s"]
        app.add(row)
        if r["timed_out"]:
            skipped.add(b["program_id"])
        durations.append(r["wall_s"] + args.cooldown)
        eta = statistics.mean(durations) * (len(todo) - i) / 3600
        main = domains[0] if domains else None
        e = f" {r['energy'][main]:.1f} J" if main else ""
        print(f"[{i}/{len(todo)}] {b['program_id']} r{rep}: {r['wall_s']:.2f} s{e}"
              f"{' TIMEOUT' if r['timed_out'] else ''}{'' if same else ' OUTPUT-DIFF'}"
              f"  (ETA {eta:.1f} h)", flush=True)
        time.sleep(args.cooldown)
    idle(args.idle)
    log(f"  measurement finished after {(time.time() - t_start) / 3600:.1f} h", out)


def pack(out: Path, name: str) -> Path:
    z = ROOT / f"results_{name}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                zf.write(f, f"results_{name}/{f.relative_to(out)}")
    return z


# --------------------------------------------------------------------------- commands

def speed_factor(tools: dict, manifest: dict, work: Path) -> float:
    """How much slower this machine is than the laptop (C++ reference of EB03)."""
    m = manifest["EB03"]
    runner = (TASKS / "EB03" / "runner" / "cpp.cpp").read_text()
    code = (TASKS / "EB03" / "reference" / "cpp.cpp").read_text()
    ok, cmd, _ = build("cpp", eb_sources("cpp", runner, code), work / "_speed", tools["paths"])
    if not ok:
        return 1.0
    stdin = (ROOT / m["workload"]).read_bytes()
    t = min(run_proc(cmd + [str(m["arg"])], stdin, 300)["wall_s"] for _ in range(3))
    return max(1.0, t / m["est_ref_seconds_laptop"]["cpp"])


def environment(args) -> tuple[dict, object, str, list[str]]:
    tools = detect_tools(args.python, args.java_home, args.cxx)
    info = platform_info()
    reader, note = detect_reader("none" if args.no_energy else "auto")
    warnings = list(tools["warnings"])
    if info.get("governor") not in (None, "performance"):
        warnings.append(f"CPU governor is '{info['governor']}', not 'performance'")
    if info.get("turbo") == "on":
        warnings.append("turbo boost is on")
    if not reader.domains:
        warnings.append(f"no energy measurement ({note})")
    return {"platform": info, "tools": tools, "energy_reader": reader.name,
            "energy_domains": reader.domains, "energy_note": note,
            "cpu_temp_c": cpu_temperature()}, reader, note, warnings


def estimate_hours(manifest: dict, factor: float, reps: int, cooldown: float) -> float:
    n_per_lang = {lang: len(list(GENERATED.glob(f"*/*/{lang}/s*/code.*"))) // 14
                  for lang in LANGS}  # programs per task and language
    total = 0.0
    for task, m in manifest.items():
        if task.startswith("_"):
            continue
        for lang in LANGS:
            total += (n_per_lang[lang] + 1) * reps * (est_seconds(m, lang) * factor + cooldown)
    return total / 3600


def cmd_check(args) -> None:
    if platform.system() == "Windows":
        sys.exit("Windows is not supported (no energy counters); see LAUFEN_UND_MESSEN.md.")
    env, reader, note, warnings = environment(args)
    manifest = load_manifest()
    work = RESULTS / "_work_check"
    factor = speed_factor(env["tools"], manifest, work)
    shutil.rmtree(work, ignore_errors=True)
    print("Platform:", json.dumps(env["platform"], indent=2))
    print("Tools:")
    for k, v in env["tools"]["versions"].items():
        print(f"  {k:<7} {v}   ({env['tools']['paths'][k]})")
    print(f"Energy reader: {reader.name} ({note}); domains: {', '.join(reader.domains) or '-'}")
    if reader.domains:
        idle = measure_idle(reader, 3)
        print("  idle power over 3 s: " + ", ".join(f"{d}={w:.2f} W" for d, w in idle.items()))
    print(f"Speed relative to the laptop: {factor:.2f}x slower")
    print(f"Estimated measurement time with --reps {args.reps}, --cooldown {args.cooldown}: "
          f"{estimate_hours(manifest, factor, args.reps, args.cooldown):.1f} h "
          f"(plus about 30-60 min for build and correctness)")
    for w in warnings:
        print("WARNING:", w)
    if hasattr(reader, "close"):
        reader.close()


def cmd_run(args) -> None:
    if platform.system() == "Windows":
        sys.exit("Windows is not supported (no energy counters); see LAUFEN_UND_MESSEN.md.")
    out = RESULTS / args.name
    work = RESULTS / f"_work_{args.name}"
    out.mkdir(parents=True, exist_ok=True)
    env, reader, note, warnings = environment(args)
    if not reader.domains and not args.no_energy:
        sys.exit(f"No energy reader available ({note}). Fix this first "
                 "(see LAUFEN_UND_MESSEN.md) or use --no-energy for time/memory only.")
    for w in warnings:
        log(f"WARNING: {w}", out)
    manifest = load_manifest()
    factor = speed_factor(env["tools"], manifest, work)
    log(f"Platform {env['platform'].get('cpu', env['platform']['machine'])}, "
        f"energy: {reader.name}, speed factor {factor:.2f}", out)
    env.update({"started_utc": datetime.now(timezone.utc).isoformat(), "speed_factor": factor,
                "args": {k: v for k, v in vars(args).items() if k != "func"},
                "manifest_sha256": hashlib.sha256((DATA / "manifest.json").read_bytes())
                .hexdigest(), "warnings": warnings, "python_orchestrator": sys.version})
    runs = sorted(out.glob("environment_*.json"))
    (out / f"environment_{len(runs) + 1}.json").write_text(json.dumps(env, indent=2))

    workers = args.workers or max(1, (os.cpu_count() or 2) - 1)
    progs = programs()
    built = phase_build(progs, env["tools"], out, work, workers)
    correct = phase_correctness(built, manifest, out, workers, factor)
    phase_measure(built, correct, manifest, out, args, reader, factor)
    if hasattr(reader, "close"):
        reader.close()
    z = pack(out, args.name)
    log(f"Phase 4/4 done. Send this file back: {z}", out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    for name, fn in (("check", cmd_check), ("run", cmd_run)):
        p = sub.add_parser(name)
        p.set_defaults(func=fn)
        p.add_argument("--reps", type=int, default=5)
        p.add_argument("--cooldown", type=float, default=3.0, help="seconds between runs")
        p.add_argument("--python", help="interpreter for the programs (default: python3.14)")
        p.add_argument("--java-home", help="JDK directory (default: JAVA_HOME or PATH)")
        p.add_argument("--cxx", help="C++ compiler (default: g++-14, then g++)")
        p.add_argument("--no-energy", action="store_true",
                       help="measure time and memory only (no energy reader)")
        if name == "run":
            p.add_argument("--name", required=True,
                           help="platform name, e.g. laptop, server, mac, pi")
            p.add_argument("--idle", type=float, default=60, help="idle baseline seconds")
            p.add_argument("--idle-every", type=float, default=30,
                           help="minutes between idle baselines")
            p.add_argument("--cpus", type=lambda s: [int(c) for c in s.split(",")],
                           help="pin programs to these CPUs (Linux), e.g. 2,3")
            p.add_argument("--workers", type=int, help="parallel jobs for build/correctness")
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
