"""Render the final prompt for every task x language.

EffiBench-X tasks use prompts/template_function.txt; the problem text is converted from
the original HTML description (description_md in the dataset has lost superscripts,
e.g. 10^5 is rendered as "105"). CLBG tasks use prompts/template_program.txt with
tasks/<id>/spec.md.

Output: prompts/rendered/<task_id>/<language>.txt and prompts/rendered/index.json
(including a SHA-256 of every prompt for the replication package).
"""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
TASKS = ROOT / "tasks"


class HtmlToMarkdown(HTMLParser):
    """Minimal converter for LeetCode problem HTML."""

    BLOCK = {"p", "div", "ul", "ol", "pre", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.pre = 0
        self.lists: list[list] = []  # stack of [kind, counter]
        self.images = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.out.append("\n\n")
        if tag == "pre":
            self.pre += 1
            self.out.append("```\n")
        elif tag in ("strong", "b") and not self.pre:
            self.out.append("**")
        elif tag in ("em", "i") and not self.pre:
            self.out.append("*")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag == "sup":
            self.out.append("^")
        elif tag == "sub":
            self.out.append("_")
        elif tag == "br":
            self.out.append("\n")
        elif tag in ("ul", "ol"):
            self.lists.append([tag, 0])
        elif tag == "li":
            kind = self.lists[-1] if self.lists else ["ul", 0]
            kind[1] += 1
            bullet = f"{kind[1]}. " if kind[0] == "ol" else "- "
            self.out.append("\n" + "  " * (len(self.lists) - 1) + bullet)
        elif tag == "img":
            self.images += 1
            self.out.append("[image omitted]")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.pre -= 1
            self.out.append("\n```")
        elif tag in ("strong", "b") and not self.pre:
            self.out.append("**")
        elif tag in ("em", "i") and not self.pre:
            self.out.append("*")
        elif tag == "code" and not self.pre:
            self.out.append("`")
        elif tag in ("ul", "ol") and self.lists:
            self.lists.pop()
        if tag in self.BLOCK:
            self.out.append("\n\n")

    def handle_data(self, data):
        if not self.pre:
            data = re.sub(r"\s+", " ", data.replace("\xa0", " "))
        self.out.append(data)

    def markdown(self) -> str:
        text = "".join(self.out)
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)
        text = re.sub(r"\*\*[ \t]*\*\*", "", text)     # empty bold
        text = re.sub(r"\n (?=\S)", "\n", text)         # space left after <br>
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_markdown(html: str) -> tuple[str, int]:
    parser = HtmlToMarkdown()
    parser.feed(html)
    return parser.markdown(), parser.images


def effibench_html(task: dict) -> str:
    for line in (ROOT / "data" / "effibench_x_metadata.jsonl").open():
        row = json.loads(line)
        if row["id"] == task["effibench_id"] and row["title_slug"] == task["title_slug"]:
            return row["description"]
    raise KeyError(task["task_id"])


def main() -> None:
    languages = json.loads((PROMPTS / "languages.json").read_text())
    templates = {f: (PROMPTS / f"template_{f}.txt").read_text()
                 for f in ("function", "program")}
    index = []
    for task_dir in sorted(TASKS.iterdir()):
        task = json.loads((task_dir / "task.json").read_text())
        fmt = task.get("format", "function")
        images = 0
        if fmt == "function":
            problem, images = html_to_markdown(effibench_html(task))
        else:
            problem = (task_dir / "spec.md").read_text().strip()
        for lang, cfg in languages.items():
            fields = {
                "language": cfg["language"],
                "language_note": cfg[f"language_note_{fmt}"],
                "problem": problem,
                "fence": cfg["fence"],
            }
            if fmt == "function":
                starter = task_dir / "starter" / f"{cfg['effibench_key']}.{cfg['ext']}"
                fields["starter"] = starter.read_text().rstrip()
            prompt = templates[fmt].format(**fields)
            out = PROMPTS / "rendered" / task["task_id"] / f"{lang}.txt"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(prompt)
            index.append({
                "task_id": task["task_id"], "language": lang, "format": fmt,
                "path": str(out.relative_to(ROOT)),
                "sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "chars": len(prompt), "images_omitted": images,
            })
    (PROMPTS / "rendered" / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    for e in index:
        flag = f"  !! {e['images_omitted']} image(s) omitted" if e["images_omitted"] else ""
        print(f"{e['task_id']:<7} {e['language']:<7} {e['chars']:>6} chars{flag}")


if __name__ == "__main__":
    main()
