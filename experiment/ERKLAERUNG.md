# Was ist im Ordner `experiment/`?

Dieser Ordner enthält alles, was die LLMs später bekommen (die **Aufgaben** und die **Prompts**),
und die Skripte, mit denen diese Dinge erzeugt wurden. Bisher ist **noch kein Code von einem LLM
generiert und noch nichts gemessen** worden. Das ist der nächste Schritt.

## Das große Bild in einem Satz

> Wir nehmen 14 Programmieraufgaben, bauen daraus für jede Sprache (Python, Java, C++) einen Prompt,
> schicken diese 42 Prompts an 3 KI-Assistenten (Claude, ChatGPT, Gemini), prüfen, ob der generierte Code korrekt ist, und messen
> anschließend, wie viel Energie er beim Ausführen verbraucht.

```
Aufgaben (tasks/)  ──►  Prompts (prompts/)  ──►  LLMs  ──►  generierter Code  ──►  Korrektheit  ──►  Energiemessung
   ✅ fertig             ✅ fertig               ⏳ noch nicht   ⏳                   ⏳                ⏳
```

---

## Übersicht der Ordner

| Ordner / Datei | Was ist das? | Musst du das anfassen? |
|---|---|---|
| `tasks/` | Die **14 Programmieraufgaben**, eine pro Unterordner | Nur zum Anschauen |
| `prompts/` | Die **Prompt-Vorlagen** und die **42 fertigen Prompts** | Hier sieht man, was die LLMs bekommen |
| `data/` | Hilfsdaten: Liste aller Aufgaben aus dem Benchmark und welche ausgewählt wurden | Nein |
| `scripts/` | Python-Skripte, die alles oben automatisch erzeugt haben | Nur, wenn man etwas neu erzeugen will |
| `README.md` | Kurze technische Anleitung (Englisch) zum Reproduzieren | Nein |
| `ERKLAERUNG.md` | Diese Datei | — |

---

## 1. `tasks/`: die Aufgaben

Es gibt **zwei Arten** von Aufgaben:

### a) `EB01` bis `EB10`: 10 Aufgaben aus EffiBench-X

EffiBench-X ist ein wissenschaftlicher Benchmark (frei nutzbar, Apache-Lizenz). Die Aufgaben stammen
ursprünglich von LeetCode. Das LLM bekommt eine Aufgabe und das **Gerüst einer Klasse** und muss
die Methode ausfüllen. **Welchen Algorithmus** es wählt, entscheidet das LLM selbst.

Ausgewählt wurden sie **zufällig, aber nachvollziehbar**: 5 Kategorien × je eine mittelschwere und
eine schwere Aufgabe.

| ID | Aufgabe | Kategorie | Schwierigkeit |
|---|---|---|---|
| EB01 | Maximum Total Damage With Spell Casting | Sortieren / Suchen | Medium |
| EB02 | Kth Smallest Amount With Single Denomination Combination | Sortieren / Suchen | Hard |
| EB03 | Sum of Digit Differences of All Pairs | Mathematik | Medium |
| EB04 | Count the Number of Infection Sequences | Mathematik | Hard |
| EB05 | Find Subtree Sizes After Changes | Strings | Medium |
| EB06 | Palindrome Rearrangement Queries | Strings | Hard |
| EB07 | Maximum Score After Applying Operations on a Tree | Dynamische Programmierung | Medium |
| EB08 | Count the Number of Powerful Integers | Dynamische Programmierung | Hard |
| EB09 | Minimum Number of Coins for Fruits | Datenstrukturen | Medium |
| EB10 | Longest Common Suffix Queries | Datenstrukturen | Hard |

**Inhalt eines EB-Ordners (Beispiel `tasks/EB03/`):**

| Datei | Was ist das? | Bekommt das LLM das? |
|---|---|---|
| `task.json` | Steckbrief: Titel, Kategorie, Schwierigkeit, Aufgabentext, Zeitlimit | Den Aufgabentext ja (über den Prompt) |
| `starter/` | Das **leere Code-Gerüst** pro Sprache (`python3.py`, `java.java`, `cpp.cpp`) | ✅ Ja |
| `reference/` | Eine **Musterlösung** pro Sprache, zum Vergleichen | ❌ Nein, geheim |
| `runner/` | Der **Test-Rahmen**: liest die Eingabe, ruft die Methode des LLMs auf und gibt das Ergebnis aus | ❌ Nein, kommt später dazu |
| `test_generator.py` | Ein Programm, das **Testfälle erzeugt**, auch sehr große Eingaben für die Messung | ❌ Nein |
| `evaluator.py` | Ein Programm, das prüft, ob die Ausgabe **richtig** ist | ❌ Nein |

> ⚠️ `test_generator.py` und `evaluator.py` stammen aus dem Datensatz und wurden noch nicht
> ausgeführt. Sie sollen später in einer abgeschotteten Umgebung (Docker) laufen.

**Warum der Runner?** Er sorgt dafür, dass alle LLMs **denselben Code zum Einlesen und Ausgeben**
benutzen. Messunterschiede kommen dann wirklich von der Lösung des LLMs und nicht davon, wie es
die Eingabe liest.

### b) `CLBG01` bis `CLBG04`: 4 klassische Benchmark-Aufgaben

Sie stammen aus dem **Computer Language Benchmarks Game**, auf dem auch das bekannte Paper von
Pereira et al. aufbaut. Hier ist der **Algorithmus fest vorgegeben**; das LLM muss ihn nur gut
umsetzen.

| ID | Aufgabe | Was passiert da? |
|---|---|---|
| CLBG01 | n-body | Simuliert die Umlaufbahnen von Sonne und Planeten (viele Fließkomma-Rechnungen) |
| CLBG02 | spectral-norm | Rechnet mit einer großen Matrix (Fließkomma, Schleifen) |
| CLBG03 | binary-trees | Baut sehr viele Binärbäume auf und ab (testet Speicherverwaltung) |
| CLBG04 | fannkuch-redux | Durchläuft alle Permutationen einer Zahlenfolge (Ganzzahl-Rechnungen) |

**Inhalt eines CLBG-Ordners:**

| Datei | Was ist das? |
|---|---|
| `spec.md` | Die **Aufgabenbeschreibung** in eigenen Worten. Genau dieser Text steht im Prompt. |
| `task.json` | Steckbrief |
| `reference/python3.py` | Eine **Musterlösung** in Python. Sie liefert exakt die offiziellen Referenzergebnisse und ist damit geprüft. |
| `expected/` | Die **richtige Ausgabe** für eine kleine Eingabe, zum Prüfen des LLM-Codes |

**Warum zwei Arten?** Damit wir später unterscheiden können:
- Bei **EB** kann ein LLM effizienter sein, weil es einen **besseren Algorithmus** wählt.
- Bei **CLBG** ist der Algorithmus gleich, Unterschiede kommen nur von der **Umsetzung**.

---

## 2. `prompts/`: was die LLMs bekommen

| Datei / Ordner | Was ist das? |
|---|---|
| `template_function.txt` | **Vorlage** für die EB-Aufgaben („Fülle diese Klasse aus“) |
| `template_program.txt` | **Vorlage** für die CLBG-Aufgaben („Schreibe ein komplettes Programm“) |
| `languages.json` | Die wenigen Stellen, die sich je Sprache unterscheiden (z. B. „Target Python 3.14“) |
| `rendered/` | Die **42 fertigen Prompts**: `rendered/<Aufgabe>/<Sprache>.txt`, z. B. `rendered/EB03/cpp.txt` |
| `rendered/index.json` | Liste aller Prompts mit einer Prüfsumme (SHA-256), damit später belegt werden kann, dass sie nicht verändert wurden |

**Wichtige Regeln der Prompts (für die Fairness):**
- Alle LLMs bekommen **exakt denselben Text**.
- Die Sprachen unterscheiden sich nur in **einer Zeile** (Sprachversion bzw. Compiler) und im
  Code-Gerüst.
- Die Wörter „effizient“, „schnell“ oder „Energie“ kommen **bewusst nicht vor**. Wir wollen
  messen, wie die LLMs **normalerweise** programmieren.

👉 **Tipp:** Öffne `prompts/rendered/EB03/cpp.txt`. Genau so sieht ein Prompt aus, der an ein LLM geht.

---

## 3. `data/`: Hilfsdaten

| Datei | Was ist das? |
|---|---|
| `effibench_x_metadata.jsonl` | Eine Liste **aller 623 Aufgaben** von EffiBench-X (nur Titel, Tags, Schwierigkeit usw., ohne Testdaten) |
| `effibench_x_extras.jsonl` | Zu jeder Aufgabe: für welche Sprachen es Musterlösungen und Test-Rahmen gibt |
| `selected_effibench_tasks.json` | **Ergebnis der Auswahl**: welche 10 Aufgaben gezogen wurden und mit welchem Zufalls-Seed (20261025) |

Diese Dateien braucht man nur, um die Auswahl nachzuvollziehen oder zu wiederholen.

---

## 4. `scripts/`: die Werkzeuge

Diese Skripte haben alles oben **automatisch** erzeugt. Sie laufen in dieser Reihenfolge:

| # | Skript | Was macht es? |
|---|---|---|
| 1 | `fetch_effibench_metadata.py` | Lädt die Liste aller EffiBench-X-Aufgaben herunter, das ergibt `data/effibench_x_metadata.jsonl` |
| 2 | `fetch_effibench_extras.py` | Lädt dazu, welche Sprachen pro Aufgabe verfügbar sind, das ergibt `data/effibench_x_extras.jsonl` |
| 3 | `select_tasks.py` | **Wählt die 10 Aufgaben** zufällig, aber reproduzierbar aus, das ergibt `data/selected_effibench_tasks.json` |
| 4 | `fetch_selected_tasks.py` | Lädt die vollständigen Daten der 10 Aufgaben, das ergibt `tasks/EB01..EB10/` |
| 5 | `render_prompts.py` | Baut aus Vorlagen und Aufgaben die **42 fertigen Prompts**, das ergibt `prompts/rendered/` |

Die Skripte 1, 2 und 4 brauchen die Python-Umgebung `.venv`, die du gelöscht hast. Das ist okay,
denn ihre Ergebnisse liegen schon vor. Die Anleitung zum Neu-Anlegen steht in `README.md`.
Skript 5 läuft ohne Zusatzpakete: `python3 scripts/render_prompts.py`.

> Die CLBG-Aufgaben wurden nicht per Skript erzeugt, sondern von Hand geschrieben und mit den
> Musterlösungen geprüft.

---

## Was kommt als Nächstes?

Folgendes fehlt noch und kommt später in diesen Ordner:

1. **Generierung:** ein Skript, das die 42 Prompts je 5-mal an Claude Code, Codex CLI und
   Gemini CLI schickt (über eure Abos, ohne API-Kosten) und die Antworten speichert (630 Programme)
2. **Korrektheit:** den generierten Code in Docker kompilieren und testen
3. **Messung:** die korrekten Programme auf PC, Server und Raspberry Pi ausführen und Energie,
   Zeit und Speicher messen
4. **Auswertung:** Statistik und Diagramme für das Paper
