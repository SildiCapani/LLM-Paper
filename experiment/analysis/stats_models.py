"""Statistical models for RQ1-RQ5 (paper, Section Results).

    analysis/.venv/bin/python analysis/stats_models.py laptop mac

One row per generated program and platform: median energy, time, and peak memory of its
repetitions (energy domain per platform as in plot_platform.py). Then
  - linear mixed models on log energy (fixed: LLM, language, platform and their
    interactions; random: intercept per task and per program nested in task), fitted by
    maximum likelihood; terms are tested with likelihood-ratio tests (hierarchical:
    main effects in the additive model, two-way terms in the two-way model, the three-way
    term in the full model); effects are reported as factors exp(beta) with 95% CIs,
  - the same for the data without task EB02 (sensitivity),
  - Kendall's W of the LLM ranking over the 42 task-language cells per platform, and
    the share of cells whose best LLM is the same on both platforms,
  - Spearman correlations between energy, time, and memory per platform (RQ5).
Prints a report and writes paper/tables/models.tex.
"""
from __future__ import annotations

import csv
import math
import statistics as st
import sys
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from plot_platform import ENERGY, ROOT

TABLES = ROOT.parent / "paper" / "tables"
LLM_NAME = {"claude": "Claude", "codex": "GPT", "gemini": "Gemini"}
LANG_NAME = {"cpp": "C++", "java": "Java", "python": "Python"}


def load(names: list[str]) -> pd.DataFrame:
    rows = []
    for name in names:
        runs = defaultdict(list)
        meta = {}
        for r in csv.DictReader(open(ROOT / "results" / name / "runs.csv")):
            if r["llm"] == "reference":
                continue
            runs[r["program_id"]].append((float(r[ENERGY[name]]), float(r["wall_s"]),
                                          float(r["maxrss_mb"])))
            meta[r["program_id"]] = (r["llm"], r["task"], r["lang"])
        for pid, v in runs.items():
            llm, task, lang = meta[pid]
            rows.append({"program": pid, "llm": llm, "task": task, "lang": lang,
                         "platform": name, "energy": st.median(x[0] for x in v),
                         "time": st.median(x[1] for x in v),
                         "memory": st.median(x[2] for x in v)})
    df = pd.DataFrame(rows)
    df["log_e"] = np.log(df["energy"])
    return df


FIXED = "C(llm, Treatment('codex')) + C(lang, Treatment('cpp')) + C(platform)"
TERMS = {"llm": "C(llm, Treatment('codex'))", "lang": "C(lang, Treatment('cpp'))",
         "platform": "C(platform)"}


def fit(df: pd.DataFrame, rhs: str):
    model = smf.mixedlm(f"log_e ~ {rhs}", df, groups="task", re_formula="1",
                        vc_formula={"program": "0 + C(program)"})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return model.fit(reml=False, method=["lbfgs", "powell"])


def lrt(full, reduced) -> tuple[float, int, float]:
    chi2 = 2 * (full.llf - reduced.llf)
    dof = len(full.fe_params) - len(reduced.fe_params)
    return chi2, dof, stats.chi2.sf(chi2, dof)


def models(df: pd.DataFrame) -> dict:
    t = TERMS
    add = fit(df, FIXED)
    res = {"additive": add, "tests": {}}
    for key, term in t.items():
        rest = " + ".join(v for k, v in t.items() if k != key)
        res["tests"][key] = lrt(add, fit(df, rest))
    pairs = {"llm:lang": (t["llm"], t["lang"]), "llm:platform": (t["llm"], t["platform"]),
             "lang:platform": (t["lang"], t["platform"])}
    two = " + ".join([FIXED] + [f"{a}:{b}" for a, b in pairs.values()])
    two_fit = fit(df, two)
    for key, (a, b) in pairs.items():
        reduced = " + ".join([FIXED] + [f"{x}:{y}" for k, (x, y) in pairs.items()
                                        if k != key])
        res["tests"][key] = lrt(two_fit, fit(df, reduced))
    three = fit(df, f"{t['llm']} * {t['lang']} * {t['platform']}")
    res["tests"]["llm:lang:platform"] = lrt(three, two_fit)
    return res


def factor(fitres, name: str) -> tuple[float, float, float]:
    b = fitres.fe_params[name]
    lo, hi = fitres.conf_int().loc[name]
    return math.exp(b), math.exp(lo), math.exp(hi)


def kendall_w(ranks: np.ndarray) -> float:
    """ranks: m raters (cells) x n objects (LLMs), no ties."""
    m, n = ranks.shape
    r = ranks.sum(axis=0)
    s = ((r - r.mean()) ** 2).sum()
    return 12 * s / (m ** 2 * (n ** 3 - n))


def rankings(df: pd.DataFrame) -> dict:
    out = {}
    best = {}
    for platform, d in df.groupby("platform"):
        med = d.groupby(["task", "lang", "llm"])["energy"].median().unstack("llm")
        med = med.dropna()
        ranks = med.rank(axis=1).to_numpy()
        out[platform] = (kendall_w(ranks), len(med),
                         med.idxmin(axis=1).value_counts().to_dict())
        best[platform] = med.idxmin(axis=1)
    if len(best) == 2:
        a, b = best.values()
        common = a.index.intersection(b.index)
        out["same_best"] = (int((a[common] == b[common]).sum()), len(common))
    return out


def spearman(df: pd.DataFrame) -> dict:
    out = {}
    for platform, d in df.groupby("platform"):
        out[platform] = {pair: stats.spearmanr(d[pair[0]], d[pair[1]]).statistic
                         for pair in (("energy", "time"), ("energy", "memory"),
                                      ("time", "memory"))}
    return out


def fmt_p(p: float) -> str:
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def write_table(res: dict, sens: dict) -> None:
    t = TERMS
    fits = [(res["additive"], res["tests"]), (sens["additive"], sens["tests"])]

    def eff(name: str) -> str:
        cells = []
        for fitres, _tests in fits:
            f, lo, hi = factor(fitres, name)
            cells.append(f"{f:.2f} & {lo:.2f}--{hi:.2f} &")
        return " & ".join(cells)

    def test(key: str) -> str:
        return " & ".join(f"& & {fmt_p(tests[key][2])}" for _f, tests in fits)

    rows = []
    for key, label, effects in [
        ("llm", "LLM (baseline GPT)", [(f"{t['llm']}[T.claude]", "Claude"),
                                       (f"{t['llm']}[T.gemini]", "Gemini")]),
        ("lang", "Language (baseline C++)", [(f"{t['lang']}[T.java]", "Java"),
                                             (f"{t['lang']}[T.python]", "Python")]),
    ]:
        rows.append(f"{label} & {test(key)} \\\\")
        rows += [f"\\quad {lab} & {eff(name)} \\\\" for name, lab in effects]
    rows.append("\\addlinespace")
    for key, label in [("llm:lang", "LLM $\\times$ language"),
                       ("llm:platform", "LLM $\\times$ platform"),
                       ("lang:platform", "Language $\\times$ platform"),
                       ("llm:lang:platform", "LLM $\\times$ language $\\times$ platform")]:
        rows.append(f"{label} & {test(key)} \\\\")
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "models.tex").write_text(
        "% Generated by experiment/analysis/stats_models.py -- do not edit by hand.\n"
        "\\begin{tabular}{@{}lcccccc@{}}\n\\toprule\n"
        "& \\multicolumn{3}{c}{All tasks} & \\multicolumn{3}{c}{Without EB02} \\\\\n"
        "\\cmidrule(lr){2-4}\\cmidrule(l){5-7}\n"
        "Term & Factor & 95\\% CI & $p$ & Factor & 95\\% CI & $p$ \\\\\n\\midrule\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def report(title: str, res: dict) -> None:
    print(f"== {title}")
    for key, (chi2, dof, p) in res["tests"].items():
        print(f"  LRT {key:<18} chi2={chi2:8.2f} df={dof} p={p:.4g}")
    add = res["additive"]
    for name in add.fe_params.index:
        if name != "Intercept":
            f, lo, hi = factor(add, name)
            print(f"  {name:<40} x{f:.3f} [{lo:.3f}, {hi:.3f}]")
    print(f"  variance: task={float(add.cov_re.iloc[0, 0]):.3f} "
          f"program={float(add.vcomp[0]):.3f} residual={add.scale:.3f}")


def main() -> None:
    names = sys.argv[1:] or ["laptop", "mac"]
    df = load(names)
    print(f"{len(df)} program x platform rows, {df['program'].nunique()} programs")
    res = models(df)
    report("all tasks", res)
    sens = models(df[df["task"] != "EB02"])
    report("without EB02", sens)
    for k, v in rankings(df).items():
        print(f"ranking {k}: {v}")
    for k, v in spearman(df).items():
        print(f"spearman {k}: " + ", ".join(f"{a}-{b} {r:.3f}" for (a, b), r in v.items()))
    write_table(res, sens)
    print(f"Wrote {TABLES / 'models.tex'}")


if __name__ == "__main__":
    main()
