# Literaturrecherche & Validierung der Forschungslücke

Stand: 2026-10-25

## 1. Suchprotokoll

**Quellen:** arXiv-API (Volltext-Abstracts), Web-Suche (Google-ähnlich), Crossref (DOI-Verifikation).
Noch **nicht** durchsucht: Scopus, IEEE Xplore, ACM DL, Google Scholar. Diese sollten vor der Einreichung
noch durchsucht werden, denn das SLR von Masthan Ali et al. zeigt, dass dort Workshop-Paper liegen, die
nicht auf arXiv stehen.

**Suchstrings (arXiv, Feld `abs`/`ti`):**

| # | Suchstring | Treffer (relevant) |
|---|---|---|
| 1 | `"energy" AND "LLM-generated code"` | 6 |
| 2 | `"energy efficiency" AND "code generation" AND "language model"` | ~8 |
| 3 | `"energy consumption" AND "code generated" AND LLM` | ~4 |
| 4 | `"energy" AND "generated code" AND "C++" AND Java` | 1 (Solovyeva) |
| 5 | `"energy" AND "hardware platforms" AND "generated code"` | 2 (Apsan, SLR) |
| 6 | `"energy" AND LLM AND code AND "interaction effect"` | **0** |
| 7 | Effizienz-Benchmarks (EffiBench, Mercury, ECCO, EvalPerf, COFFE) | 6 |
| 8 | `RAPL AND accuracy AND "energy measurement"` | 3 |

**Einschlusskriterium:** empirische Messung des Energieverbrauchs (oder der Laufzeit/des Speichers) von
LLM-generiertem Code bei der *Ausführung*.
**Ausschluss:** Energie der LLM-Inferenz bzw. des Trainings (z. B. GREEN-CODE, Green Prompting, ENERGY STAR),
GPU- bzw. HPC-Kernel-Generierung.

**Snowballing:** Ausgangspunkt waren die Referenzen im SLR (Masthan Ali et al. 2026).

## 2. Kernarbeiten im Detail (aus den Volltexten extrahiert)

| Studie | LLMs | Sprachen | Plattformen | Messung | Statistik | Interaktion getestet? |
|---|---|---|---|---|---|---|
| Solovyeva et al. 2025 (arXiv) | 3 (Copilot, GPT-4o, o1-mini) | Py, Java, C++ | MacBook M3, Intel i7 PC | powermetrics / RAPL (perf), nur CPU | Mann-Whitney U, Hedges' g, Spearman | Nein |
| Apsan et al. 2026 (**ICSE '26**) | 6 | nur Py | Xeon-Server, i9-PC, RPi (Cortex-A72) | EnergiBridge (5 Hz) / Monsoon (5 kHz) | ART-ANOVA (LLM × Prompt), Holm, Cliff's δ | Nur LLM × Prompt, **je Plattform getrennt** |
| Islam et al. 2025 (arXiv) | 20 | nur Py | 1 Xeon (Chameleon Cloud) | perf: pkg + RAM, Idle abgezogen | keine | Nein |
| Rekhi et al. 2026 (arXiv) | 10 | Py, C++ | 1 Intel-Cloud | perf: pkg + DRAM | keine (nur Mittelwerte) | Nein (qualitativ: „inkonsistent“) |
| Cursaru et al. 2024 (arXiv) | 1 (Code Llama) | C++, JS, Py | RPi | Monsoon (extern) | noch prüfen | noch prüfen |
| Cappendijk et al. 2025 (GREENS) | 5 | nur Py | 1 | perf | noch prüfen | Nein |
| Ashraf et al. 2025 (arXiv) | 5 (3 SLM + 2 LLM) | nur Py | Cloud | CodeCarbon | noch prüfen | Nein |

**Verwandt, aber ohne Energie:** EffiBench (NeurIPS '24), EffiBench-X (6 Sprachen inkl. Py/Java/C++),
EvalPerf, ENAMEL (ICLR '25), COFFE (FSE '25) messen nur Laufzeit bzw. Speicher auf einer Plattform.

**Sekundärstudie:** Masthan Ali et al. 2026, SLR mit 18 Primärstudien. Wichtige Aussagen:
- „Most studies evaluate generated code on a single hardware configuration“
- Nur wenige Studien messen direkt mit externer Hardware
- Ausdrückliche Forderung nach „cross-platform evaluations across CPUs, GPUs, edge devices“

## 3. Bewertung der Forschungslücke

**Ergebnis: Die Lücke ist bestätigt, aber enger als ursprünglich formuliert.**

| Behauptete Neuheit | Status | Begründung |
|---|---|---|
| Mehrere LLMs × mehrere Sprachen | ❌ nicht neu | Solovyeva (3 × 3), Rekhi (10 × 2) |
| Mehrere LLMs × heterogene Plattformen inkl. RPi | ❌ nicht neu | Apsan (6 × 3, nur Python) |
| **Sprachen × heterogene Plattformen (inkl. ARM) gleichzeitig** | ✅ **neu** | keine Studie gefunden |
| **Formaler Test der Interaktionen LLM × Sprache × Plattform** | ✅ **neu** | Suchstring #6 ergab 0 Treffer; alle Kernarbeiten haben keine Interaktionsterme |
| **Test der Rangstabilität der LLMs** | ✅ **neu** | Apsan *beobachtet* wechselnde Rangfolgen, testet sie aber nicht; Solovyeva korreliert nur Plattformen |

**Empfohlene Formulierung des Beitrags:** Nicht „die erste Studie zur Energie von LLM-Code über Sprachen und
Plattformen“, sondern:

> The first study to jointly vary LLM, programming language, and architecturally heterogeneous hardware platform
> in a full factorial design and to explicitly test their interaction effects and the stability of LLM
> efficiency rankings.

**Stärkstes Argument:** Apsan et al. (ICSE '26) berichten selbst, dass das effizienteste LLM je Plattform
wechselt (Server: Speechless CodeLlama, PC: Code Millenials, RPi: WizardCoder). Diese Beobachtung wurde aber
weder statistisch abgesichert noch auf andere Sprachen übertragen. Genau hier setzt RQ4 an.

## 4. Konsequenzen für das Studiendesign

1. **C++ mit `-O2` kompilieren** (Solovyeva verwendet `-O0`). Damit ist man realitätsnäher; optional ein
   Vergleich `-O0` vs. `-O2` als Nebenanalyse.
2. **Laufdauer kalibrieren:** Apsan kalibriert die Iterationszahl, sodass jeder Lauf etwa 3 min dauert.
   Das sollten wir übernehmen.
3. **Gleiche Laufzeitversionen auf allen Plattformen:** Apsan verwendet Python 3.8, 3.12 und 3.11 je nach
   Plattform. Das ist ein Störfaktor, den wir vermeiden können.
4. **Externe Messung möglichst auf allen Plattformen** (das SLR bemängelt den Mangel an Hardware-Messung).
   Mindestens auf dem RPi ist sie ohnehin nötig.
5. **Nur Aufgaben, die alle LLMs in allen Sprachen korrekt lösen**, für die Energieanalyse verwenden
   (Apsan und Rekhi gehen genauso vor). Die Korrektheit wird separat berichtet.
6. **Benchmark-Kandidaten:** EffiBench-X (bereits Py/Java/C++ mit Tests und Referenzlösungen), EvalPerf,
   EvoEval. Die Kontaminationsgefahr bei LeetCode-Aufgaben muss diskutiert werden.

## 5. Offene Punkte

- [ ] Scopus / IEEE Xplore / ACM DL mit denselben Suchstrings durchsuchen
- [ ] Cursaru et al. und Cappendijk et al.: Statistik und Plattform im Volltext prüfen
- [ ] Die Studie, die laut SLR auf „two platforms“ läuft, identifizieren
- [ ] Zitate zu ICT-Energieanteil und Verbreitung von AI-Assistenten für die Introduction finden
- [ ] Kurz vor der Einreichung: arXiv-Suche wiederholen (das Feld bewegt sich schnell; Rekhi et al. ist vom
      01.10.2026)
