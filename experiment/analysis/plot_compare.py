"""Comparison figures for LLMs and languages (paper, Section Results).

    analysis/.venv/bin/python analysis/plot_compare.py laptop mac

Writes to paper/figures/:
  languages_literature.pdf  energy of Java and Python relative to C++: our generated code,
                            our EffiBench-X reference solutions, and Pereira et al. (2017)
  llm_heatmap.pdf           geometric mean of program energy relative to the task--language
                            median, per LLM x language x platform
  llm_tasks.pdf             per task: median energy of each LLM's five samples relative to
                            the task--language median, one panel per language and platform
Style, colours, and the energy domain per platform come from plot_platform.py.
"""
from __future__ import annotations

import csv
import math
import statistics as st
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.ticker import FuncFormatter

from plot_platform import (ENERGY, FIGS, GRID, INK, LANG_STYLE, LLM_STYLE, MUTED, ROOT,
                           TITLE, joules, style_axis)

# Pereira et al., SLE 2017 (doi:10.1145/3136014.3136031): Table 4 (normalised energy over
# ten CLBG benchmarks, C = 1) and Table 3 (energy in J per benchmark).
PEREIRA = {
    "all": {"cpp": 1.34, "java": 1.98, "python": 75.88},
    "CLBG03": {"cpp": 41.23, "java": 111.84, "python": 1793.46},   # binary-trees
    "CLBG04": {"cpp": 219.89, "java": 311.38, "python": 12784.09},  # fannkuch-redux
}
TASK_NAME = {"CLBG03": "binary-trees", "CLBG04": "fannkuch-redux"}
# Diverging blue <-> red with a neutral grey midpoint at 1 (the task median).
DIVERGING = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])


def gm(xs) -> float:
    return math.exp(st.mean(math.log(x) for x in xs))


def load_all(name: str) -> dict[str, dict]:
    progs: dict[str, dict] = {}
    for r in csv.DictReader(open(ROOT / "results" / name / "runs.csv")):
        p = progs.setdefault(r["program_id"], {"llm": r["llm"], "task": r["task"],
                                               "lang": r["lang"], "e": []})
        p["e"].append(float(r[ENERGY[name]]))
    for p in progs.values():
        p["energy"] = st.median(p["e"])
    return progs


def cell_medians(progs: dict, reference: bool) -> dict[tuple[str, str], float]:
    cell = defaultdict(list)
    for p in progs.values():
        if (p["llm"] == "reference") == reference:
            cell[(p["task"], p["lang"])].append(p["energy"])
    return {k: st.median(v) for k, v in cell.items()}


def lang_factors(med: dict, tasks) -> dict[str, float]:
    tasks = [t for t in tasks if all((t, l) in med for l in LANG_STYLE)]
    return {l: gm(med[(t, l)] / med[(t, "cpp")] for t in tasks) for l in ("java", "python")}


def fig_literature(platforms: dict[str, dict], out) -> None:
    p_all = PEREIRA["all"]
    rows = [("Pereira et al.: 10 CLBG tasks", {l: p_all[l] / p_all["cpp"] for l in
                                                ("java", "python")}, "lit")]
    for t in ("CLBG03", "CLBG04"):
        rows.append((f"Pereira et al.: {TASK_NAME[t]}",
                     {l: PEREIRA[t][l] / PEREIRA[t]["cpp"] for l in ("java", "python")},
                     "lit"))
    for name, progs in platforms.items():
        gen, ref = cell_medians(progs, False), cell_medians(progs, True)
        tasks = sorted({t for t, _ in gen})
        short = name.capitalize()
        rows += [
            (f"{short}: 4 CLBG tasks", lang_factors(gen, [t for t in tasks if "CLBG" in t]),
             name),
            (f"{short}: {TASK_NAME['CLBG03']}", lang_factors(gen, ["CLBG03"]), name),
            (f"{short}: {TASK_NAME['CLBG04']}", lang_factors(gen, ["CLBG04"]), name),
            (f"{short}: 10 EB tasks", lang_factors(gen, [t for t in tasks if "EB" in t]),
             name),
            (f"{short}: 10 EB tasks, references", lang_factors(ref, tasks), name),
        ]
    fig, ax = plt.subplots(figsize=(3.45, 0.55 + 0.17 * len(rows)))
    style_axis(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.axvline(1, color=MUTED, linewidth=0.7, zorder=1)
    for y, (_label, f, _grp) in enumerate(rows):
        ax.plot([1, f["python"]], [y, y], color=GRID, linewidth=2, zorder=1,
                solid_capstyle="round")
        for lang in ("java", "python"):
            label, color, marker = LANG_STYLE[lang]
            ax.scatter(f[lang], y, s=24, color=color, marker=marker, zorder=3,
                       edgecolor="white", linewidth=0.7, label=label if y == 0 else None)
    for y in (2.5, 7.5):
        ax.axhline(y, color=MUTED, linewidth=0.4, linestyle=":")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(joules))
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Energy relative to C++ (log scale)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.35, 1.0), ncols=2, frameon=False,
              handletextpad=0.2, columnspacing=1.0, borderaxespad=0.1)
    fig.tight_layout(pad=0.3)
    fig.savefig(out)
    plt.close(fig)


def llm_ratios(progs: dict) -> dict[tuple[str, str, str], list[float]]:
    """(llm, task, lang) -> energies of its samples relative to the task--language median."""
    base = cell_medians(progs, False)
    out = defaultdict(list)
    for p in progs.values():
        if p["llm"] != "reference":
            out[(p["llm"], p["task"], p["lang"])].append(
                p["energy"] / base[(p["task"], p["lang"])])
    return out


def fig_heatmap(platforms: dict[str, dict], out) -> None:
    cols = [(n, l) for n in platforms for l in (*LANG_STYLE, "all")]
    llms = list(LLM_STYLE)
    vals = []
    for llm in llms:
        row = []
        for name, lang in cols:
            r = llm_ratios(platforms[name])
            row.append(gm(x for (m, _t, l), xs in r.items() if m == llm
                          and (lang == "all" or l == lang) for x in xs))
        vals.append(row)
    fig, ax = plt.subplots(figsize=(3.45, 1.35))
    ax.imshow(vals, cmap=DIVERGING, norm=LogNorm(vmin=0.5, vmax=2), aspect="auto")
    for i, row in enumerate(vals):
        for j, v in enumerate(row):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5, color=INK,
                    fontweight="bold" if v == min(r[j] for r in vals) else "normal")
    ax.set_yticks(range(len(llms)), [LLM_STYLE[m][0] for m in llms])
    ax.set_xticks(range(len(cols)),
                  [LANG_STYLE[l][0] if l in LANG_STYLE else "All" for _n, l in cols])
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    per = len(LANG_STYLE) + 1
    for k, name in enumerate(platforms):
        ax.text(k * per + (per - 1) / 2, -0.75, TITLE.get(name, name), ha="center",
                va="bottom", fontsize=7)
        if k:
            ax.axvline(k * per - 0.5, color="white", linewidth=3)
    fig.tight_layout(pad=0.3)
    fig.savefig(out)
    plt.close(fig)


def fig_tasks(platforms: dict[str, dict], out) -> None:
    tasks = sorted({p["task"] for p in next(iter(platforms.values())).values()},
                   key=lambda t: (t.startswith("CLBG"), t))
    panels = [(n, l) for n in platforms for l in LANG_STYLE]
    fig, axes = plt.subplots(1, len(panels), figsize=(7.16, 2.95), sharey=True,
                             sharex=True)
    for ax, (name, lang) in zip(axes, panels):
        r = llm_ratios(platforms[name])
        style_axis(ax)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.axvline(1, color=MUTED, linewidth=0.7, zorder=1)
        for y, t in enumerate(tasks):
            meds = {m: st.median(r[(m, t, lang)]) for m in LLM_STYLE if (m, t, lang) in r}
            if meds:
                ax.plot([min(meds.values()), max(meds.values())], [y, y], color=GRID,
                        linewidth=1.6, zorder=1)
            for m, (label, color, marker) in LLM_STYLE.items():
                if m in meds:
                    ax.scatter(meds[m], y, s=16, color=color, marker=marker, zorder=3,
                               edgecolor="white", linewidth=0.5,
                               label=label if y == 0 and ax is axes[0] else None)
        ax.set_xscale("log")
        ax.set_xlim(0.03, 600)
        ax.set_xticks([0.1, 1, 10, 100])
        ax.xaxis.set_major_formatter(FuncFormatter(joules))
        ax.set_title(f"{LANG_STYLE[lang][0]}, {name.capitalize()}", fontsize=7, pad=3)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    axes[0].set_yticks(range(len(tasks)), tasks)
    axes[0].invert_yaxis()
    fig.supxlabel("Median energy of the LLM's five samples relative to the task median "
                  "(log scale)", fontsize=7.5, y=0.02)
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncols=3, frameon=False,
               handletextpad=0.1, columnspacing=1.2)
    fig.tight_layout(pad=0.3, rect=(0, 0.03, 1, 0.91), w_pad=0.4)
    fig.savefig(out)
    plt.close(fig)


def main() -> None:
    names = sys.argv[1:] or ["laptop"]
    FIGS.mkdir(parents=True, exist_ok=True)
    platforms = {n: load_all(n) for n in names}
    gen = {n: {k: p for k, p in v.items() if p["llm"] != "reference"}
           for n, v in platforms.items()}
    fig_literature(platforms, FIGS / "languages_literature.pdf")
    fig_heatmap(gen, FIGS / "llm_heatmap.pdf")
    fig_tasks(gen, FIGS / "llm_tasks.pdf")
    print(f"Wrote languages_literature.pdf, llm_heatmap.pdf, llm_tasks.pdf to {FIGS}")


if __name__ == "__main__":
    main()
