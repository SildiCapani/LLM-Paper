# LLM-Paper: Projektübersicht

**Energy Efficiency of LLM-Generated Code: A Cross-Language and Cross-Platform Empirical Study**
Autoren: Brisild Capani, Seyyid

Diese Datei ist der **Einstieg ins Projekt**. Sie zeigt, was in welchem Ordner liegt, wie die
Teile zusammenhängen und wo die ausführlichere Doku zu finden ist.

---

## Worum geht es?

Wir untersuchen, wie **energieeffizient der Code ist, den KI-Assistenten schreiben**, und zwar
abhängig von

- dem **KI-Assistenten**: Claude, ChatGPT, Gemini (über ihre offiziellen Kommandozeilen-Tools)
- der **Programmiersprache**: Python, Java, C++
- der **Hardware**: Laptop, Server, Raspberry Pi bzw. Mac (noch in Klärung)

Die Kernfrage ist **RQ4**: *Bleibt die Rangfolge der KI-Assistenten gleich, oder hängt sie von
Sprache und Hardware ab?*

---

## Ordnerstruktur

```
LLM-Paper/
├── README.md                ← diese Datei (Übersicht)
├── CLAUDE.md                ← Arbeitsregeln für Claude in diesem Projekt
├── .gitignore               ← was Git ignoriert (LaTeX-Hilfsdateien, .venv …)
│
├── paper/                   ← das wissenschaftliche Paper (LaTeX)
│   ├── main.tex             ← Hauptdatei: Titel, Autoren, bindet alle Kapitel ein
│   ├── sections/            ← ein Kapitel pro Datei (00-abstract … 11-appendix)
│   ├── references.bib       ← Literaturliste (alle Einträge geprüft)
│   ├── IEEEtran.cls/.bst    ← IEEE-Layout (zweispaltig) und Zitierstil
│   ├── figures/, tables/    ← Platz für Abbildungen und Tabellen (noch leer)
│   └── build/main.pdf       ← das fertige PDF (beim Kompilieren erzeugt)
│
├── notes/                   ← Arbeitsnotizen (Deutsch), Grundlage für das Paper
│   ├── entscheidungsprotokoll.md ← ALLE Entscheidungen + Beobachtungen, mit Paper-Stelle
│   ├── literature-review.md ← Literaturrecherche + Begründung der Forschungslücke
│   └── experimental-design.md ← komplettes Experimentdesign mit allen Entscheidungen
│
└── experiment/              ← alles für das Experiment (Daten, Prompts, Skripte)
    ├── ERKLAERUNG.md        ← ausführliche Erklärung dieses Ordners (Deutsch)
    ├── LAUFEN_UND_MESSEN.md ← Gesamtablauf: bauen, testen, messen auf allen Plattformen
    ├── README.md            ← technische Kurzanleitung (Englisch)
    ├── tasks/               ← die 14 Programmieraufgaben
    ├── prompts/             ← Prompt-Vorlagen + 42 fertige Prompts
    ├── data/                ← Metadaten des Benchmarks + Aufgabenauswahl
    ├── scripts/             ← Skripte, die Aufgaben und Prompts erzeugen
    ├── generate/            ← Generierungsskript für Claude Code, Codex CLI, Antigravity CLI
    │   ├── ANLEITUNG.md     ← Installation, Login, Pilot, Hauptlauf (Deutsch)
    │   ├── generate.py, config.json
    │   └── homes/           ← Login-Daten der CLIs (NIE in Git!)
    ├── generated/           ← generierter Code + Rohantworten (entsteht beim Lauf; nicht in Git)
    └── measure/             ← Messskript für Energie, Zeit und Speicher
        ├── ANLEITUNG.md     ← Schritt-für-Schritt-Anleitung zum Messen (Deutsch)
        ├── measure.py, energy.py, test_energy.py
        ├── jobs/            ← Listen von Programmen, die gemessen werden
        └── results/         ← Messergebnisse (CSV + JSON)
```

---

## Wie hängt alles zusammen?

```
 notes/literature-review.md ──► Forschungslücke ──► paper/sections/03-related-work.tex
 notes/experimental-design.md ─► Entscheidungen ──► paper/sections/05-…, 06-…

 experiment/tasks/  ──┐
                      ├─► experiment/prompts/rendered/  ──► Claude / ChatGPT / Gemini (CLIs)
 experiment/prompts/ ─┘        (42 Prompts)                        │
   template_*.txt ──────────────────────────► im Paper-Anhang     ▼
                                                           generierter Code   ⏳
                                                                   │
                                                       Korrektheit prüfen    ⏳
                                                                   │
                                          experiment/measure/ ─► Energie messen
                                                                   │
                                                           results/*.csv  ──► Statistik ⏳ ──► paper/sections/07-results.tex
```

**Wichtig:** Das Paper bindet die Prompt-Vorlagen **direkt** aus `experiment/prompts/` ein. Wenn
du dort etwas änderst, ändert sich der Anhang des Papers automatisch mit.

---

## Wo steht was? (Doku-Wegweiser)

| Ich will … | Datei |
|---|---|
| **beim Schreiben nichts vergessen**: jede Entscheidung mit Begründung und Paper-Stelle | [notes/entscheidungsprotokoll.md](notes/entscheidungsprotokoll.md) |
| verstehen, warum es dieses Paper braucht | [notes/literature-review.md](notes/literature-review.md) |
| wissen, wie das Experiment aufgebaut ist und warum | [notes/experimental-design.md](notes/experimental-design.md) |
| den Experiment-Ordner verstehen (Aufgaben, Prompts) | [experiment/ERKLAERUNG.md](experiment/ERKLAERUNG.md) |
| einen Prompt sehen, wie ihn die KI bekommt | [experiment/prompts/rendered/EB03/cpp.txt](experiment/prompts/rendered/EB03/cpp.txt) |
| Code generieren (CLIs installieren, anmelden, starten) | [experiment/generate/ANLEITUNG.md](experiment/generate/ANLEITUNG.md) |
| Code ausführen und messen auf allen Plattformen (Gesamtablauf) | [experiment/LAUFEN_UND_MESSEN.md](experiment/LAUFEN_UND_MESSEN.md) |
| Energie messen (Details zum Messskript) | [experiment/measure/ANLEITUNG.md](experiment/measure/ANLEITUNG.md) |
| das Paper lesen bzw. bearbeiten | [paper/main.tex](paper/main.tex) und [paper/sections/](paper/sections/) |

---

## Häufige Aufgaben

**Paper als PDF bauen:**

```bash
cd paper && latexmk -pdf main.tex
```

Das Ergebnis liegt in `paper/build/main.pdf`. In VS Code geht es auch mit der Erweiterung
„LaTeX Workshop“ (Speichern löst das Kompilieren aus).

**Prompts neu erzeugen** (z. B. nach einer Änderung an einer Vorlage):

```bash
python3 experiment/scripts/render_prompts.py
```

**Energie messen:** siehe [experiment/measure/ANLEITUNG.md](experiment/measure/ANLEITUNG.md).
Kurzform für Linux:

```bash
sudo chmod a+r /sys/class/powercap/intel-rapl:*/energy_uj
cd experiment/measure && python3 measure.py check
```

---

## Paper-Kapitel

| Datei | Kapitel | Stand |
|---|---|---|
| `00-abstract.tex` | Abstract | Entwurf, ohne Ergebnisse |
| `01-introduction.tex` | Introduction | Entwurf |
| `02-background.tex` | Background | nur TODOs |
| `03-related-work.tex` | Related Work | ✅ ausgearbeitet |
| `04-research-questions.tex` | Forschungsfragen + Hypothesen | ✅ ausgearbeitet |
| `05-experimental-setup.tex` | Setup (LLMs, Aufgaben, Hardware) | ✅ ausgearbeitet, Hardware teils `[TBD]` |
| `06-methodology.tex` | Methodik (Prompts, Messung, Statistik) | ✅ ausgearbeitet |
| `07-results.tex` | Ergebnisse | leer (nach dem Experiment) |
| `08-discussion.tex` | Diskussion | leer (nach dem Experiment) |
| `09-threats.tex` | Threats to Validity | großteils ausgearbeitet |
| `10-conclusion.tex` | Fazit + Future Work | Entwurf |
| `11-appendix-prompts.tex` | Anhang: Prompt-Vorlagen | ✅ fertig |

Rote `[TBD]`-Markierungen und orange TODO-Kästen im PDF zeigen offene Stellen. Am Ende des
PDFs steht eine Liste aller TODOs.

---

## Projektstand

| Schritt | Stand |
|---|---|
| Forschungsfrage, Literatur, Forschungslücke | ✅ fertig |
| Experimentdesign | ✅ fertig (Plattformen noch offen) |
| 14 Aufgaben ausgewählt und geprüft | ✅ fertig |
| 42 Prompts erzeugt | ✅ fertig |
| Messskript (Linux) | ✅ fertig, auf dem Laptop getestet |
| Messskript (Mac) | ⚠️ gebaut, noch nicht auf echtem Mac getestet |
| Generierungsskript | ✅ fertig, mit Attrappen getestet |
| CLIs installieren, Probe, Code generieren (630 Programme) | ⏳ offen |
| Korrektheit prüfen | ⏳ offen |
| Pilot: Eingabegrößen auf ca. 5 s pro Lauf kalibrieren | ⏳ offen |
| Hauptmessung auf allen Plattformen | ⏳ offen |
| Statistische Auswertung + Ergebnisse im Paper | ⏳ offen |

## Offene Entscheidungen

- [ ] **Plattformen:** Kommen Raspberry Pi und Server dazu? Der Mac M4 wäre die Alternative für ARM.
- [ ] Seyyids Nachname und die Affiliations für das Paper
- [ ] Deutscher Abstract zum Übersetzen
- [ ] Windows-PC: genaues Prozessormodell (nur falls Windows als Plattform genutzt wird)

---

## Hinweise

- Die Dateien `main.aux`, `main.log`, `main.synctex.gz` usw. direkt in `paper/` sind
  **Hilfsdateien von LaTeX**. Sie entstehen beim Kompilieren (z. B. durch VS Code), lassen sich
  jederzeit neu erzeugen und gehören nicht in Git.
- Messergebnisse in `experiment/measure/results/` sind **Rohdaten**. Sie werden nicht von Hand
  bearbeitet.
