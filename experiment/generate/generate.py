"""Generate code with Claude Code, Codex CLI and Antigravity CLI (Gemini) under identical conditions.

Usage:
    python3 generate.py setup                     # create isolated config dirs (homes/)
    python3 generate.py versions                  # show CLI versions as seen by the script
    python3 generate.py probe [--tools claude]    # one test request per tool (not study data)
    python3 generate.py run [--tools ...] [--tasks EB03] [--langs cpp] [--samples 1]
                            [--limit N] [--dry-run]
    python3 generate.py status

Protocol (see notes/entscheidungsprotokoll.md, section F):
  * every request is a new, non-interactive CLI invocation in a fresh, empty directory
    outside the project (no CLAUDE.md / AGENTS.md / GEMINI.md can be found)
  * every CLI uses its own config directory (homes/<tool>), so personal settings, memory
    and plugins of the user's normal installation are not used
  * the prompt is read from prompts/rendered/ and checked against its SHA-256
  * all (tool, task, language, sample) requests run in one fixed random order (plan.json)
  * technical failures (timeout, crash, empty answer) are retried; wrong code never is
  * on a rate/usage limit the tool is paused for the rest of the run; re-run to resume
  * raw output, extracted code and metadata are stored for every request
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
PROMPTS = EXPERIMENT / "prompts"
OUT = Path(os.environ.get("LLMGEN_OUT", EXPERIMENT / "generated"))  # override for tests
HOMES = Path(os.environ.get("LLMGEN_HOMES", HERE / "homes"))
CONFIG = json.loads(Path(os.environ.get("LLMGEN_CONFIG", HERE / "config.json")).read_text())
LANGUAGES = json.loads((PROMPTS / "languages.json").read_text())

FINAL_STATUSES = {"ok", "no_code"}  # requests that are never repeated
PROBE_PROMPT = (
    "This is a configuration check. Answer in plain text, without using any tools:\n"
    "1. Which model are you (name and version, if known)?\n"
    "2. Did you receive any instructions besides your built-in system prompt and this "
    "message, e.g. from CLAUDE.md, AGENTS.md, GEMINI.md, memory, or user settings? "
    "If yes, quote their first line.\n"
    "3. Do you have access to any tools in this session? List their names.\n"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- environment

def tool_env(tool: str) -> dict[str, str]:
    cfg = CONFIG["tools"][tool]
    env = dict(os.environ)
    env.update(cfg.get("env", {}))
    env[cfg["config_env"]] = str(HOMES / tool)
    env["NO_COLOR"] = "1"
    return env


def cmd_setup(args) -> None:
    for tool, cfg in CONFIG["tools"].items():
        home = HOMES / tool
        home.mkdir(parents=True, exist_ok=True)
        if "settings" in cfg:
            target = home / cfg.get("config_subdir", "") / cfg["settings_file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(cfg["settings"], indent=2) + "\n")
            print(f"{tool}: wrote {target}")
        print(f"{tool}: config dir {home}\n   login: {cfg['config_env']}={home} {cfg['cmd'][0]}")


def cli_versions(tools) -> dict[str, str]:
    versions = {}
    for tool in tools:
        cfg = CONFIG["tools"][tool]
        try:
            r = subprocess.run(cfg["version_cmd"], capture_output=True, text=True,
                               env=tool_env(tool), timeout=60)
            versions[tool] = (r.stdout or r.stderr).strip().splitlines()[0]
        except (OSError, subprocess.TimeoutExpired, IndexError) as e:
            versions[tool] = f"unavailable ({e.__class__.__name__})"
    return versions


def cmd_versions(args) -> None:
    for tool, v in cli_versions(args.tools).items():
        print(f"{tool:<7} {v}")


# --------------------------------------------------------------------------- parsing

def parse_claude_json(stdout: str, last_message: str | None) -> dict:
    data = json.loads(stdout)
    usage = data.get("usage") or {}
    models = list((data.get("modelUsage") or {}).keys())
    return {
        "text": data.get("result") or "",
        "reported_models": models,
        "is_error": bool(data.get("is_error")),
        "num_turns": data.get("num_turns"),
        "tool_calls": max(0, (data.get("num_turns") or 1) - 1),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "session_id": data.get("session_id"),
    }


def parse_codex_jsonl(stdout: str, last_message: str | None) -> dict:
    items, usage, texts, errors = Counter(), {}, [], []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get("type", "")
        if kind == "item.completed":
            item = event.get("item") or {}
            items[item.get("type", "?")] += 1
            if item.get("type") == "agent_message" and item.get("text"):
                texts.append(item["text"])
        elif kind == "turn.completed":
            usage = event.get("usage") or usage
        elif kind in ("turn.failed", "error"):
            errors.append(json.dumps(event)[:300])
    non_tool = {"agent_message", "reasoning", "plan_update", "todo_list"}
    return {
        "text": last_message if last_message else (texts[-1] if texts else ""),
        "reported_models": [],
        "is_error": bool(errors) and not texts,
        "item_types": dict(items),
        "tool_calls": sum(n for t, n in items.items() if t not in non_tool),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": usage.get("reasoning_output_tokens"),
        "errors": errors,
    }


def parse_agy_stream_json(stdout: str, last_message: str | None) -> dict:
    """Antigravity CLI (`agy -p --output-format stream-json`): init, step_update, result."""
    deltas, models, tools, result, available_tools = [], [], [], {}, None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get("event", "")
        body = event.get(kind) or {}
        if kind == "init":
            if body.get("model"):
                models.append(body["model"])
            available_tools = body.get("tools")
        elif kind == "step_update":
            step_type = body.get("step_type")
            if step_type == "agent_response" and body.get("text_delta"):
                deltas.append(body["text_delta"])
            elif step_type not in ("user_input", "agent_response") and body.get("state") == "DONE":
                # every other step type (run_command, view_file, ...) is a tool step
                info = body.get("tool_info") or {}
                tools.append(info.get("name") or step_type or "?")
        elif kind == "result":
            result = body
    usage = result.get("usage") or {}
    status = result.get("status")
    return {
        "text": result.get("response") or "".join(deltas),
        "reported_models": models,
        "is_error": status not in (None, "SUCCESS") or bool(result.get("error")),
        "agy_status": status,
        "num_turns": result.get("num_turns"),
        "tool_calls": len(tools),
        "tool_names": tools,
        "available_tools": available_tools,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": usage.get("thinking_tokens"),
        "error": result.get("error"),
    }


PARSERS = {"claude_json": parse_claude_json, "codex_jsonl": parse_codex_jsonl,
           "agy_stream_json": parse_agy_stream_json}

FENCE = re.compile(r"```[ \t]*([A-Za-z0-9_+#.-]*)[^\n]*\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> tuple[str | None, str | None, int]:
    """First fenced code block (as defined in the protocol), its tag, and block count."""
    blocks = FENCE.findall(text)
    if not blocks:
        return None, None, 0
    tag, code = blocks[0]
    return code.rstrip() + "\n", tag.lower() or None, len(blocks)


# --------------------------------------------------------------------------- one request

def build_cmd(tool: str, prompt: str, last_message_file: Path) -> list[str]:
    cfg = CONFIG["tools"][tool]
    values = {"model": cfg["model"], "effort": CONFIG["reasoning_effort"], "prompt": prompt,
              "last_message_file": str(last_message_file)}
    return [part.format(**values) if "{" in part else part for part in cfg["cmd"]]


def run_request(tool: str, prompt: str) -> dict:
    """Run one CLI request in a fresh temporary directory outside the project."""
    cfg = CONFIG["tools"][tool]
    workdir = Path(tempfile.mkdtemp(prefix=f"llmgen-{tool}-"))
    side = Path(tempfile.mkdtemp(prefix="llmgen-out-"))  # outside the workdir
    last_message_file = side / "last_message.txt"
    cmd = build_cmd(tool, prompt, last_message_file)
    started = now()
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=workdir, env=tool_env(tool), text=True,
                              input=prompt if cfg["stdin_prompt"] else "",
                              capture_output=True, timeout=CONFIG["timeout_s"])
        stdout, stderr, code, timed_out = proc.stdout, proc.stderr, proc.returncode, False
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        code, timed_out = None, True
    except FileNotFoundError:
        stdout, stderr, code, timed_out = "", f"command not found: {cmd[0]}", 127, False
    duration = time.monotonic() - t0
    last_message = last_message_file.read_text() if last_message_file.exists() else None
    leftovers = sorted(p.name for p in workdir.iterdir())
    shutil.rmtree(workdir, ignore_errors=True)
    shutil.rmtree(side, ignore_errors=True)

    parsed, parse_error = {}, None
    if stdout.strip():
        try:
            parsed = PARSERS[cfg["parser"]](stdout, last_message)
        except (ValueError, KeyError, TypeError) as e:
            parse_error = f"{e.__class__.__name__}: {e}"
    text = parsed.get("text", "")
    haystack = (stderr + "\n" + stdout[-2000:]).lower()
    rate_limited = any(p in haystack for p in CONFIG["rate_limit_patterns"])

    if text.strip() and not parsed.get("is_error"):
        status = "answered"
    elif rate_limited:
        status = "rate_limited"
    else:
        status = "technical_error"
    return {
        "status": status, "started_utc": started, "duration_s": round(duration, 2),
        "exit_code": code, "timed_out": timed_out, "parse_error": parse_error,
        "workdir_leftovers": leftovers, "stdout": stdout, "stderr": stderr,
        "text": text, "parsed": {k: v for k, v in parsed.items() if k != "text"},
        "cmd": [c if c != prompt else "<prompt>" for c in cmd],
    }


# --------------------------------------------------------------------------- plan / run

def load_prompts() -> dict[tuple[str, str], dict]:
    index = json.loads((PROMPTS / "rendered" / "index.json").read_text())
    return {(e["task_id"], e["language"]): e for e in index}


def load_plan() -> list[dict]:
    plan_file = OUT / "plan.json"
    if plan_file.exists():
        return json.loads(plan_file.read_text())["requests"]
    prompts = load_prompts()
    requests = [{"tool": tool, "task": task, "lang": lang, "sample": s}
                for tool in CONFIG["tools"] for (task, lang) in sorted(prompts)
                for s in range(1, CONFIG["samples"] + 1)]
    random.Random(CONFIG["seed"]).shuffle(requests)
    for i, r in enumerate(requests, 1):
        r["order"] = i
    OUT.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(json.dumps({"created_utc": now(), "seed": CONFIG["seed"],
                                     "samples": CONFIG["samples"],
                                     "requests": requests}, indent=1) + "\n")
    print(f"Created plan with {len(requests)} requests (seed {CONFIG['seed']}).")
    return requests


def request_dir(r: dict) -> Path:
    return OUT / r["tool"] / r["task"] / r["lang"] / f"s{r['sample']}"


def current_status(r: dict) -> str | None:
    meta = request_dir(r) / "meta.json"
    return json.loads(meta.read_text())["status"] if meta.exists() else None


def read_prompt(entry: dict) -> str:
    prompt = (EXPERIMENT / entry["path"]).read_text()
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    if digest != entry["sha256"]:
        sys.exit(f"Prompt {entry['path']} does not match its SHA-256 in index.json. "
                 "Prompts must not change during data collection.")
    return prompt


def save(r: dict, entry: dict, result: dict, attempts: list[dict], versions: dict) -> str:
    d = request_dir(r)
    d.mkdir(parents=True, exist_ok=True)
    (d / "stdout.raw").write_text(result["stdout"])
    (d / "stderr.txt").write_text(result["stderr"])
    (d / "response.md").write_text(result["text"])
    status = result["status"]
    code_info = {}
    if status == "answered":
        code, tag, n_blocks = extract_code(result["text"])
        if code is None:
            status = "no_code"
        else:
            status = "ok"
            ext = LANGUAGES[r["lang"]]["ext"]
            (d / f"code.{ext}").write_text(code)
            code_info = {"code_file": f"code.{ext}", "fence_tag": tag,
                         "code_blocks": n_blocks, "code_sha256":
                             hashlib.sha256(code.encode()).hexdigest()}
    cfg = CONFIG["tools"][r["tool"]]
    meta = {
        **{k: r[k] for k in ("tool", "task", "lang", "sample", "order")},
        "status": status, "cli": cfg["cli"], "cli_version": versions.get(r["tool"]),
        "configured_model": cfg["model"],
        "reasoning_effort": CONFIG["reasoning_effort"],
        "reported_models": result["parsed"].get("reported_models"),
        "prompt_path": entry["path"], "prompt_sha256": entry["sha256"],
        **code_info,
        "tool_calls": result["parsed"].get("tool_calls"),
        "workdir_leftovers": result["workdir_leftovers"],
        "parsed": result["parsed"], "parse_error": result["parse_error"],
        "attempts": attempts,
    }
    (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return status


def append_log(row: dict) -> None:
    log = OUT / "requests_log.csv"
    new = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def cmd_run(args) -> None:
    for tool in args.tools:
        if not CONFIG["tools"][tool]["model"]:
            sys.exit(f"No model configured for '{tool}' in config.json (set it after "
                     "checking which models the CLI offers).")
    prompts = load_prompts()
    plan = [r for r in load_plan()
            if r["tool"] in args.tools
            and (not args.tasks or r["task"] in args.tasks)
            and (not args.langs or r["lang"] in args.langs)
            and r["sample"] <= args.samples]
    todo = [r for r in plan if current_status(r) not in FINAL_STATUSES]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(plan)} requests selected, {len(plan) - len(todo)} already done, "
          f"{len(todo)} to run.")
    if args.dry_run:
        for r in todo[:10]:
            print(r["order"], r["tool"], r["task"], r["lang"], f"s{r['sample']}",
                  " ".join(build_cmd(r["tool"], "<prompt>", Path("<last_message>"))))
        return
    versions = cli_versions(args.tools)
    session = {"started_utc": now(), "versions": versions, "args": vars(args)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"session_{datetime.now():%Y%m%d_%H%M%S}.json").write_text(
        json.dumps(session, indent=2) + "\n")
    paused: set[str] = set()
    for n, r in enumerate(todo, 1):
        if r["tool"] in paused:
            continue
        entry = prompts[(r["task"], r["lang"])]
        prompt = read_prompt(entry)
        attempts = []
        for attempt in range(CONFIG["max_technical_retries"] + 1):
            result = run_request(r["tool"], prompt)
            attempts.append({k: result[k] for k in ("status", "started_utc", "duration_s",
                                                     "exit_code", "timed_out")})
            if result["status"] != "technical_error" or attempt == CONFIG["max_technical_retries"]:
                break
            wait = CONFIG["retry_backoff_s"][min(attempt, len(CONFIG["retry_backoff_s"]) - 1)]
            print(f"   technical error, retrying in {wait} s")
            time.sleep(wait)
        status = save(r, entry, result, attempts, versions)
        append_log({"logged_utc": now(), "order": r["order"], "tool": r["tool"],
                    "task": r["task"], "lang": r["lang"], "sample": r["sample"],
                    "status": status, "attempts": len(attempts),
                    "duration_s": result["duration_s"],
                    "tool_calls": result["parsed"].get("tool_calls"),
                    "reported_models": ";".join(result["parsed"].get("reported_models") or [])})
        print(f"[{n}/{len(todo)}] #{r['order']} {r['tool']:<6} {r['task']:<6} "
              f"{r['lang']:<6} s{r['sample']}: {status} ({result['duration_s']} s)")
        if status == "rate_limited":
            paused.add(r["tool"])
            print(f"   {r['tool']} hit a usage limit: paused for this run. "
                  "Run the same command again later to continue.")
        time.sleep(CONFIG["pause_s"])
    if paused:
        print("Paused tools:", ", ".join(sorted(paused)))


def cmd_status(args) -> None:
    counts: dict[str, Counter] = {}
    for r in load_plan():
        counts.setdefault(r["tool"], Counter())[current_status(r) or "open"] += 1
    for tool, c in counts.items():
        total = sum(c.values())
        print(f"{tool:<7} " + ", ".join(f"{k}: {v}" for k, v in sorted(c.items()))
              + f"  (total {total})")


def cmd_probe(args) -> None:
    probe_dir = OUT / "_probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    for tool in args.tools:
        if not CONFIG["tools"][tool]["model"]:
            print(f"{tool}: no model configured, skipped")
            continue
        result = run_request(tool, PROBE_PROMPT)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        (probe_dir / f"{tool}_{stamp}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"===== {tool}: {result['status']} ({result['duration_s']} s), "
              f"models={result['parsed'].get('reported_models')}, "
              f"tool_calls={result['parsed'].get('tool_calls')}, "
              f"leftovers={result['workdir_leftovers']}")
        print(result["text"].strip()[:1500] or result["stderr"].strip()[:1500])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    tools = list(CONFIG["tools"])
    for name in ("setup", "versions", "probe", "run", "status"):
        p = sub.add_parser(name)
        if name in ("versions", "probe", "run"):
            p.add_argument("--tools", nargs="+", choices=tools, default=tools)
        if name == "run":
            p.add_argument("--tasks", nargs="+")
            p.add_argument("--langs", nargs="+", choices=list(LANGUAGES))
            p.add_argument("--samples", type=int, default=CONFIG["samples"],
                           help="only samples 1..N (e.g. 1 for a pilot)")
            p.add_argument("--limit", type=int, help="run at most N requests")
            p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    {"setup": cmd_setup, "versions": cmd_versions, "probe": cmd_probe,
     "run": cmd_run, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    main()
