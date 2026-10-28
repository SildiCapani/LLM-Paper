"""Turn a generated (or reference) solution into a runnable program.

EffiBench-X tasks ("function" format): the submission is inserted into the task's
language-specific runner (tasks/EBxx/runner/), which reads one input from stdin, calls the
Solution method and prints the result. We add
  * the standard import preamble the runners rely on ("auto-injected imports"), and
  * a repetition wrapper: the program takes R as its first argument and executes the
    runner's main R times on the same stdin in one process, printing only the last
    output. This lifts sub-millisecond calls to a measurable duration without changing
    the harness logic. Each repetition creates a new Solution object.

CLBG tasks ("program" format): the submission is a complete program that takes N as its
first command-line argument; it is used unchanged.

build(...) writes the sources to a directory, compiles them if needed and returns the
command prefix to run the program (append R or N).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

MARKER = "==Code Submission=="

PREAMBLE = {
    "python": ("import sys, os, io, re, math, string, random, heapq, bisect, itertools, "
               "functools, operator, collections\n"
               "from typing import *\n"
               "from collections import *\n"
               "from itertools import *\n"
               "from functools import *\n"
               "from heapq import *\n"
               "from bisect import *\n"),
    "java": ["import java.util.*;", "import java.util.function.*;",
             "import java.util.stream.*;", "import java.io.*;", "import java.math.*;"],
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n",
}

PY_WRAPPER = '''import io, os, sys
_R = int(sys.argv[1]) if len(sys.argv) > 1 else 1
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "body.py"), encoding="utf-8") as _f:
    _CODE = compile(_f.read(), "body.py", "exec")
_DATA = sys.stdin.read()
_REAL = sys.stdout
_last = ""
for _i in range(_R):
    sys.stdin = io.StringIO(_DATA)
    _buf = io.StringIO()
    sys.stdout = _buf
    exec(_CODE, {"__name__": "__main__", "__builtins__": __builtins__})
    _last = _buf.getvalue()
sys.stdout = _REAL
sys.stdout.write(_last)
sys.stdout.flush()
'''

JAVA_WRAPPER = '''
public class Main {
    public static void main(String[] args) throws Exception {
        int r = args.length > 0 ? Integer.parseInt(args[0]) : 1;
        byte[] data = System.in.readAllBytes();
        java.io.PrintStream real = System.out;
        byte[] last = new byte[0];
        for (int i = 0; i < r; i++) {
            System.setIn(new java.io.ByteArrayInputStream(data));
            java.io.ByteArrayOutputStream buf = new java.io.ByteArrayOutputStream();
            System.setOut(new java.io.PrintStream(buf, false));
            EbMain.main(new String[0]);
            System.out.flush();
            last = buf.toByteArray();
        }
        System.setOut(real);
        real.write(last);
        real.flush();
    }
}
'''

CPP_WRAPPER = '''
int main(int argc, char** argv) {
    std::ios_base::sync_with_stdio(false);
    int r = argc > 1 ? std::atoi(argv[1]) : 1;
    std::string data((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
    std::streambuf* cin0 = std::cin.rdbuf();
    std::streambuf* cout0 = std::cout.rdbuf();
    std::string last;
    for (int i = 0; i < r; i++) {
        std::istringstream in(data);
        std::ostringstream out;
        std::cin.rdbuf(in.rdbuf());
        std::cin.clear();
        std::cout.rdbuf(out.rdbuf());
        eb_main();
        std::cout.flush();
        last = out.str();
    }
    std::cin.rdbuf(cin0);
    std::cout.rdbuf(cout0);
    std::cout << last;
    std::cout.flush();
    return 0;
}
'''

JAVA_IMPORT = re.compile(r"^\s*import\s+(static\s+)?[\w.]+(\.\*)?\s*;\s*$")
JAVA_PACKAGE = re.compile(r"^\s*package\s+[\w.]+\s*;\s*$")
JAVA_PUBLIC_TOP = re.compile(r"^public\s+((?:final\s+|abstract\s+)*(?:class|interface|record|enum)\b)")
CPP_MAIN = re.compile(r"\bint\s+main\s*\(\s*(void)?\s*\)")
CPP_SYNC = re.compile(r"(std::)?ios(_base)?::sync_with_stdio\s*\(\s*(false|0)\s*\)\s*;")


def insert_submission(runner: str, code: str) -> str:
    """Replace the first marker line with the code and drop further marker lines."""
    out, done = [], False
    for line in runner.splitlines():
        if line.strip() == MARKER:
            if not done:
                out.append(code.rstrip("\n"))
                done = True
            continue
        out.append(line)
    if not done:
        raise ValueError("runner has no submission marker")
    return "\n".join(out) + "\n"


def _split_java_imports(src: str) -> tuple[list[str], str]:
    imports, rest = [], []
    for line in src.splitlines():
        if JAVA_IMPORT.match(line):
            imports.append(line.strip())
        elif JAVA_PACKAGE.match(line):
            continue
        else:
            rest.append(line)
    return imports, "\n".join(rest)


def eb_sources(lang: str, runner: str, code: str) -> dict[str, str]:
    """Source files for an EffiBench-X task (function format) with repetition wrapper."""
    if lang == "python":
        return {"body.py": PREAMBLE["python"] + insert_submission(runner, code),
                "prog.py": PY_WRAPPER}
    if lang == "java":
        sub_imports, sub = _split_java_imports(code)
        sub = "\n".join(JAVA_PUBLIC_TOP.sub(r"\1", l) for l in sub.splitlines())
        run_imports, run = _split_java_imports(runner)
        run = run.replace("public class Main", "class EbMain", 1)
        imports = list(dict.fromkeys(PREAMBLE["java"] + run_imports + sub_imports))
        return {"Main.java": "\n".join(imports) + "\n\n" + insert_submission(run, sub)
                + JAVA_WRAPPER}
    if lang == "cpp":
        run = CPP_SYNC.sub("", CPP_MAIN.sub("int eb_main()", runner, count=1))
        return {"prog.cpp": PREAMBLE["cpp"] + insert_submission(run, code) + CPP_WRAPPER}
    raise ValueError(lang)


def clbg_sources(lang: str, code: str) -> dict[str, str]:
    return {"python": {"prog.py": code}, "java": {"Main.java": code},
            "cpp": {"prog.cpp": code}}[lang]


def build(lang: str, sources: dict[str, str], out_dir: Path, tools: dict,
          timeout: float = 300) -> tuple[bool, list[str], str]:
    """Write and compile; return (ok, run command prefix, compiler message)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in sources.items():
        (out_dir / name).write_text(text, encoding="utf-8")
    if lang == "python":
        return True, [tools["python"], "-I", str(out_dir / "prog.py")], ""
    if lang == "java":
        cmd = [tools["javac"], "-encoding", "UTF-8", "-nowarn", "-d", str(out_dir),
               str(out_dir / "Main.java")]
        run = [tools["java"], "-cp", str(out_dir), "Main"]
    else:
        cmd = [tools["cxx"], "-O2", "-std=c++20", "-o", str(out_dir / "prog"),
               str(out_dir / "prog.cpp")]
        run = [str(out_dir / "prog")]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, run, "compiler timeout"
    return p.returncode == 0, run, (p.stdout + p.stderr)[-4000:]
