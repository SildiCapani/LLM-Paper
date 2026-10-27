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
| B7 | 25.10. | Reasoning-Aufwand (Effort) bleibt auf Default und wird geloggt | Wie B6 | §6 | ✅ §6 |
| B8 | 25.10. | **Zero-Shot**, keine Hinweise auf Effizienz, Geschwindigkeit oder Energie im Prompt | Wir messen das Standardverhalten; Prompting untersuchen schon Rekhi, Cappendijk und Apsan | §6 | ✅ §6 |
| B9 | 25.10. | **k = 5 unabhängige Samples** pro Aufgabe × Sprache × LLM, jeweils in einer neuen Sitzung | Bildet die Streuung des Modellverhaltens ab | §5, §6 | ✅ §5, §6 |
| B10 | 25.10. | Codex bietet über das Abo eigene Codex-Modelle an (z. B. `gpt-6.1-sol`), nicht zwingend „GPT-6 Astra“ | Modell-ID erst nach der Installation bekannt | §5 Tabelle | ⏳ ID eintragen |
| B11 | 25.10. | Mit 3 LLMs gibt es nur 3! = 6 mögliche Rangfolgen, daher ist **das Mixed Model die Hauptevidenz für RQ4** | Begrenzte Auflösung von Ranganalysen | §6, §9 | ✅ §9 |
| B12 | 25.10. | **Interessenkonflikt**: Der KI-Assistent, der beim Paper hilft, ist Claude, und Claude ist auch ein Studienobjekt | Transparenz; Claude darf weder bevorzugt noch benachteiligt werden | Erklärung zur KI-Nutzung (siehe G1) | ⏳ |

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

## D. Plattformen und Energiemessung

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| D1 | 25.10. | Plattform „Desktop-PC“ heißt jetzt **„Laptop“** (Intel i7-1185G7, 8 Threads, 32 GB) | Ehrliche Bezeichnung des vorhandenen Geräts | §5 | ✅ §5 |
| D2 | 26.10. | Plattformen **noch offen**: RPi 5 und Server (Klärung in 2–3 Tagen); **Mac M4 als ARM-Alternative**; Windows nur im Notfall | Verfügbarkeit | §5 | ⏳ nach Entscheidung |
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
| E2 | 25.10. | **Gleiche Laufzeitversionen auf allen Plattformen** (Python 3.14, OpenJDK 25, GCC 14) | Apsan et al. hatten Python 3.8/3.11/3.12 gemischt (Störfaktor) | §5 | ✅ §5 · ⚠️ Docker vs. nativ (Mac/Windows) noch klären |
| E3 | 25.10. | **Gemessen wird der ganze Prozess** inkl. Interpreter- bzw. JVM-Start | So wird ein Programm tatsächlich ausgeführt; der Startaufwand wird separat berichtet | §6 | ✅ §6 |
| E4 | 25.10. | **Nur korrekte Programme** gehen in die Energieanalyse; Korrektheit wird separat berichtet | Fehlerhafter Code ist oft „effizient“, weil er früh abbricht | §6 | ✅ §6 |
| E5 | 25.10. | Ranganalysen nur auf Aufgaben, bei denen jedes LLM in jeder Sprache ≥ 1 korrekte Lösung hat; das Mixed Model nutzt alle Daten | Vollständige Zellen für Rangfolgen | §6 | ✅ §6 |
| E6 | 26.10. | **Messablauf**: Leerlauf (30 s) → Aufwärmlauf → alle Läufe in zufälliger Reihenfolge, 5 s Pause → Leerlauf (30 s); netto = brutto − mittlere Leerlaufleistung × Laufzeit | Drift und Hintergrundlast herausrechnen | §5, §6 | ✅ (Grundzüge) · ⏳ Details |
| E7 | 26.10. | 10 Wiederholungen pro Programm und Plattform; Kern-Pinning (Linux) | Weniger Varianz | §6 | ✅ |
| E8 | 27.10. | **Pilot 1 (Laptop, CLBG-Python-Referenzen, ~1 s pro Lauf)**: Laufzeit streut 1,5–3,3 %, Brutto-Energie 4–6 %, **Netto-Energie 13–29 %** (zu hoch) | Ursache: **14–15 W Leerlauf** durch Hintergrundprogramme, Leerlauf-Drift von 14,0 auf 15,5 W, CPU etwa 80 °C, `powersave` + Turbo aktiv | §6 (Pilotstudie) | ⏳ |
| E9 | 27.10. | Konsequenz aus E8: **Eingaben auf ca. 5 s pro Lauf kalibrieren**, ohne die Claude-App und ohne Browser messen, `performance`-Modus, Turbo aus | Rauschen verringern | §6 | ⏳ nach Pilot 2 |

## F. Generierung (geplant, Skript noch nicht gebaut)

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| F1 | 27.10. | **Keine Chat-Oberflächen**, nur automatisierte CLI-Aufrufe per Skript | Chat-Oberflächen nutzen Memory, Custom Instructions und frühere Chats; manuelles Kopieren ist fehleranfällig | §6 | ✅ (implizit) · ⏳ explizit |
| F2 | 27.10. | **Jede Anfrage: neue Sitzung + neuer leerer Ordner**; keine CLAUDE.md, AGENTS.md oder GEMINI.md | Gleicher Kontext für alle | §6 | ✅ §6 |
| F3 | 27.10. | **Benutzer-Konfiguration, Memory, Plugins und MCP aus**; wenn möglich mit **eigenem, leerem Home-Ordner** pro CLI | Globale Dateien (z. B. `~/.claude/CLAUDE.md`) könnten sonst einfließen | §6 | ⏳ nach Verifikation |
| F4 | 27.10. | **CLI-Versionen einfrieren** (automatische Updates aus) | Gleiches Werkzeug über die ganze Erhebung | §6 | ✅ §6 |
| F5 | 27.10. | **Zufällige Reihenfolge** über Werkzeuge, Aufgaben und Sprachen; Erhebung in kurzem Zeitraum | Serverseitige Updates und Tageszeit-Effekte treffen alle gleich | §6 | ⏳ |
| F6 | 27.10. | **Wiederholt wird nur bei technischen Fehlern** (Netzwerk, Nutzungslimit), **nie bei falschem Code** | Keine Schönung der Ergebnisse | §6 | ⏳ |
| F7 | 27.10. | Werkzeugaufrufe werden aus den JSON-Logs ausgewertet und berichtet | Kontrolle, ob die CLIs trotz Verbot Werkzeuge nutzen | §6, §7 | ✅ §5 (angekündigt) |

## G. Sonstiges / Formalia

| ID | Datum | Entscheidung / Beobachtung | Begründung | Paper | Im Paper? |
|---|---|---|---|---|---|
| G1 | 27.10. | **Erklärung zur KI-Nutzung** nötig: KI-Unterstützung bei Recherche, Design, Code und Text; dazu der Interessenkonflikt aus B12 | Viele Konferenzen und Hochschulen verlangen das; Transparenz | eigener Abschnitt vor den Referenzen | ⏳ |
| G2 | 25.10. | Layout: IEEE-Konferenzformat (zweispaltig, `IEEEtran`) | Typisches Paper-Format; bei Wahl des Zielorts ggf. wechseln | — | ✅ |
| G3 | 25.10. | Alle Literaturangaben gegen arXiv und Crossref geprüft; die ICSE-Version von Apsan et al. hat einen Zusatzautor (Malavolta) | Korrekte Zitation | Referenzen | ✅ |
| G4 | 25.10. | Recherche bisher nur über arXiv, Web und Crossref; **Scopus, IEEE Xplore und ACM DL fehlen noch** | Vollständigkeit der Literaturrecherche | §3 | ⏳ |

---

## Offene Punkte fürs Paper (Kurzliste aller ⏳)

- [ ] B10 Codex-Modell-ID in die Tabelle eintragen
- [ ] B12 + G1 Erklärung zur KI-Nutzung und zum Interessenkonflikt
- [ ] C2 Diskussion: EB vs. CLBG getrennt interpretieren
- [ ] C9 binary-trees: Allokation erzwungen
- [ ] D2 endgültige Plattformen
- [ ] D5/D6/D7 Messgrenzen der gewählten Plattformen in §5/§9
- [ ] E6 Details des Messablaufs
- [ ] E8/E9 Pilotstudie und Kalibrierung in §6
- [ ] F1, F3, F5, F6 Generierungsprotokoll explizit in §6
- [ ] G4 Literatursuche in Scopus, IEEE Xplore und ACM DL
