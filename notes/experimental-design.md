# Experimentdesign (Entwurf v1)

Stand: 2026-10-25. Rahmenbedingungen: kein Raspberry Pi vorhanden, kein externes Messgerät,
Server noch unklar, LLM-Zugang über einen Mix aus API und Open-Weight-Modellen.

> Alles hier ist ein **Vorschlag**. Was als *Entscheidung* markiert ist, sollte vor der
> Datenerhebung fixiert und idealerweise präregistriert werden (z. B. auf OSF).

---

## 1. Faktoren und Umfang

| Faktor | Stufen | Typ |
|---|---|---|
| LLM (via offizielles CLI) | 3 | fest |
| Sprache | Python, Java, C++ | fest |
| Plattform | Desktop-PC, Server, Raspberry Pi 5 | fest |
| Aufgabe | 14 | zufällig (Random Effect) |
| Sample | k = 5 Generierungen pro Aufgabe × LLM × Sprache | zufällig (genestet) |

**Umfang:** 3 × 3 × 14 × 5 = **630 generierte Programme**. Jedes korrekte Programm wird auf
3 Plattformen mit je 10 Wiederholungen gemessen, das sind bis zu 18 900 Messungen.

**Zeitabschätzung (wird im Pilot kalibriert):** etwa 5 s pro Messung plus Cool-down ergeben etwa
35–50 h pro x86-Plattform und auf dem Raspberry Pi etwa 2–4× so viel. Machbar, aber sorgfältig
automatisieren.

---

## 2. LLM-Auswahl und Zugang (v4: offizielle Coding-CLIs)

### Entscheidung
Wir testen die **drei verbreitetsten kommerziellen KI-Assistenten**, und zwar jeweils über ihr
**offizielles Kommandozeilen-Werkzeug (CLI)** und die vorhandenen Pro-Abos. Dadurch entstehen
keine API-Kosten.

| # | Anbieter | CLI | Modell (bei Installation festlegen und loggen) | Zugang |
|---|---|---|---|---|
| 1 | Anthropic | Claude Code | Claude Opus 5.5 (`claude-opus-5-5`) | Claude-Pro-Abo |
| 2 | OpenAI | Codex CLI | Flaggschiff-Modell, das Codex für das Abo anbietet (z. B. `gpt-6.1-sol`; prüfen!) | ChatGPT-Abo |
| 3 | Google | ~~Gemini CLI~~ → **Antigravity CLI** (`agy`), siehe Protokoll F17 | `gemini-4-argon-medium` (B14) | Google-Konto / Google AI Pro |

**Framing im Paper:** Wir messen nicht das „nackte“ Modell, sondern das Modell **so, wie
Entwickler es über das offizielle Coding-Werkzeug des Anbieters nutzen** (hohe ökologische
Validität). Das wird in Setup und Threats to Validity offen beschrieben.

### Kimi K3 und DeepSeek-V4.1: gestrichen
- Für sie gibt es keinen gleichwertigen Zugang über ein offizielles Abo-CLI. Über eine API
  liefen sie unter anderen Bedingungen (kein Agenten-System-Prompt, keine Werkzeuge), damit
  wäre der Faktor „LLM“ mit dem Faktor „Zugangsweg“ vermischt.
- Kostenlos sind sie nur unzuverlässig verfügbar (OpenRouter-Gratisvarianten mit Tageslimits,
  wechselnde Verfügbarkeit).
- Im Paper kommen Open-Weight-Modelle als **Future Work** vor.

**Konsequenz:** Der Faktor LLM hat 3 Stufen. Für RQ4 (Rangstabilität) heißt das: Es gibt nur
3! = 6 mögliche Rangfolgen. Die Analyse bleibt sinnvoll („wechselt der Sieger?“), primär
stützt sich RQ4 aber auf die Interaktionsterme im Mixed Model.

### Generierungsprotokoll (für alle drei gleich)
Grundsatz: **System-Prompt des Werkzeugs bleibt unverändert („as shipped“)**, aber
**keine Werkzeugnutzung und kein Projektkontext**.

| Regel | Umsetzung |
|---|---|
| Leeres Arbeitsverzeichnis pro Anfrage | neues temporäres Verzeichnis, keine CLAUDE.md, AGENTS.md oder GEMINI.md |
| Keine Benutzer-Konfiguration | Claude: `--setting-sources ""`, `--strict-mcp-config`; Codex: `--ignore-user-config`; Gemini: isoliertes Settings-Verzeichnis |
| Keine Werkzeuge | Claude: `--tools ""` (offiziell dokumentiert); Gemini: `tools.exclude` bzw. `tools.core` in Settings; Codex: kein dokumentierter Schalter, daher `--sandbox read-only` im leeren Verzeichnis |
| Werkzeug-Kontrolle | JSON-Logs jeder Anfrage auswerten: Hat das Werkzeug trotzdem Tools aufgerufen? Das wird pro Anfrage protokolliert und berichtet |
| Keine Sitzungs-Historie | jede Anfrage neu (Claude `--no-session-persistence`, Codex `--ephemeral`) |
| Modell fest | Claude `--model claude-opus-5-5`, Codex `-m <id>`, Gemini `-m <id>`; tatsächliches Modell aus JSON-Log übernehmen |
| Sampling | Default des Werkzeugs, nicht verändert, geloggt |
| Reasoning-Effort | **einheitlich „medium“** (Protokoll B13) |
| Ausgabe | JSON bzw. stream-JSON (Claude `--output-format json`, Codex `--json -o`, Gemini `-o stream-json`) |
| Versionen | CLI-Version (`--version`) und Datum jeder Anfrage loggen; CLI-Versionen während der Erhebung **nicht** aktualisieren |
| Prompt | identischer Prompt-Text (siehe §5), über stdin bzw. `-p` |

> ⚠️ Die genauen Flags für Codex und Gemini (Werkzeuge abschalten, Settings isolieren) sind
> **noch zu verifizieren**, sobald die CLIs installiert sind. Für Claude Code sind sie in der
> offiziellen CLI-Referenz dokumentiert.

### Weitere Punkte
- **Nutzungslimits der Abos:** 210 Anfragen pro Werkzeug, auf mehrere Tage verteilen und
  Pausen einplanen.
- **Nutzungsbedingungen:** Nicht-interaktive Nutzung ist bei allen drei eine offizielle
  Funktion. Trotzdem kurz die Abo-Bedingungen prüfen.
- **Interessenkonflikt:** Der Assistent, der beim Paper hilft, gehört zur Claude-Familie.
  Claude darf im Paper weder bevorzugt noch benachteiligt werden.
- **Keine Nachbearbeitung** außer dem automatischen Extrahieren des Codeblocks. Kompiliert ein
  Programm nicht oder ist es falsch, zählt es als Fehlschlag.

---

## 3. Aufgaben (Benchmark)

### Entscheidung: Hybrid aus EffiBench-X und CLBG (14 Aufgaben)

**A) 10 Aufgaben aus EffiBench-X** (Qing et al. 2025, Apache 2.0)
- Vorteile: Py/Java/C++-Referenzlösungen vorhanden, Testgeneratoren mit Stresstests,
  sprachneutrale serialisierte Ein- und Ausgabe, Aufgaben überwiegend nach Oktober 2023
  (geringeres Kontaminationsrisiko als bei klassischem LeetCode).
- Auswahl **stratifiziert nach Kategorie**:

| Kategorie (aus deinem Konzept) | Anzahl |
|---|---|
| Sortieren / Suchen | 2 |
| Mathematik / Zahlentheorie | 2 |
| String-Verarbeitung | 2 |
| Rekursion / dynamische Programmierung | 2 |
| Datenstrukturen (Graph, Heap, Baum) | 2 |

- Nur **Standard-I/O-Aufgaben** (vollständiges Programm, liest von stdin und schreibt auf stdout),
  damit für alle Sprachen derselbe Harness gilt und kein sprachspezifischer Testrahmen die
  Messung verfälscht.
- Die Auswahl erfolgt zufällig innerhalb der Kategorie, mit festem Seed. Das ist dokumentierbar
  und vermeidet Rosinenpickerei.

**B) 4 Aufgaben aus dem Computer Language Benchmarks Game** (CLBG)
- `n-body`, `spectral-norm`, `binary-trees`, `fannkuch-redux`
- Vorteile: CPU- und speicherintensiv, Eingabegröße frei skalierbar, **direkte Anknüpfung an
  Pereira et al.** (Brücke zu RQ2/RQ5), etablierte Referenzlösungen.
- Nachteil: hohe Kontamination, weil die Lösungen weit verbreitet sind. Das wird als Threat
  diskutiert. Man kann es aber auch als Kontrollbedingung lesen: „bekannte“ vs. „neuere“ Aufgaben.

### Workload-Kalibrierung (Entscheidung)
- **Eine feste Eingabe pro Aufgabe**, identisch über alle LLMs, Sprachen und Plattformen.
  Das ist Voraussetzung für RQ3.
- Die Eingabegröße wird im Pilot so gewählt, dass die **C++-Referenzlösung auf dem Server
  mindestens etwa 1 s** läuft. Damit liegen auch die schnellsten Läufe deutlich über der
  RAPL-Auflösung.
- Programme, die auf dem Raspberry Pi länger als ein Timeout (z. B. 10 min) brauchen, werden als
  Timeout erfasst und nicht verworfen.
- **Gemessen wird der gesamte Prozess**, inklusive Interpreter- bzw. JVM-Start. Begründung: Wir
  messen „das Programm ausführen“, wie es ein Nutzer täte. Der JVM-Start ist eine Eigenschaft der
  Sprache, kein Messartefakt. Als Nebenanalyse kann man den Leerlauf eines „Hello World“ pro
  Sprache abziehen.

### Korrektheit
- Jede Lösung wird gegen alle Tests (EffiBench-X: 100 generierte Tests; CLBG: Referenzausgabe)
  geprüft.
- **Primäre Energieanalyse:** nur korrekte Lösungen.
- **Für RQ4 (Rangfolgen)** braucht man vollständige Zellen. Ranking-Analysen laufen daher auf
  Aufgaben, für die jedes LLM in jeder Sprache mindestens eine korrekte Lösung hat. Eine
  Sensitivitätsanalyse auf allen Daten mit dem Mixed Model ergänzt das, denn das Modell kommt mit
  fehlenden Zellen zurecht.

---

## 4. Plattformen und Energiemessung

### Grundproblem
Ohne externes Messgerät messen die Plattformen **unterschiedliche Dinge**:
- x86 mit **RAPL**: CPU-Package (+ DRAM bei Intel), *ohne* Mainboard, Netzteil und Lüfter
- Raspberry Pi 5 mit **PMIC-ADCs**: die Eingangsleistung der Platine *ohne* 5-V-Peripherie

**Entscheidung:** Absolute Joule werden **nicht** über Plattformen hinweg verglichen. RQ3 und RQ4
werden über **relative Größen** beantwortet: Rangfolgen der LLMs, Verhältnisse zur
Referenzlösung und normalisierte Energie innerhalb jeder Plattform. Das passt ohnehin genau zu
RQ4, und die Formulierung von RQ3 wird entsprechend angepasst.

### Pro Plattform

| | Desktop-PC | Server | Raspberry Pi 5 |
|---|---|---|---|
| Hardware | **TBD** (welche CPU hast du?) | **TBD**, muss Bare-Metal sein | **beschaffen:** RPi 5, 8 GB (~90 €) + offizielles 27-W-Netzteil + aktiver Kühler |
| Messwerkzeug | `perf stat -e power/energy-pkg/,power/energy-ram/` (RAPL) | wie PC | `vcgencmd pmic_read_adc`, Summe der Strom- × Spannungs-Kanäle, mit ~10 Hz gepollt |
| Erfasst | Package (+ DRAM, nur Intel) | Package + DRAM | Board-Eingang ohne 5-V-Peripherie |
| Hinweis | Bei **AMD** misst RAPL kein DRAM, nur Package | | Headless betreiben, keine USB-Geräte, Ethernet statt WLAN |

### Server-Optionen (zu klären)
1. **Physischer Uni- oder Firmenserver mit Root-Zugang**: beste Option
2. **Grid'5000** (Frankreich): Bare-Metal-Testbed für die Forschung, viele Knoten mit **externen
   Wattmetern**. Für Forschende in Europa beantragbar.
3. **Bare-Metal-Cloud** (z. B. AWS `*.metal`; EffiBench-X lief auf `i7ie.metal`): Ob RAPL
   lesbar ist, muss vorher geprüft werden. Kostet Geld.
4. ❌ **Normale Cloud-VM**: kein RAPL, deshalb ungeeignet.

### Dringende Empfehlung: einmalig ~50 € für ein USB-C-Messgerät mit PC-Logging
Ein USB-C-Leistungsmessgerät mit Datenlogging (Klasse FNIRSI FNB58 o. ä.) zwischen Netzteil und
Raspberry Pi würde
- die PMIC-Werte **kalibrieren** (die Community berichtet von systematischer Unterschätzung mit
  linearer Korrektur, das muss für das eigene Gerät geprüft werden),
- den größten Validitätseinwand der Gutachter entkräften. Das SLR kritisiert genau den Mangel an
  Hardware-Messung.

Optional dazu eine **WLAN-Steckdose mit Leistungsmessung** (~20 €, 1 Hz) für Desktop und Server.
Sie erfasst das Gesamtsystem bei langen Läufen grob und hilft, RAPL zu plausibilisieren.

### Kontrollierte Bedingungen (Entscheidung, auf allen Plattformen)
- CPU-Governor `performance`, Turbo bzw. Boost **aus** (soweit möglich). Grund: weniger Varianz.
- Prozess per `taskset` auf feste Kerne pinnen. Die Programme sind laut Prompt single-threaded.
- Minimales System: keine GUI, keine Cronjobs, kein Swap, Netzwerk nur fürs Logging.
- **Idle-Baseline**: vor jedem Block 60 s Leerlauf messen. Berichtet werden Brutto- und
  Netto-Energie.
- **Reihenfolge randomisiert** über LLM × Sprache × Aufgabe, damit Drift (Temperatur, Hintergrund)
  nicht mit den Faktoren konfundiert.
- **Cool-down** von etwa 10 s zwischen Läufen; die CPU-Temperatur wird mitgeloggt.
- **10 Wiederholungen** pro Programm und Plattform.

### Software-Umgebung (Entscheidung)
Auf **allen drei Plattformen identische, versionsgepinnte Multi-Arch-Docker-Images** (amd64 und
arm64):

| Sprache | Image (Vorschlag, exakte Digest-Pins bei Setup) | Flags |
|---|---|---|
| Python | `python:3.14-slim` | — |
| Java | `eclipse-temurin:25-jdk` (LTS) | Default-JVM-Flags |
| C++ | `gcc:14` | `-O2 -std=c++20`, **ohne** Sanitizer (EffiBench-X nutzt ASan, das verfälscht Energiewerte) |

So werden die Versionsunterschiede vermieden, die Apsan et al. hatten (Python 3.8/3.11/3.12).
Docker verursacht bei CPU-gebundenen Programmen kaum Overhead; RAPL misst ohnehin das ganze
Package.

### Weitere Messgrößen
- **Laufzeit**: Wall-Clock-Zeit (monotone Uhr) des Prozesses
- **Speicher**: Peak-RSS über `/usr/bin/time -v` bzw. cgroup `memory.peak`
- **CPU-Auslastung**: über `perf stat` (task-clock), optional

---

## 5. Prompt-Template (Entwurf)

```
You are given a programming task. Write a complete, self-contained {LANGUAGE} program
that solves it.

Requirements:
- Read the input from standard input and write the output to standard output, exactly
  in the format described below.
- Use only the {LANGUAGE} standard library.
- The program must be single-threaded.
- {LANGUAGE_SPECIFIC}
- Return only the source code in a single fenced code block.

Task:
{TASK_DESCRIPTION}

Input format:
{INPUT_FORMAT}

Output format:
{OUTPUT_FORMAT}

Example:
{EXAMPLE_IO}
```

`{LANGUAGE_SPECIFIC}` ist die einzige erlaubte sprachspezifische Zeile:
- Python: „Target Python 3.14.“
- Java: „Target Java 25. The public class must be named `Main`.“
- C++: „Target C++20. It will be compiled with `g++ -O2 -std=c++20`.“

**Bewusst nicht im Prompt:** „efficient“, „fast“, „energy“. Wir messen das Standardverhalten.
Ein Hinweis auf `-O2` ist eine neutrale Information, keine Optimierungsaufforderung.

---

## 6. Ablauf / Pipeline

```
1. Aufgaben auswählen (Seed)  →  tasks/
2. Generieren (3 CLIs × 3 Sprachen × 14 Aufgaben × k=5)  →  generated/  (+ raw logs)
3. Korrektheit prüfen (Docker, alle Tests)  →  correctness.csv
4. Pilot: Eingabegrößen kalibrieren, Messrauschen schätzen (→ Wiederholungen bestätigen)
5. Messung je Plattform (randomisiert, 10 Wdh.)  →  measurements_<platform>.csv
6. Auswertung (R: lme4/lmerTest, ARTool; oder Python: statsmodels)  →  figures/, tables/
```

Der **Pilot** (Schritt 4) sollte mit 2 LLMs × 3 Sprachen × 3 Aufgaben laufen, bevor die Hardware
fertig konfiguriert ist. So lassen sich Variationskoeffizient und Laufzeiten abschätzen, und
k sowie die Zahl der Wiederholungen können begründet werden (Power-Überlegung).

---

## 7. Anpassung der Forschungsfragen

- **RQ3** neu: „How does the *relative* energy efficiency of generated code (and the ranking of
  LLMs) differ across a desktop PC, a server, and a Raspberry Pi?“ Absolute Werte werden pro
  Plattform berichtet und nicht direkt verglichen (unterschiedliche Messgrenzen).

---

## 8. Offene Entscheidungen (von dir)

- [x] **Laptop/Desktop**: Intel i7-1185G7 (Laptop), RAPL verfügbar
- [ ] **Server**: Uni bzw. Firma, Grid'5000 oder Bare-Metal-Cloud?
- [ ] **Raspberry Pi 5 (8 GB)** beschaffen
- [ ] **USB-C-Messgerät** (~50 €) zur Kalibrierung: ja oder nein?
- [ ] CLIs installieren (Claude Code, Codex CLI, Antigravity CLI), Flags verifizieren, Modell-IDs festhalten
- [ ] Abo-Nutzungsbedingungen kurz prüfen

---

## Änderungen v2 (2026-10-25)

- **LLMs festgelegt:** Claude Opus 5.5, GPT-6 Astra, Gemini Pro (aktuelle stabile Version), Kimi K3,
  DeepSeek-V4.1 (Qwen3.8-27B in v3 gestrichen). Die exakten IDs werden am Tag der Generierung eingetragen.
- **EffiBench-X: Funktions- statt stdio-Format.** Die 285 stdio-Aufgaben haben keine Kategorie-Tags,
  eine stratifizierte Auswahl wäre nicht nachvollziehbar gewesen. Die Funktionsaufgaben (LeetCode)
  haben Tags und einen gemeinsamen I/O-Harness pro Sprache, sodass alle LLMs denselben I/O-Code
  nutzen. Das ist fairer als selbst geschriebenes I/O.
- **Auswahl:** 5 Kategorien × {Medium, Hard}, Seed 20261025, Pool aus 244 Aufgaben
  (`experiment/scripts/select_tasks.py`).
- **CLBG:** n-body, spectral-norm, binary-trees, fannkuch-redux. Spezifikationen in eigenen Worten,
  verifiziert gegen die offiziellen Referenzausgaben.
- **Prompt-Fix:** Prompts werden aus dem HTML erzeugt, weil `description_md` im Datensatz die
  Exponenten verliert (10^5 wird zu „105“).
- **Kontamination:** Die EB-Aufgaben stammen von 11/2023 bis 10/2024 und liegen damit vor allen
  Modell-Cutoffs. Das ist in den Threats to Validity offen dokumentiert. Option: 2–3 Aufgaben ergänzen,
  die nach allen Cutoffs veröffentlicht wurden.

## Änderungen v3 (2026-10-25)

- **Nur noch 5 LLMs**: Qwen3.8-27B gestrichen. Es bleiben Claude Opus 5.5, GPT-6 Astra, Gemini Pro,
  Kimi K3 und DeepSeek-V4.1. Damit sind es 1 050 Programme. Das Kriterium „Größenklassen“ entfällt;
  alle fünf sind Frontier-Modelle.
- **Keine Temperatur** mehr: Anbieter-Defaults für alle (siehe oben).

### Kosten (API ist **nicht** in Pro-Abos enthalten) — *überholt durch v4, siehe unten*

ChatGPT Plus/Pro, Claude Pro und Google AI Pro (Gemini) sind **Chat-Abos**. Die APIs werden
separat nach Tokens abgerechnet (OpenAI Platform, Anthropic Console, Google AI Studio bzw. Vertex).

Grobe Rechnung pro Modell: 42 Prompts × 5 Samples = **210 Anfragen**, je ~0,8k Input-Tokens und
~2–8k Output-Tokens (inklusive Reasoning, das mitbezahlt wird).

| Modell | Preis (Input / Output pro 1 Mio. Tokens) | Schätzung für 210 Anfragen |
|---|---|---|
| Claude Opus 5.5 | 4 $ / 20 $ (Anthropic, Stand 10/2026) | ca. 10–35 $ |
| GPT-6 Astra | vor Start auf openai.com/api/pricing prüfen | vermutlich ähnliche Größenordnung |
| Gemini Pro | vor Start auf ai.google.dev/pricing prüfen | AI Studio hat ein kostenloses Kontingent (Achtung: Daten können dort zum Training genutzt werden) |
| Kimi K3, DeepSeek-V4.1 | über OpenRouter bzw. Anbieter-API | meist wenige Dollar |

**Gesamt: grob 30–100 $**, für Pilotläufe und Wiederholungen etwas Puffer einplanen.
Vor dem Start: Preise prüfen und ein **Ausgabenlimit** in jeder Konsole setzen.

**Warum nicht einfach die Chat-Oberflächen?** Dort fehlen feste Modellversionen, und es greifen
versteckte System-Prompts, „Memory“ und eigene Anweisungen. Dazu kämen rund 630 manuelle
Copy-&-Paste-Vorgänge. Für die Reproduzierbarkeit, die Gutachter verlangen, ist die API nötig.

## Änderungen v4 (2026-10-25)

- **Kostenloser Weg:** Generierung über Claude Code, Codex CLI und Gemini CLI mit den vorhandenen
  Abos (siehe §2). Es fallen **keine API-Kosten** an.
- **Kimi K3 und DeepSeek-V4.1 gestrichen**, damit es nur einen Zugangsweg gibt; Open-Weight-Modelle
  werden Future Work.
- **3 × 3 × 14 × 5 = 630 Programme.**
- **Plattform „Desktop-PC“:** Der vorhandene Rechner ist ein Laptop (Intel i7-1185G7, 8 Threads,
  32 GB). Im Paper heißt er dann „Laptop“. RAPL ist verfügbar.

## Änderungen v5 (2026-10-28): Ausführung auf den Plattformen

- **Ein Skript pro Plattform** (`experiment/bench/run_platform.py`): bauen → Korrektheit → messen → ZIP. Details und Begründungen im Entscheidungsprotokoll (C14–C16, D10, E10–E14).
- **Große Eingaben:** EB-Aufgaben bekommen eine eigene Eingabe an der Constraint-Obergrenze, die R-mal im selben Prozess gelöst wird; CLBG über N. Kalibriert auf dem Laptop: C++ ≈ 1 s, keine Referenz > 60 s.
- **Korrektheit:** 30 Generator-Tests (bzw. CLBG-Prüfausgabe) + große Eingabe, auf jeder Plattform.
- **Messung:** 3 Wiederholungen, 3 s Pause, Leerlauf alle 30 min, feste Zufallsreihenfolge, fortsetzbar.
- **Software-Umgebung:** native Installation (Python 3.14, Java 25, GCC 14) statt Docker, weil Mac- und Pi-Energie nur vom Host lesbar sind. Ersetzt den Abschnitt „Software-Umgebung (Entscheidung)“ oben.
- **Raspberry Pi:** Energie über PMIC (`vcgencmd pmic_read_adc`), Summe aller Schienen.
