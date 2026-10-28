"""Measure energy, time and memory of programs (Linux: RAPL, Pi: PMIC, macOS: powermetrics).

Usage:
    python3 measure.py check
    python3 measure.py run JOBS.json --reps 10 --out results/run1.csv

A jobs file is a JSON list of programs to measure:

    [{"id": "CLBG01-python-ref",
      "cmd": ["python3", "-I", "../../tasks/CLBG01/reference/python3.py", "200000"],
      "stdin": null,
      "meta": {"task": "CLBG01", "language": "python", "source": "reference"}}]

Relative paths in "cmd" and "stdin" are resolved against the jobs file's directory,
which is also the working directory of every program.

Procedure: idle baseline -> warm-up runs (not recorded) -> all job x repetition pairs
in random order, each followed by a cool-down -> idle baseline again. Net energy is
gross energy minus the mean idle power of both baselines times the run's wall time.
Results go to a CSV file (one row per run) and a JSON file with platform metadata.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from energy import cpu_temperature, detect_reader, platform_info

IS_LINUX = platform.system() == "Linux"
MAXRSS_TO_MB = 1 / 1024 if IS_LINUX else 1 / (1024 * 1024)  # KiB on Linux, bytes on macOS


def measure_idle(reader, seconds: float) -> dict[str, float]:
    """Mean idle power in watts per energy domain."""
    if not reader.domains or seconds <= 0:
        return {}
    reader.start()
    t0 = time.perf_counter()
    time.sleep(seconds)
    energy = reader.stop()
    elapsed = time.perf_counter() - t0
    return {d: e / elapsed for d, e in energy.items()}


def run_once(job: dict, base: Path, reader, cpus: list[int] | None, timeout: float) -> dict:
    cmd = [str((base / c).resolve()) if (base / c).exists() and not c.startswith("-") else c
           for c in job["cmd"]]
    stdin_path = base / job["stdin"] if job.get("stdin") else None

    def preexec():
        os.setsid()
        if cpus and IS_LINUX:
            os.sched_setaffinity(0, cpus)

    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err, \
            (open(stdin_path, "rb") if stdin_path else open(os.devnull, "rb")) as fin:
        temp_before = cpu_temperature()
        reader.start()
        t0 = time.perf_counter()
        proc = subprocess.Popen(cmd, stdin=fin, stdout=out, stderr=err, cwd=base,
                                preexec_fn=preexec)
        timed_out = threading.Event()

        def kill():
            timed_out.set()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        timer = threading.Timer(timeout, kill)
        timer.start()
        _, status, rusage = os.wait4(proc.pid, 0)
        t1 = time.perf_counter()
        energy = reader.stop()
        timer.cancel()
        proc.returncode = os.waitstatus_to_exitcode(status)

        out.seek(0)
        digest = hashlib.sha256(out.read()).hexdigest()
        err.seek(0)
        stderr_tail = err.read()[-300:].decode(errors="replace").replace("\n", " | ")

    return {
        "exit_code": proc.returncode,
        "timed_out": timed_out.is_set(),
        "wall_s": t1 - t0,
        "user_s": rusage.ru_utime,
        "sys_s": rusage.ru_stime,
        "maxrss_mb": rusage.ru_maxrss * MAXRSS_TO_MB,
        "stdout_sha256": digest,
        "stderr_tail": stderr_tail,
        "temp_before_c": temp_before,
        "energy": energy,
    }


def cmd_check(args) -> None:
    info = platform_info()
    reader, note = detect_reader(args.reader)
    print("Platform:")
    for k, v in info.items():
        print(f"  {k:<10} {v}")
    print(f"Energy reader: {reader.name} ({note})")
    print(f"  domains: {', '.join(reader.domains) or '-'}")
    if reader.domains:
        idle = measure_idle(reader, 3)
        print("  idle power over 3 s: "
              + ", ".join(f"{d}={w:.2f} W" for d, w in idle.items()))
    warnings = []
    if info.get("governor") not in (None, "performance"):
        warnings.append(f"CPU governor is '{info['governor']}', not 'performance'")
    if info.get("turbo") == "on":
        warnings.append("turbo boost is on (higher variance)")
    if not reader.domains:
        warnings.append("no energy measurement: only time and memory will be recorded")
    for w in warnings:
        print(f"WARNING: {w}")
    if hasattr(reader, "close"):
        reader.close()


def cmd_run(args) -> None:
    jobs_path = Path(args.jobs).resolve()
    base = jobs_path.parent
    jobs = json.loads(jobs_path.read_text())
    reader, note = detect_reader(args.reader)
    if not reader.domains and not args.allow_no_energy:
        sys.exit(f"No energy reader available ({note}). "
                 "Use --allow-no-energy to record time and memory only.")
    cpus = [int(c) for c in args.cpus.split(",")] if args.cpus else None
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Energy reader: {reader.name} ({note})")
    print(f"Idle baseline ({args.idle} s) ...")
    idle_before = measure_idle(reader, args.idle)

    for job in jobs:
        for _ in range(args.warmup):
            run_once(job, base, reader, cpus, args.timeout)

    schedule = [(job, rep) for job in jobs for rep in range(1, args.reps + 1)]
    random.Random(args.seed).shuffle(schedule)

    meta_keys = sorted({k for job in jobs for k in job.get("meta", {})})
    domains = reader.domains
    fields = (["run_index", "job_id", "rep"] + meta_keys
              + ["exit_code", "timed_out", "wall_s", "user_s", "sys_s", "maxrss_mb",
                 "temp_before_c", "stdout_sha256"]
              + [f"energy_{d}_j" for d in domains]
              + [f"net_energy_{d}_j" for d in domains]
              + ["stderr_tail"])
    rows = []
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, (job, rep) in enumerate(schedule, 1):
            r = run_once(job, base, reader, cpus, args.timeout)
            row = {"run_index": i, "job_id": job["id"], "rep": rep,
                   **{k: job.get("meta", {}).get(k, "") for k in meta_keys},
                   **{k: v for k, v in r.items() if k != "energy"}}
            for d in domains:
                row[f"energy_{d}_j"] = r["energy"].get(d)
            rows.append((row, r))
            status = "TIMEOUT" if r["timed_out"] else f"exit {r['exit_code']}"
            main = domains[0] if domains else None
            e = f", {r['energy'][main]:.2f} J ({main})" if main else ""
            print(f"[{i}/{len(schedule)}] {job['id']} rep {rep}: "
                  f"{r['wall_s']:.2f} s{e}, {r['maxrss_mb']:.0f} MB, {status}")
            time.sleep(args.cooldown)

        print(f"Idle baseline ({args.idle} s) ...")
        idle_after = measure_idle(reader, args.idle)
        idle = {d: (idle_before.get(d, 0) + idle_after.get(d, 0)) / 2 for d in domains}
        for row, r in rows:
            for d in domains:
                row[f"net_energy_{d}_j"] = r["energy"][d] - idle[d] * r["wall_s"]
            writer.writerow(row)

    meta = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform_info(),
        "energy_reader": reader.name,
        "energy_reader_note": note,
        "idle_power_w_before": idle_before,
        "idle_power_w_after": idle_after,
        "args": vars(args),
        "python": sys.version,
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    if hasattr(reader, "close"):
        reader.close()
    print(f"Wrote {out} and {out.with_suffix('.json')}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reader", default="auto",
                        choices=["auto", "rapl", "pmic", "powermetrics", "none"])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="show platform info and energy reader status")
    run = sub.add_parser("run", help="measure all jobs of a jobs file")
    run.add_argument("jobs")
    run.add_argument("--out", required=True, help="CSV output path")
    run.add_argument("--reps", type=int, default=10)
    run.add_argument("--warmup", type=int, default=1, help="unrecorded runs per job")
    run.add_argument("--idle", type=float, default=30, help="idle baseline seconds")
    run.add_argument("--cooldown", type=float, default=5, help="seconds between runs")
    run.add_argument("--timeout", type=float, default=600)
    run.add_argument("--seed", type=int, default=20261025)
    run.add_argument("--cpus", help="pin programs to these CPUs, e.g. 2,3 (Linux only)")
    run.add_argument("--allow-no-energy", action="store_true")
    args = parser.parse_args()
    {"check": cmd_check, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    main()
