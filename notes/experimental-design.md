# Experimentdesign (Entwurf v1)

Stand: 2026-10-25. Rahmenbedingungen: kein Raspberry Pi vorhanden, kein externes Messgerät,
Server noch unklar, LLM-Zugang über einen Mix aus API und Open-Weight-Modellen.

> Alles hier ist ein **Vorschlag**. Was als *Entscheidung* markiert ist, sollte vor der
> Datenerhebung fixiert und idealerweise präregistriert werden (z. B. auf OSF).

---

## 1. Faktoren und Umfang

| Faktor | Stufen | Typ |
|---|---|---|
| LLM | 6 | fest |
| Sprache | Python, Java, C++ | fest |
| Plattform | Desktop-PC, Server, Raspberry Pi 5 | fest |
| Aufgabe | 14 | zufällig (Random Effect) |
| Sample | k = 5 Generierungen pro Aufgabe × LLM × Sprache | zufällig (genestet) |

**Umfang:** 6 × 3 × 14 × 5 = **1 260 generierte Programme**. Jedes korrekte Programm wird auf
3 Plattformen mit je 10 Wiederholungen gemessen, das sind bis zu 37 800 Messungen.

**Zeitabschätzung (wird im Pilot kalibriert):** etwa 5 s pro Messung plus Cool-down ergeben etwa
35–50 h pro x86-Plattform und auf dem Raspberry Pi etwa 2–4× so viel. Machbar, aber sorgfältig
automatisieren.

---

## 2. LLM-Auswahl

### Auswahlkriterien (gehören so ins Paper)
1. **Diversität der Anbieter**: keine zwei Modelle desselben Herstellers in derselben Klasse.
2. **Proprietär vs. Open-Weight**: je zur Hälfte. Open-Weight-Modelle sind reproduzierbar, weil
   die Gewichte fixiert sind.
3. **Größenklassen**: Frontier-Modelle und kleine bzw. günstige Modelle. Damit lässt sich prüfen,
   ob Modellgröße mit Effizienz zusammenhängt (Ashraf et al. und Mehditabar et al. haben das schon
   angerissen).
4. **Feste Versionen**: Es werden nur Modelle mit datiertem Snapshot bzw. fester Versions-ID
   verwendet; die ID wird bei jeder Anfrage geloggt.
5. **Relevanz**: Die Modelle sind in der Praxis verbreitet und auf aktuellen Coding-Leaderboards
   vertreten.

### Vorschlag (Stand Oktober 2026, **Namen und IDs bei der Generierung verifizieren**)

| # | Klasse | Kandidat | Zugang |
|---|---|---|---|
| 1 | proprietär, Frontier | Claude Opus 5.5 (Anthropic) | API |
| 2 | proprietär, Frontier | GPT-6 Astra (OpenAI) | API |
| 3 | proprietär, Frontier | aktuelle Gemini-Pro-Version (Google) | API |
| 4 | Open-Weight, groß | Kimi K3 (Moonshot) *oder* DeepSeek-V4.1 | API (z. B. OpenRouter) |
| 5 | Open-Weight, groß | DeepSeek-V4.1 *oder* MiMo-V2.6-Pro | API |
| 6 | Open-Weight, klein | Qwen3.8-27B (Apache 2.0) | API oder lokal |

Quellen für die Kandidaten: aktuelle Coding-Leaderboards (llm-stats, BenchLM, whatllm; Oktober
2026). Diese Ranglisten sind uneinheitlich und dienen nur der Vorauswahl, nicht als
Qualitätsurteil.

**Hinweis zu Interessenkonflikten:** Das Modell, das dir hier hilft, gehört zur Claude-Familie.
Die Auswahl folgt den Kriterien oben. Claude sollte im Paper weder bevorzugt noch ausgeschlossen
werden.

### Generierungsparameter (Entscheidung)
- **Zero-Shot** mit standardisiertem Prompt (siehe §5), **keine** Hinweise auf Energie oder
  Effizienz. Wir messen das Standardverhalten; Prompting untersuchen schon Rekhi, Cappendijk und
  Apsan.
- **Temperatur**: 0.7 bei allen Modellen, die das erlauben. Reasoning-Modelle, die keine
  Temperatur zulassen, laufen mit Anbieter-Default; das wird dokumentiert.
  Begründung: k = 5 Samples sollen die *Verteilung* des Modellverhaltens abbilden; T = 0 ist
  bei APIs ohnehin nicht deterministisch.
- **Reasoning-Aufwand**: auf den Default setzen und loggen.
- **Keine Nachbearbeitung** außer dem automatischen Extrahieren des Codeblocks. Kompiliert ein
  Programm nicht oder ist es falsch, zählt es als Fehlschlag (keine Reparaturschleife).
- Alle Prompts, Rohantworten, Zeitstempel, Modell-IDs und Token-Zahlen werden gespeichert und
  sind Teil des Replikationspakets.

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
2. Generieren (6 LLMs × 3 Sprachen × 14 Aufgaben × k=5)  →  generated/  (+ raw logs)
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

- [ ] **Desktop-PC**: welche CPU (Intel oder AMD, Modell)? Davon hängt ab, ob DRAM gemessen werden kann.
- [ ] **Server**: Uni bzw. Firma, Grid'5000 oder Bare-Metal-Cloud?
- [ ] **Raspberry Pi 5 (8 GB)** beschaffen
- [ ] **USB-C-Messgerät** (~50 €) zur Kalibrierung: ja oder nein?
- [ ] Endgültige LLM-Liste: Modelle und exakte IDs am Tag der Generierung festhalten
- [ ] API-Budget: grob 1 260 Generierungen × ~2–5k Tokens, das ist ein niedriger zweistelliger
      bis niedriger dreistelliger Eurobetrag, je nach Modell (vor dem Start mit aktuellen Preisen
      nachrechnen)

---

## Änderungen v2 (2026-10-25)

- **LLMs festgelegt:** Claude Opus 5.5, GPT-6 Astra, Gemini Pro (aktuelle stabile Version), Kimi K3,
  DeepSeek-V4.1, Qwen3.8-27B. Die exakten IDs werden am Tag der Generierung eingetragen.
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
