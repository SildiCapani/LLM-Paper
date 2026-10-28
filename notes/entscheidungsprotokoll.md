# Entscheidungsprotokoll (für das Schreiben des Papers)

Hier steht **jede methodische Entscheidung und jede wichtige Beobachtung**, mit Begründung und
dem Ort, an dem sie im Paper erwähnt werden muss. Gutachter fragen genau nach solchen Dingen
(„Warum ohne Temperatur?“, „Warum diese Aufgaben?“, „Wie wurde Kontext ausgeschlossen?“).

**Regel:** Jede neue Entscheidung kommt sofort hierher. Die Spalte „Im Paper?“ zeigt, ob sie
schon im Text steht.

Legende: ✅ steht im Paper · ⏳ muss noch ins Paper · 🔁 überholt (siehe späterer Eintrag)

Paper-Kapitel: `§1` Introduction · `§3` Related Work · `§4` RQs · `§5` Setup · `§6` Methodik ·
`§7` Results · `§8` Discussion · `§9` Threats · `§10` Conclusion · `App` Anhang

---

## A. Forschungsfrage und Abgrenzung

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| A1 | 25.10. | Gemessen wird die Energie beim **Ausführen** des generierten Codes, nicht bei der Generierung | Abgrenzung von Green-AI-Arbeiten zur Inferenz-Energie | §1, §9 (Scope) | ✅ §1 |
| A2 | 25.10. | Die **Forschungslücke ist enger** als ursprünglich gedacht: Mehrere Sprachen (Solovyeva) und mehrere Plattformen (Apsan) gibt es schon, aber **nicht kombiniert** und **ohne Interaktionstests** | Literaturrecherche, siehe `literature-review.md` | §1, §3 | ✅ §3 |
| A3 | 25.10. | Stärkstes Argument: **Apsan et al. (ICSE '26) beobachten wechselnde LLM-Rangfolgen je Plattform, testen das aber nicht** | Begründet RQ4 direkt | §1, §3 | ✅ §3 |
| A4 | 25.10. | Das SLR von Masthan Ali et al. (2026) fordert ausdrücklich plattformübergreifende Studien und mehr Hardware-Messung | Stützt die Lücke durch eine Sekundärstudie | §1, §3 | ✅ §3 |
| A5 | 25.10. | **Hypothesen umgebaut**: H1 Haupteffekt LLM, H2 LLM × Sprache, H3 LLM × Plattform, H4 Dreifach-Interaktion, H5 Zeit-Energie | Jede Hypothese entspricht genau einem Term im Mixed Model | §4 | ✅ §4 |
| A6 | 25.10. | **RQ3 relativ formuliert** („relative energy efficiency“) | Messwerkzeuge erfassen auf den Plattformen unterschiedliche Systemteile (siehe D3) | §4 | ✅ §4 |

## B. LLMs und Zugang

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| B1 | 25.10. | 🔁 Ursprünglich 6 LLMs (3 proprietär, 3 Open-Weight) | Kriterien: Anbieter-Vielfalt, feste Versionen, Relevanz | — | 🔁 |
| B2 | 25.10. | 🔁 Qwen3.8-27B gestrichen, dann 5 LLMs | Wunsch der Autoren | — | 🔁 |
| B3 | 25.10. | **Nur 3 LLMs: Claude, GPT, Gemini, jeweils über das offizielle CLI** (Claude Code, Codex CLI, Gemini CLI) mit vorhandenen Abos | **Keine API-Kosten**; Pro-Abos enthalten keinen API-Zugang | §5, §9 | ✅ §5, §9 |
| B4 | 25.10. | **Framing: Wir messen „Modell + offizielles Werkzeug“**, so wie Entwickler es nutzen (ökologische Validität) | Ehrliche Benennung des Faktors „LLM“ | §5, §9 | ✅ §5, §9 |
| B5 | 25.10. | **Kimi K3 und DeepSeek-V4.1 gestrichen** | Kein vergleichbares Abo-CLI; über eine API wären die Bedingungen andere (Vermischung von Modell und Zugangsweg) | §5, §10 (Future Work) | ✅ §5, §10 |
| B6 | 25.10. | **Temperatur wird nicht gesetzt**, überall Werkzeug-Default | Die Claude-API lehnt `temperature` seit 21.10.2026 ab; die CLIs lassen keine einheitliche Einstellung zu | §6 | ✅ §6 |
| B7 | 25.10. | 🔁 Reasoning-Aufwand (Effort) bleibt auf Default und wird geloggt (ersetzt durch B13) | Wie B6 | — | 🔁 |
| B8 | 25.10. | **Zero-Shot**, keine Hinweise auf Effizienz, Geschwindigkeit oder Energie im Prompt | Wir messen das Standardverhalten; Prompting untersuchen schon Rekhi, Cappendijk und Apsan | §6 | ✅ §6 |
| B9 | 25.10. | **k = 5 unabhängige Samples** pro Aufgabe × Sprache × LLM, jeweils in einer neuen Sitzung | Bildet die Streuung des Modellverhaltens ab | §5, §6 | ✅ §5, §6 |
| B10 | 25.10. / 27.10. | Codex-Modell: **`gpt-6.1-sol`** (GPT-6.1 Sol), das Modell mit höchster Priorität in `codex debug models`; sein Standard-Effort ist ohnehin „medium“ | Stärkstes Modell im Abo, passt zu B13 | §5 Tabelle | ✅ §5 |
| B11 | 25.10. | Mit 3 LLMs gibt es nur 3! = 6 mögliche Rangfolgen, daher ist **das Mixed Model die Hauptevidenz für RQ4** | Begrenzte Auflösung von Ranganalysen | §6, §9 | ✅ §9 |
| B12 | 25.10. | **Interessenkonflikt**: Der KI-Assistent, der beim Paper hilft, ist Claude, und Claude ist auch ein Studienobjekt | Transparenz; Claude darf weder bevorzugt noch benachteiligt werden | Erklärung zur KI-Nutzung (siehe G1) | ⏳ |
| B13 | 27.10. | **Reasoning-Effort einheitlich „medium“** für alle drei Werkzeuge (Claude Code `--effort medium`, Codex `model_reasoning_effort="medium"`, Antigravity über die Modell-ID `…-medium`) | Antigravity verlangt eine Stufe im Modellnamen, die Default-Regel (B7) war damit nicht mehr haltbar. Gleiche nominale Stufe ist fairer als drei unbekannte Defaults; „medium“ ist auch der Default von Claude Opus 5.5. **Einschränkung:** Die Stufen sind herstellerübergreifend nicht gleich kalibriert. | §6, §9 | ✅ §6, §9 |
| B14 | 27.10. | **Gemini-Modell: `gemini-4-argon-medium`** (Gemini 4 Argon), das stärkste Gemini-Modell laut `agy models` | Flaggschiff-Prinzip wie bei Claude und GPT | §5 Tabelle | ✅ §5 |
| B15 | 27.10. | Antigravity bietet auch Claude Opus 5.5, Claude Sonnet 5.5 und GPT-OSS 120B an. **Diese werden nicht über Antigravity genutzt**: Claude läuft über sein eigenes Werkzeug (Claude Code) | Prinzip „jedes Modell über das CLI seines Herstellers“ (B4) | — (optional Future Work: gleiches Modell in verschiedenen CLIs) | — |

## C. Aufgaben und Prompts

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| C1 | 25.10. | **14 Aufgaben: 10 aus EffiBench-X + 4 aus CLBG** | EB: Referenzlösungen und Tests in allen 3 Sprachen; CLBG: skalierbar, Anknüpfung an Pereira et al. | §5 | ✅ §5 |
| C2 | 25.10. | **Zwei Aufgabentypen: EB = Algorithmus frei, CLBG = Algorithmus vorgegeben** | Trennt „besserer Algorithmus“ von „bessere Umsetzung“; hilft bei der Interpretation | §5, §8 | ✅ §5 · ⏳ §8 |
| C3 | 25.10. | **EB-Auswahl stratifiziert**: 5 Kategorien × {Medium, Hard}, Zufall mit **Seed 20261025**, Pool aus 244 Aufgaben | Reproduzierbar, keine Rosinenpickerei; Schwierigkeit als möglicher Faktor | §5 | ✅ §5 |
| C4 | 25.10. | **Funktionsformat statt stdio** für EB-Aufgaben | Nur Funktionsaufgaben haben Kategorie-Tags; gemeinsamer I/O-Harness pro Sprache für alle LLMs | §5 | ✅ §5 |
| C5 | 25.10. | Kategorien beruhen auf LeetCode-Tags und **sind nicht exklusiv** (z. B. EB05: `string` + `tree`) | Ehrlich benennen | §5 | ✅ §5 |
| C6 | 25.10. | **Fehler im Datensatz gefunden**: In `description_md` fehlen Hochstellungen (10^5 wird zu „105“). Deshalb werden die Prompts aus dem HTML erzeugt. | Sonst sehen die LLMs falsche Größenordnungen und wählen womöglich andere Algorithmen | §6 | ✅ §6 |
| C7 | 25.10. | Bilder in EB05 und EB07 werden durch „[image omitted]“ ersetzt; die Beispiele bleiben als Text vollständig | Rein textueller Prompt | §6 | ✅ §6 |
| C8 | 25.10. | **CLBG-Spezifikationen in eigenen Worten**, verifiziert: eigene Referenzlösungen liefern exakt die offiziellen Ausgaben | Urheberrecht; Korrektheit der Spezifikation belegt | §5 | ✅ §5 |
| C9 | 25.10. | binary-trees verlangt ausdrücklich echte Allokation (keine Formel, kein Caching) | Sonst ist der Benchmark sinnlos | App/§5 | ⏳ kurz erwähnen |
| C10 | 25.10. | **Kontamination wahrscheinlich**: EB-Aufgaben stammen von 11/2023 bis 10/2024, also vor allen Modell-Cutoffs | Betrifft eher absolute Werte als den Vergleich der LLMs | §9 | ✅ §9 |
| C11 | 25.10. | Prompts unterscheiden sich je Sprache nur in Sprachname, einer Versionszeile und dem Code-Gerüst | Fairness zwischen den Sprachen | §6, App | ✅ |
| C12 | 25.10. | Alle 42 Prompts mit **SHA-256-Prüfsumme** gespeichert | Belegt, dass die Prompts unverändert blieben | §6 | ✅ §6 |
| C13 | 25.10. | Prompt-Vorlagen werden **direkt aus `experiment/prompts/`** in den Anhang eingebunden | Paper und Experiment können nicht auseinanderlaufen | App | ✅ |
| C14 | 28.10. | **Datensatzfehler:** Die C++-Referenz von EB03 nutzt ein nicht initialisiertes Array (`int cntDigits[11][10];`, undefiniertes Verhalten) und liefert mit `-O2` falsche Werte. Behoben mit `= {}` (Kommentar in der Datei) | Referenz dient als Basislinie; minimale Korrektur | Replikationspaket | – |
| C15 | 28.10. | **Korrektheitstests:** 30 Fälle pro EB-Aufgabe aus dem Datensatz-Generator (Seed 42), **einmal** auf dem Laptop isoliert erzeugt (`python -I`, eigener Ordner; EB04 braucht ein höheres Rekursionslimit, per Aufruf-Wrapper gesetzt). CLBG: offizielle Prüfausgabe. Zusätzlich muss die Ausgabe der großen Eingabe der Referenz entsprechen. Vergleich mit den Datensatz-`evaluator.py` (geprüft: reine Zahlen-/Listenvergleiche). Mutationstest: verfälschte Lösung fällt bei 30/30 durch | Gleiche Tests auf allen Plattformen; Generator-Code läuft nur einmal | §6 | ✅ §6 |
| C16 | 28.10. | **Große Eingaben für EB selbst erzeugt** (`bench/workloads.py`, Seed 20261025): an der Obergrenze der Constraints, Bäume flach (keine Rekursionsfallen), Strings mit Überlappungen. Die Datensatz-Generatoren liefern nur kleine Fälle | Messbare Laufzeit nötig | §5 Workload | ✅ §5 |

## D. Plattformen und Energiemessung

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| D1 | 25.10. | Plattform „Desktop-PC“ heißt jetzt **„Laptop“** (Intel i7-1185G7, 8 Threads, 32 GB) | Ehrliche Bezeichnung des vorhandenen Geräts | §5 | ✅ §5 |
| D2 | 26.10. | Plattformen **noch offen**: RPi 5 und Server (Klärung in 2–3 Tagen); **Mac M4 als ARM-Alternative**; Windows nur im Notfall | Verfügbarkeit | §5 | ⏳ nach Entscheidung |
| D9 | 28.10. | **Windows: keine Energiemessung** – RAPL ist ohne Kernel-Treiber nicht lesbar (auch nicht in WSL). Falls der Rechner gebraucht wird: Linux-Live-System booten und wie Linux messen | Ein Windows-Treiber wäre eine weitere, ungeprüfte Messmethode | §5 (nur falls genutzt) | ⏳ |
| D10 | 28.10. | **Raspberry Pi 5:** Energie-Leser `PmicReader` gebaut: pollt `vcgencmd pmic_read_adc` laufend und summiert Strom × Spannung aller Schienen; Verluste vor dem PMIC (USB-C-Eingang) fehlen; das Pollen kostet CPU, ist aber auch im Leerlauf enthalten. Mit Beispieldaten getestet, **auf echtem Pi noch nicht** | Einzige Software-Messmöglichkeit am Pi | §5 | ⏳ nach Test auf dem Pi |
| D3 | 25.10. | **Absolute Joule werden nicht plattformübergreifend verglichen**, nur Rangfolgen und Verhältnisse | RAPL, powermetrics und PMIC erfassen unterschiedliche Systemteile | §5, §9 | ✅ §5, §9 |
| D4 | 27.10. | **Laptop-RAPL-Bereiche: package, core, uncore, psys, kein DRAM**. Gemessen wird über die Linux-Powercap-Schnittstelle, nicht über `perf`. | Im Pilot festgestellt; das Paper hatte fälschlich „+DRAM“ und „perf“ genannt (korrigiert) | §5 | ✅ §5 (korrigiert) |
| D5 | 26.10. | Mac: `powermetrics` liefert **Modell-Schätzungen von Apple**, keine direkte Messung; Abtastung alle 100 ms; Bereich `combined` | Einschränkung der Messgenauigkeit | §5, §9 | ⏳ |
| D6 | 25.10. | RPi 5: PMIC über `vcgencmd pmic_read_adc`; die Werte liegen laut Community systematisch zu niedrig. Kalibrierung mit USB-C-Messgerät empfohlen. | Validität | §5, §9 | ⏳ falls RPi genutzt wird |
| D7 | 25.10. | Server muss **Bare-Metal** sein, keine Cloud-VM | In VMs ist RAPL fast nie verfügbar | §5 | ⏳ falls Server genutzt wird |
| D8 | 25.10. | RAPL-Zähler sind aus Sicherheitsgründen nur für Root lesbar (CVE-2020-8694); für die Messung werden sie **vorübergehend** freigegeben | Reproduzierbarkeit des Aufbaus | Replikationspaket | ⏳ (nur README) |

## E. Ausführung und Messprotokoll

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| E1 | 25.10. | **C++ mit `-O2`, ohne Sanitizer** | Solovyeva nutzt `-O0` (unrealistisch); EffiBench-X nutzt ASan (verfälscht Energie) | §5 | ✅ §5 |
| E2 | 25.10. | **Gleiche Laufzeitversionen auf allen Plattformen** (Python 3.14, OpenJDK 25, GCC 14) | Apsan et al. hatten Python 3.8/3.11/3.12 gemischt (Störfaktor) | §5 | ✅ §5 · Docker vs. nativ entschieden → E11 |
| E3 | 25.10. | **Gemessen wird der ganze Prozess** inkl. Interpreter- bzw. JVM-Start | So wird ein Programm tatsächlich ausgeführt; der Startaufwand wird separat berichtet | §6 | ✅ §6 |
| E4 | 25.10. | **Nur korrekte Programme** gehen in die Energieanalyse; Korrektheit wird separat berichtet | Fehlerhafter Code ist oft „effizient“, weil er früh abbricht | §6 | ✅ §6 |
| E5 | 25.10. | Ranganalysen nur auf Aufgaben, bei denen jedes LLM in jeder Sprache ≥ 1 korrekte Lösung hat; das Mixed Model nutzt alle Daten | Vollständige Zellen für Rangfolgen | §6 | ✅ §6 |
| E6 | 26.10. | **Messablauf**: Leerlauf (30 s) → Aufwärmlauf → alle Läufe in zufälliger Reihenfolge, 5 s Pause → Leerlauf (30 s); netto = brutto − mittlere Leerlaufleistung × Laufzeit | Drift und Hintergrundlast herausrechnen | §5, §6 | ✅ (Grundzüge) · ⏳ Details |
| E7 | 26.10. | 10 Wiederholungen pro Programm und Plattform; Kern-Pinning (Linux) | Weniger Varianz | §6 | ✅ |
| E8 | 27.10. | **Pilot 1 (Laptop, CLBG-Python-Referenzen, ~1 s pro Lauf)**: Laufzeit streut 1,5–3,3 %, Brutto-Energie 4–6 %, **Netto-Energie 13–29 %** (zu hoch) | Ursache: **14–15 W Leerlauf** durch Hintergrundprogramme, Leerlauf-Drift von 14,0 auf 15,5 W, CPU etwa 80 °C, `powersave` + Turbo aktiv | §6 (Pilotstudie) | ⏳ |
| E9 🔁 E10 | 27.10. | Konsequenz aus E8: **Eingaben auf ca. 5 s pro Lauf kalibrieren**, ohne die Claude-App und ohne Browser messen, `performance`-Modus, Turbo aus | Rauschen verringern | §6 | ⏳ nach Pilot 2 |
| E10 | 28.10. | **Kalibrierung (ersetzt E9):** Pro EB-Aufgabe Wiederholungen **R im selben Prozess**, pro CLBG-Aufgabe **N**, einmal auf dem Laptop: C++ ca. **1 s**, aber keine Referenz über **60 s**. Ergebnis (`bench/data/manifest.json`): EB01 R=78, EB02 4208, EB03 115, EB04 1518, EB05 46, EB06 20, EB07 113, EB08 855051, EB09 2850, EB10 52; CLBG01 N=10⁷, CLBG02 2500, CLBG03 18, CLBG04 10. Gleiche Werte auf allen Plattformen. Bei EB02 und CLBG01/02/04 bleibt C++ unter 1 s (begrenzt durch Java bzw. Python) | 5 s für C++ hätte Python-Läufe von mehreren Minuten bedeutet (Tage pro Plattform) | §5 Workload | ✅ §5 |
| E11 | 28.10. | **Native Sprachinstallationen statt Docker** (ersetzt die Container-Planung aus E2): gleiche Versionen (Python 3.14, Java 25, GCC 14) auf jeder Plattform installieren; das Skript prüft und protokolliert die Versionen und warnt bei Abweichung | powermetrics (Mac) und PMIC (Pi) sind nur vom Host lesbar; Container auf dem Mac liefen in einer VM | §5 | ✅ §5 |
| E12 | 28.10. | **Messprotokoll** (`bench/run_platform.py`): 3 Wiederholungen pro Programm (k=5 Samples liefern zusätzliche Replikation), 3 s Pause, Leerlauf 60 s am Anfang und alle 30 min, feste Zufallsreihenfolge (Seed 20261025), Zeitgrenze 10× Referenzdauer, nach Timeout keine weiteren Wiederholungen, Fortsetzen nach Abbruch. Korrektheit wird auf **jeder** Plattform geprüft. Kein Core-Pinning (JVM ist mehrfädig) | Laptop ≈ 8 h statt mehrerer Tage | §5, §6 | ✅ §5, §6 |
| E13 | 28.10. | **Einschränkung der Wiederholung im Prozess:** einmalige Initialisierung (z. B. statische Tabellen der C++-Referenz von EB04) wird über R Aufrufe verteilt; begünstigt Lösungen mit Cache über Aufrufe hinweg | Ehrlich benennen | §9 | ✅ §9 |
| E14 | 28.10. | **Testlauf der Pipeline auf dem Laptop** (Python 3.12, Java 21, GCC 13, ohne Energie): alle 664 Programme (630 + 34 Referenzen) kompilieren; **629/630 generierte Programme korrekt** (Ausnahme: Gemini, CLBG04, Python, 1 Sample); alle Referenzen korrekt. Nur Vorab-Ergebnis mit falschen Sprachversionen, **nicht ins Paper** | Pipeline funktioniert | – (erst nach echter Messung) | – |

## F. Generierung

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| F1 | 27.10. | **Keine Chat-Oberflächen**, nur automatisierte CLI-Aufrufe per Skript | Chat-Oberflächen nutzen Memory, Custom Instructions und frühere Chats; manuelles Kopieren ist fehleranfällig | §6 | ✅ (implizit) · ⏳ explizit |
| F2 | 27.10. | **Jede Anfrage: neue Sitzung + neuer leerer Ordner**; keine CLAUDE.md, AGENTS.md oder GEMINI.md | Gleicher Kontext für alle | §6 | ✅ §6 |
| F3 | 27.10. | **Benutzer-Konfiguration, Memory, Plugins und MCP aus**; wenn möglich mit **eigenem, leerem Home-Ordner** pro CLI | Globale Dateien (z. B. `~/.claude/CLAUDE.md`) könnten sonst einfließen | §6 | ⏳ nach Verifikation |
| F4 | 27.10. | **CLI-Versionen einfrieren** (automatische Updates aus) | Gleiches Werkzeug über die ganze Erhebung | §6 | ✅ §6 |
| F5 | 27.10. | **Zufällige Reihenfolge** über Werkzeuge, Aufgaben und Sprachen; Erhebung in kurzem Zeitraum | Serverseitige Updates und Tageszeit-Effekte treffen alle gleich | §6 | ⏳ |
| F6 | 27.10. | **Wiederholt wird nur bei technischen Fehlern** (Netzwerk, Nutzungslimit), **nie bei falschem Code** | Keine Schönung der Ergebnisse | §6 | ⏳ |
| F7 | 27.10. | Werkzeugaufrufe werden aus den JSON-Logs ausgewertet und berichtet | Kontrolle, ob die CLIs trotz Verbot Werkzeuge nutzen | §6, §7 | ✅ §5 (angekündigt) |
| F8 | 27.10. | **Eigener Konfigurationsordner pro CLI** über `CLAUDE_CONFIG_DIR`, `CODEX_HOME` und `GEMINI_CLI_HOME` (`experiment/generate/homes/`); dort liegen nur die Login-Daten | Persönliche Einstellungen, Memory und Plugins der normalen Installation fließen nicht ein; setzt F3 um | §6 (1 Satz), Replikationspaket | ⏳ |
| F9 | 27.10. | **Arbeitsordner außerhalb des Projekts** (`/tmp/llmgen-…`), pro Anfrage neu und leer | Claude Code und Codex suchen auch in übergeordneten Ordnern nach `CLAUDE.md` bzw. `AGENTS.md` und würden sonst die Projekt-`CLAUDE.md` mitlesen | Replikationspaket | ⏳ |
| F10 | 27.10. | Zusätzlich abgeschaltet: Laden von CLAUDE.md und Auto-Memory (`CLAUDE_CODE_DISABLE_CLAUDE_MDS`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`), nicht notwendiger Netzverkehr inkl. Auto-Update (`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`); ~~Gemini: Auto-Update aus, Nutzungsstatistik aus, 12 Werkzeuge ausgeschlossen~~ (🔁 F17: Gemini CLI entfällt) | Doppelte Absicherung von F3/F4 | Replikationspaket | ⏳ |
| F11 | 27.10. | **Feste zufällige Reihenfolge aller 630 Anfragen** in `generated/plan.json` (Seed 20261025); das Skript ist fortsetzbar | Setzt F5 um; Unterbrechungen durch Nutzungslimits ändern die Reihenfolge nicht | §6 | ⏳ |
| F12 | 27.10. | Technische Fehler (Absturz, Timeout, leere Antwort) werden bis zu 2× wiederholt; bei **Nutzungslimit** wird das Werkzeug für den Lauf pausiert; „kein Codeblock“ ist ein **endgültiges** Ergebnis (`no_code`) | Setzt F6 um; `no_code` zählt als Fehlschlag in der Korrektheitsrate | §6, §7 | ⏳ |
| F13 | 27.10. | Übernommen wird der **erste** Codeblock; Sprach-Tag und Anzahl der Blöcke werden protokolliert | Eindeutige, automatische Regel ohne Handarbeit (setzt F1/C12 um) | §6 | ✅ §6 |
| F14 | 27.10. | **Probe-Anfrage** vor dem Hauptlauf: Jedes CLI wird gefragt, welches Modell es ist, ob es zusätzliche Anweisungen hat und welche Werkzeuge es sieht | Überprüfung der Isolation; nicht Teil der Studiendaten | Replikationspaket | ⏳ |
| F15 | 27.10. | Generierungsskript mit **Attrappen der CLIs getestet**: Isolation (leerer Ordner außerhalb des Projekts, eigene Konfiguration, leere Werkzeugliste), Wiederholung, Pause bei Limit und Fortsetzen funktionieren. **Die echten JSON-Formate sind noch zu prüfen.** | Qualitätssicherung | — | — |
| F16 | 27.10. | CLI-Versionen für die Erhebung: Claude Code **2.1.311**, Codex CLI **0.164.0** (npm, Stand 27.10.2026), fest installiert; ~~Gemini CLI 0.65.0~~ → Antigravity CLI, Version unpinbar (F20) | Setzt F4 um | §5 Tabelle | ⏳ |
| F17 | 27.10. | **Gemini CLI durch Antigravity CLI (`agy`) ersetzt.** Der Login mit dem Google-Konto schlug fehl: „This client is no longer supported for Gemini Code Assist for individuals“. Google hat die Gemini CLI am **18.06.2026** für private Konten, Google AI Pro und Ultra abgeschaltet; die Antigravity CLI ist der offizielle Nachfolger und läuft mit dem AI-Pro-Abo | Kostenloser Zugang bleibt erhalten; Werkzeug-Paar „Gemini-Modell + offizielles Google-CLI“ bleibt gleich | §5 (Fußnote), §6, §9 | ✅ §5, §6, §9 |
| F18 | 27.10. | Antigravity: **Werkzeuge lassen sich nicht komplett abschalten**; Shell-Befehle sind headless standardmäßig verboten, Dateizugriff nur im Arbeitsordner (der leer ist). Werkzeugaufrufe werden aus `step_update`-Ereignissen gezählt | Wie bei Codex: Kontrolle über Protokoll statt Schalter | §6, §9 | ✅ §6, §9 |
| F19 | 27.10. | Antigravity: Einstellungen getrennt über eigenes `HOME` (`homes/gemini/.gemini/antigravity-cli/`); **der Login liegt im Schlüsselbund des Betriebssystems** und wird mit der normalen Installation geteilt | Kein Einfluss auf den Kontext; nur die Anmeldung ist geteilt | Replikationspaket | ⏳ |
| F20 | 27.10. | Antigravity wird über ein Installationsskript installiert (`curl … install.sh`), **eine feste Version lässt sich nicht wählen**; die Version wird pro Sitzung protokolliert (Stand: 1.4.8) | Abweichung von F4/F16 bei diesem Werkzeug | §9 | ⏳ |
| F21 | 27.10. | Codex: optionale Werkzeuge per Feature-Flags aus (`--disable` für shell_tool, unified_exec, multi_agent, image_generation, browser_use, apps, plugins, view_image u. a.; `web_search="disabled"`). **Nicht abschaltbar:** Sub-Agenten (`spawn_agent`), `apply_patch`, `request_user_input`; `code_mode_host` abzuschalten bricht Codex | So nah wie möglich an „keine Werkzeuge“ wie bei Claude | §6, §9 | ✅ §6, §9 |
| F22 | 27.10. | Antigravity läuft zusätzlich mit `--sandbox` (Terminal-Einschränkungen). Laut Probe bleiben u. a. `search_web` und Sub-Agenten verfügbar | Keine Abschaltoption; Kontrolle über das Protokoll der Werkzeugaufrufe | §6, §9 | ✅ §6, §9 |
| F23 | 27.10. | **Probe bestanden** (alle 3 Werkzeuge): keine CLAUDE.md/AGENTS.md/GEMINI.md/Memory im Kontext, Arbeitsordner danach leer, 0 Werkzeugaufrufe. Antigravity hängt automatisch Uhrzeit und „Modellwahl geändert“ an; Claude Code einen kleinen Kontoblock. Codex meldet seine Modell-ID nicht im Ereignisstrom (sie ist per `-m` fest gesetzt) | Isolation ist belegt; die automatischen Zusätze sind Teil des Werkzeugs (Faktor „Modell + Werkzeug“) | §6 | ✅ §6 |
| F24 | 27.10. | Antigravity-Parser an das echte Format angepasst (Schlüssel `event`, Inhalt verschachtelt unter `init`/`step_update`/`result`) | Die erste Probe lieferte sonst „technical_error“ trotz Antwort | – (nur Skript) | – |
| F25 | 27.10. | **Pilot-Generierung** (EB03 + CLBG01 × 3 Sprachen × 3 Werkzeuge × 1 = 18 Anfragen): 18/18 `ok`, je genau 1 Codeblock, 0 Werkzeugaufrufe, keine Wiederholungen nötig. Dauer pro Anfrage: Claude 3–14 s, Codex 6–21 s, Gemini 15–38 s | Skript und Protokoll funktionieren mit den echten CLIs; Hauptlauf (~612 Anfragen, ca. 3–4 h reine Laufzeit) kann starten. Korrektheit noch nicht geprüft | §6 (1 Satz) | ⏳ |
| F26 | 28.10. | **Generierung abgeschlossen:** 630/630 Anfragen `ok` (je 210 pro LLM), 0 Werkzeugaufrufe, kein `no_code`. Zeitraum 27.10. 14:06 – 28.10. 09:27 UTC. Umfang `generated/` ca. 17 MB | Datensatz vollständig; Korrektheit noch ungeprüft | §6 (1 Satz) | ⏳ |
| F27 | 28.10. | `experiment/generated/` liegt **nicht in Git** (.gitignore), wird zum Messen per rsync auf die Plattformen kopiert und separat gesichert (später Zenodo) | Wunsch der Autoren: Repo schlank halten | Replikationspaket | ⏳ |
| F28 | 28.10. | **Generierungszeit** (Wanduhrzeit des CLI-Aufrufs, letzter Versuch) als beschreibendes Ergebnis: Mittel ± SD Claude 7,1 ± 3,7 s, GPT 15,1 ± 5,9 s, Gemini 17,4 ± 13,8 s (Max. 191 s); CLBG bei allen langsamer als EB. Nur deskriptiv, kein eigener Test | Enthält Netzwerk und Serverlast beim Hersteller → misst Reaktionszeit des Werkzeugs, nicht Rechenaufwand des Modells. Token-Zahlen nicht vergleichbar (Claude meldet Eingabe-Tokens ohne Cache, keine getrennten Denk-Tokens) | §7 Tab. „Generation time“ | ✅ §7 |

## G. Sonstiges / Formalia

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| G1 | 27.10. | **Erklärung zur KI-Nutzung** nötig: KI-Unterstützung bei Recherche, Design, Code und Text; dazu der Interessenkonflikt aus B12 | Viele Konferenzen und Hochschulen verlangen das; Transparenz | eigener Abschnitt vor den Referenzen | ⏳ |
| G2 | 25.10. | Layout: IEEE-Konferenzformat (zweispaltig, `IEEEtran`) | Typisches Paper-Format; bei Wahl des Zielorts ggf. wechseln | — | ✅ |
| G3 | 25.10. | Alle Literaturangaben gegen arXiv und Crossref geprüft; die ICSE-Version von Apsan et al. hat einen Zusatzautor (Malavolta) | Korrekte Zitation | Referenzen | ✅ |
| G4 | 25.10. | Recherche bisher nur über arXiv, Web und Crossref; **Scopus, IEEE Xplore und ACM DL fehlen noch** | Vollständigkeit der Literaturrecherche | §3 | ⏳ |
| G5 | 27.10. | **Längenvorgabe: ca. 500 Wörter** für das Paper, **ohne Literaturverzeichnis und Abstract**; nicht wesentlich überschreiten | Vorgabe der Aufgabenstellung. Stand 27.10.: ca. 4.200 Wörter (inkl. Prompt-Anhang) → Paper muss stark gekürzt werden | alle Abschnitte | 🔁 durch G6 |
| G6 | 27.10. | **Längenvorgabe präzisiert: Ziel 500 Wörter, Obergrenze ca. 700–800 Wörter** (ohne Literaturverzeichnis und Abstract); trotzdem alle wichtigen Punkte nennen, jeweils in einem Satz | Leichte Überschreitung ist laut Autor:innen tolerierbar, deutlich mehr nicht. Details wandern in Tabellen und ins Replikationspaket | alle Abschnitte | ⏳ |

---

## Offene Punkte fürs Paper (Kurzliste aller ⏳)

- [ ] B12 + G1 Erklärung zur KI-Nutzung und zum Interessenkonflikt
- [ ] C2 Diskussion: EB vs. CLBG getrennt interpretieren
- [ ] C9 binary-trees: Allokation erzwungen
- [ ] D2 endgültige Plattformen
- [ ] D5/D6/D7 Messgrenzen der gewählten Plattformen in §5/§9
- [ ] E6 Details des Messablaufs
- [ ] E8/E9 Pilotstudie und Kalibrierung in §6
- [ ] F1, F3, F5, F6, F8–F12 Generierungsprotokoll: 1–2 Sätze in §6, Details ins Replikationspaket (wegen G6)
- [ ] F16 CLI-Versionen: aus Platzgründen nicht in der LLM-Tabelle → Replikationspaket bzw. 1 Satz in §5
- [ ] F20 Antigravity-Version nicht fixierbar → §9
- [ ] F25/F26 Pilot und Abschluss der Generierung: 1 Satz in §6 (Abschluss steht in §7)
- [ ] F28 Generierungszeit: bei Kürzung (G6) ggf. nur Tabelle behalten
- [ ] F27 generated/ ins Replikationspaket (Zenodo)
- [ ] D10 Pi-Messung auf echtem Pi prüfen
- [ ] E14 Korrektheitsraten nach der echten Messung in §7 eintragen
- [ ] Sprachversionen auf allen Plattformen installieren (E11), dann §5-Tabelle (TBD) füllen
- [ ] **G6 Paper auf 500 (max. 700–800) Wörter kürzen (ohne Quellen und Abstract)**
- [ ] G4 Literatursuche in Scopus, IEEE Xplore und ACM DL
