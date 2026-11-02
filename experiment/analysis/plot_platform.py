"""Figures for the platform measurements (paper, Section Results).

    analysis/.venv/bin/python analysis/plot_platform.py laptop mac

Reads results/<name>/runs.csv for each platform and writes to paper/figures/:
  <first>_languages.pdf  median energy per task and language (generated programs)
  llms.pdf               energy of each generated program relative to the median of all
                         generated programs for the same task and language, per LLM;
                         one panel per platform
  platforms.pdf          program energy on the second vs. the first platform
Energy per program is the median of its repetitions (gross energy of the domain in
ENERGY: RAPL package on Linux, powermetrics CPU+GPU+ANE estimate on the Mac).
"""
from __future__ import annotations

import csv
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT.parent / "paper" / "figures"
ENERGY = {"laptop": "energy_package-0_j", "server": "energy_package-0_j",
          "mac": "energy_combined_j", "pi": "energy_board_j"}
TITLE = {"laptop": "Laptop (x86-64)", "server": "Server (x86-64)", "mac": "Mac (Arm64)",
         "pi": "Raspberry Pi 5 (Arm64)"}

# Categorical slots validated for colour-vision deficiency; shapes as second channel.
LLM_STYLE = {"claude": ("Claude", "#2a78d6", "o"), "codex": ("GPT", "#eb6834", "s"),
             "gemini": ("Gemini", "#1baf7a", "^")}
LANG_STYLE = {"cpp": ("C++", "#008300", "o"), "java": ("Java", "#e87ba4", "s"),
              "python": ("Python", "#eda100", "^")}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"

plt.rcParams.update({
    "font.family": "serif", "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 7.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "text.color": INK, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42,
})


def load(name: str) -> dict[str, dict]:
    rows = list(csv.DictReader(open(ROOT / "results" / name / "runs.csv")))
    progs: dict[str, dict] = {}
    for r in rows:
        p = progs.setdefault(r["program_id"], {"llm": r["llm"], "task": r["task"],
                                               "lang": r["lang"], "e": []})
        p["e"].append(float(r[ENERGY[name]]))
    for p in progs.values():
        p["energy"] = st.median(p["e"])
    return {k: v for k, v in progs.items() if v["llm"] != "reference"}


def joules(x, _pos) -> str:
    return f"{x:g}"


def style_axis(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_axisbelow(True)


def fig_languages(progs: dict, out: Path) -> None:
    cell = defaultdict(list)
    for p in progs.values():
        cell[(p["task"], p["lang"])].append(p["energy"])
    med = {k: st.median(v) for k, v in cell.items()}
    tasks = sorted({t for t, _ in med}, key=lambda t: med[(t, "cpp")])
    fig, ax = plt.subplots(figsize=(3.45, 2.9))
    style_axis(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    for y, t in enumerate(tasks):
        vals = [med[(t, l)] for l in LANG_STYLE]
        ax.plot([min(vals), max(vals)], [y, y], color=GRID, linewidth=2, zorder=1,
                solid_capstyle="round")
        for lang, (label, color, marker) in LANG_STYLE.items():
            ax.scatter(med[(t, lang)], y, s=26, color=color, marker=marker, zorder=3,
                       edgecolor="white", linewidth=0.8, label=label if y == 0 else None)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(joules))
    ax.set_yticks(range(len(tasks)), tasks)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Package energy per run (J, log scale)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncols=3, frameon=False,
              handletextpad=0.2, columnspacing=1.0, borderaxespad=0.1)
    fig.tight_layout(pad=0.3)
    fig.savefig(out)
    plt.close(fig)


def fig_llms(platforms: dict[str, dict], out: Path) -> None:
    n = len(platforms)
    fig, axes = plt.subplots(n, 1, figsize=(3.45, 0.4 + 1.75 * n), sharex=True,
                             squeeze=False)
    width = 0.26
    for ax, (name, progs) in zip(axes[:, 0], platforms.items()):
        cell = defaultdict(list)
        for p in progs.values():
            cell[(p["task"], p["lang"])].append(p["energy"])
        base = {k: st.median(v) for k, v in cell.items()}
        style_axis(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.axhline(1, color=MUTED, linewidth=0.7, zorder=1)
        for g, lang in enumerate(LANG_STYLE):
            for k, (llm, (label, color, marker)) in enumerate(LLM_STYLE.items()):
                x0 = g + (k - 1) * width
                vals = [p["energy"] / base[(p["task"], lang)] for p in progs.values()
                        if p["llm"] == llm and p["lang"] == lang]
                jitter = [x0 + ((i * 0.618) % 1 - 0.5) * width * 0.7
                          for i in range(len(vals))]
                ax.scatter(jitter, vals, s=5, color=color, alpha=0.35, linewidth=0,
                           zorder=2)
                gm = math.exp(st.mean(math.log(v) for v in vals))
                ax.scatter(x0, gm, s=34, color=color, marker=marker, edgecolor=INK,
                           linewidth=0.7, zorder=4,
                           label=label if g == 0 and ax is axes[0, 0] else None)
        ax.set_yscale("log")
        ax.set_ylim(0.1, 1000)
        ax.yaxis.set_major_formatter(FuncFormatter(joules))
        ax.set_ylabel("Rel. to task median")
        ax.text(0.01, 0.97, TITLE.get(name, name), transform=ax.transAxes, va="top",
                fontsize=7, color=INK)
    axes[-1, 0].set_xticks(range(3), [LANG_STYLE[l][0] for l in LANG_STYLE])
    axes[-1, 0].tick_params(axis="x", length=0)
    axes[0, 0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=3,
                      frameon=False, handletextpad=0.1, columnspacing=1.0,
                      borderaxespad=0.1)
    fig.tight_layout(pad=0.3, h_pad=0.6)
    fig.savefig(out)
    plt.close(fig)


def fig_platforms(a: tuple[str, dict], b: tuple[str, dict], out: Path) -> None:
    (na, pa), (nb, pb) = a, b
    common = [k for k in pa if k in pb]
    fig, ax = plt.subplots(figsize=(3.45, 2.5))
    style_axis(ax)
    ax.grid(color=GRID, linewidth=0.5)
    lo = min(min(pa[k]["energy"], pb[k]["energy"]) for k in common) / 1.5
    hi = max(max(pa[k]["energy"], pb[k]["energy"]) for k in common) * 1.5
    for lang, (label, color, marker) in LANG_STYLE.items():
        ks = [k for k in common if pa[k]["lang"] == lang]
        ax.scatter([pa[k]["energy"] for k in ks], [pb[k]["energy"] for k in ks], s=9,
                   color=color, marker=marker, alpha=0.6, linewidth=0, zorder=3,
                   label=label)
    r = st.correlation([math.log(pa[k]["energy"]) for k in common],
                       [math.log(pb[k]["energy"]) for k in common])
    ax.text(0.03, 0.95, f"$r={r:.3f}$ (log), $n={len(common)}$", transform=ax.transAxes,
            va="top", fontsize=7)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.xaxis.set_major_formatter(FuncFormatter(joules))
    ax.yaxis.set_major_formatter(FuncFormatter(joules))
    ax.set_xlabel(f"{TITLE.get(na, na)}: energy per run (J)")
    ax.set_ylabel(f"{TITLE.get(nb, nb)}: energy per run (J)")
    ax.legend(loc="lower right", frameon=False, handletextpad=0.1, borderaxespad=0.2,
              markerscale=1.6)
    fig.tight_layout(pad=0.3)
    fig.savefig(out)
    plt.close(fig)


def main() -> None:
    names = sys.argv[1:] or ["laptop"]
    FIGS.mkdir(parents=True, exist_ok=True)
    platforms = {n: load(n) for n in names}
    fig_languages(platforms[names[0]], FIGS / f"{names[0]}_languages.pdf")
    fig_llms(platforms, FIGS / "llms.pdf")
    if len(names) > 1:
        fig_platforms(*list(platforms.items())[:2], FIGS / "platforms.pdf")
    print(f"Wrote figures to {FIGS} for", {n: len(p) for n, p in platforms.items()})


if __name__ == "__main__":
    main()
