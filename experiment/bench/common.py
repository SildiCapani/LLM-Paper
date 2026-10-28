"""Shared helpers: paths, toolchain detection, running a process, output comparison."""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # experiment/ (or the unpacked bundle)
TASKS = ROOT / "tasks"
GENERATED = ROOT / "generated"
DATA = HERE / "data"
LANGS = ("python", "java", "cpp")
EXT = {"python": "py", "java": "java", "cpp": "cpp"}
REF_FILE = {"python": "python3.py", "java": "java.java", "cpp": "cpp.cpp"}

# Versions planned for all platforms (paper, Table "Hardware and software configuration").
PLANNED = {"python": "3.14", "java": "25", "cxx": "14"}


def _first(*names: str) -> str | None:
    for n in names:
        if n and shutil.which(n):
            return shutil.which(n)
    return None


def detect_tools(python: str | None = None, java_home: str | None = None,
                 cxx: str | None = None) -> dict:
    """Find interpreters/compilers (planned versions first) and record their versions."""
    java_home = java_home or os.environ.get("JAVA_HOME")
    jbin = Path(java_home, "bin") if java_home else None
    tools = {
        "python": python or _first("python3.14", "python3"),
        "java": str(jbin / "java") if jbin else _first("java"),
        "javac": str(jbin / "javac") if jbin else _first("javac"),
        "cxx": cxx or _first("g++-14", "g++-15", "g++-13", "g++"),
    }
    versions, warnings = {}, []
    for key, cmd in (("python", [tools["python"], "--version"]),
                     ("java", [tools["java"], "-version"]),
                     ("javac", [tools["javac"], "-version"]),
                     ("cxx", [tools["cxx"], "--version"])):
        if not tools[key] or not Path(tools[key]).exists():
            versions[key] = None
            warnings.append(f"{key} not found")
            continue
        p = subprocess.run(cmd, capture_output=True, text=True)
        versions[key] = (p.stdout + p.stderr).strip().splitlines()[0]
    if versions.get("cxx") and "clang" in versions["cxx"].lower():
        warnings.append("C++ compiler is clang, not GCC (on macOS: brew install gcc@14)")
    for key, want in (("python", PLANNED["python"]), ("java", PLANNED["java"]),
                      ("cxx", PLANNED["cxx"])):
        v = versions.get(key) or ""
        m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", v.split(")")[-1] if key == "cxx" else v)
        got = (f"{m.group(1)}.{m.group(2)}" if key == "python" else m.group(1)) if m else "?"
        if v and got != want:
            warnings.append(f"{key} version {got} differs from planned {want}")
    return {"paths": tools, "versions": versions, "warnings": warnings}


def run_proc(cmd: list[str], stdin: bytes | None, timeout: float,
             cwd: Path | None = None) -> dict:
    """Run a program (own process group), kill it after `timeout` seconds."""
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=cwd, start_new_session=True)
    try:
        out, err = proc.communicate(stdin or b"", timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        timed_out = True
    return {"rc": proc.returncode, "out": out, "err": err[-2000:],
            "wall_s": time.perf_counter() - t0, "timed_out": timed_out}


_EVALUATORS: dict[str, object] = {}


def evaluator(task: str):
    """The task's output comparison. EB: dataset evaluator.py (reviewed, pure string and
    number comparison); CLBG: exact text match ignoring trailing whitespace."""
    if task not in _EVALUATORS:
        path = TASKS / task / "evaluator.py"
        if path.exists():
            ns: dict = {}
            exec(compile(path.read_text(), str(path), "exec"), ns)
            _EVALUATORS[task] = ns["evaluate"]
        else:
            def norm(s: str) -> str:
                return "\n".join(l.rstrip() for l in s.strip().splitlines())
            _EVALUATORS[task] = lambda exp, got: norm(exp) == norm(got)
    return _EVALUATORS[task]


def task_ids() -> list[str]:
    return sorted(p.name for p in TASKS.iterdir() if (p / "task.json").exists())


def task_format(task: str) -> str:
    return json.loads((TASKS / task / "task.json").read_text())["format"]


def load_manifest() -> dict:
    return json.loads((DATA / "manifest.json").read_text())
