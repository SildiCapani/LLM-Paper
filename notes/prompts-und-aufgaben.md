# Prompts und Aufgaben – was die LLMs lösen mussten

Diese Notiz erklärt, **woher die 14 Aufgaben kommen**, **wie die Prompts aussehen** und
**warum** wir es so gemacht haben. Die zugehörigen Entscheidungen stehen im
Entscheidungsprotokoll unter C1–C16 (Aufgaben/Prompts) und F (Generierung).

---

## 1. Überblick in einem Satz

Jedes der drei LLMs (Claude, GPT, Gemini) bekommt **14 Aufgaben × 3 Sprachen** (Python,
Java, C++) und löst jede davon **5-mal** mit genau demselben Prompt
→ 3 × 14 × 3 × 5 = **630 Programme**.

## 2. Woher kommen die Aufgaben?

Wir nutzen zwei Quellen, die sich bewusst unterscheiden (C1, C2):

| | **EffiBench-X (EB01–EB10)** | **Benchmarks Game (CLBG01–CLBG04)** |
|---|---|---|
| Herkunft | Datensatz EffiBench-X (Qing et al., 2025, Apache-2.0); die Aufgaben stammen ursprünglich von **LeetCode** | *Computer Language Benchmarks Game*, der Klassiker für Sprachvergleiche (auch Pereira et al. nutzen ihn) |
| Was ist vorgegeben? | Nur das **Problem** – den Algorithmus wählt das LLM frei | Der **Algorithmus** ist genau beschrieben – das LLM muss ihn nur umsetzen |
| Was messen wir damit? | „Findet das LLM einen effizienten Algorithmus?“ | „Setzt das LLM einen festen Algorithmus effizient um?“ |
| Format | **Funktion** in einer `Solution`-Klasse; unser Test-Harness ruft sie auf | **Ganzes Programm**, liest `N` von der Kommandozeile, schreibt auf stdout |
| Tests | 30 Testfälle aus dem Datensatz-Generator + große Messeingabe | offizielle Prüfausgabe + große Messeingabe |

**Warum EffiBench-X?** Es hat für jede Aufgabe Referenzlösungen und Testgeneratoren in
**allen drei Sprachen** – so können wir fair vergleichen und haben eine Basislinie.

**Warum CLBG?** Weil der Algorithmus feststeht, sehen wir dort Unterschiede in der
*Umsetzung* (z. B. Datenstrukturen, Speicherverwaltung) getrennt von der *Algorithmenwahl*.

### 2.1 Wie wurden die 10 EB-Aufgaben ausgewählt? (C3)

Nicht von Hand, sondern **zufällig und nachvollziehbar**:

1. Pool: alle Funktionsaufgaben aus EffiBench-X mit Kategorie-Tag (244 Aufgaben).
2. Einteilung in **5 Kategorien** × **2 Schwierigkeiten** (Medium, Hard).
3. Aus jeder der 10 Gruppen **eine** Aufgabe per Zufall mit festem Seed `20261025`.

So kann niemand sagen, wir hätten Aufgaben ausgesucht, die einem LLM liegen.

### 2.2 Die 14 Aufgaben

| ID | Aufgabe | Kategorie | Stufe | Worum geht es (vereinfacht) |
|---|---|---|---|---|
| EB01 | Maximum Total Damage With Spell Casting | Sortieren / Suchen | Medium | Zauber mit Schadenswerten auswählen, ohne dass zwei „benachbarte“ Werte (±1, ±2) vorkommen; Summe maximieren |
| EB02 | Kth Smallest Amount With Single Denomination Combination | Sortieren / Suchen | Hard | Mit Münzen (jeweils nur *eine* Sorte pro Betrag) den k-kleinsten möglichen Betrag finden |
| EB03 | Sum of Digit Differences of All Pairs | Mathematik | Medium | Für alle Zahlenpaare zählen, an wie vielen Stellen sich die Ziffern unterscheiden |
| EB04 | Count the Number of Infection Sequences | Mathematik | Hard | Zählen, in wie vielen Reihenfolgen sich eine „Infektion“ in einer Reihe ausbreiten kann (Kombinatorik, modulo) |
| EB05 | Find Subtree Sizes After Changes | String-Verarbeitung | Medium | Baum mit Buchstaben umhängen und danach die Größe jedes Teilbaums ausgeben |
| EB06 | Palindrome Rearrangement Queries | String-Verarbeitung | Hard | Für viele Anfragen prüfen, ob man durch Umordnen von Teilstücken ein Palindrom bekommt |
| EB07 | Maximum Score After Applying Operations on a Tree | Dynamische Programmierung | Medium | Werte aus einem Baum einsammeln, ohne einen Pfad komplett „leer“ zu machen |
| EB08 | Count the Number of Powerful Integers | Dynamische Programmierung | Hard | Zahlen in einem Bereich zählen, die auf ein bestimmtes Suffix enden und nur kleine Ziffern haben (Ziffern-DP) |
| EB09 | Minimum Number of Coins for Fruits | Datenstrukturen | Medium | Früchte kaufen, wobei jeder Kauf einige folgende Früchte gratis macht; minimale Kosten |
| EB10 | Longest Common Suffix Queries | Datenstrukturen | Hard | Für jedes Anfragewort das Wort mit dem längsten gemeinsamen Ende finden (typisch: Trie) |
| CLBG01 | n-body | Gleitkomma-Simulation | – | Umlaufbahnen von Sonne und vier Planeten simulieren, Energie vorher/nachher ausgeben |
| CLBG02 | spectral-norm | Lineare Algebra | – | Spektralnorm einer unendlichen Matrix mit der Potenzmethode annähern |
| CLBG03 | binary-trees | Speicher / Rekursion | – | Viele Binärbäume **wirklich** anlegen und durchlaufen (misst Speicherverwaltung) |
| CLBG04 | fannkuch-redux | Permutationen | – | Für alle Permutationen „Pfannkuchen-Wenden“ zählen; Prüfsumme und Maximum ausgeben |

Die Kategorien kommen aus den LeetCode-Tags und **überschneiden sich** (EB05 ist z. B.
auch eine Baumaufgabe, C5).

### 2.3 Was wir an den Aufgaben selbst gemacht haben

- **Datensatzfehler behoben (C6):** Im Markdown-Text von EffiBench-X fehlen
  Hochstellungen – aus `10^5` wird „105“. Ein LLM würde dann denken, die Eingabe sei winzig,
  und einen langsamen Algorithmus wählen. Deshalb erzeugen wir den Prompt aus dem **HTML**
  der Aufgabe, wo die Hochstellung erhalten ist.
- **Bilder (C7):** EB05 und EB07 enthalten Bilder; sie werden durch „[image omitted]“
  ersetzt. Die Beispiele stehen trotzdem vollständig als Text da.
- **CLBG in eigenen Worten (C8):** Die offiziellen Beschreibungen sind urheberrechtlich
  geschützt. Wir haben sie neu formuliert und mit eigenen Referenzlösungen geprüft, dass
  genau die offiziellen Ausgaben herauskommen.
- **binary-trees (C9):** Der Text verlangt ausdrücklich echtes Anlegen der Bäume – sonst
  könnte ein LLM das Ergebnis per Formel ausrechnen, und der Benchmark wäre sinnlos.
- **Fehler in einer Referenz (C14):** Die C++-Referenz von EB03 hatte ein nicht
  initialisiertes Array (falsche Werte mit `-O2`); minimal korrigiert.
- **Große Messeingaben (C16):** Die Testfälle des Datensatzes sind klein. Für die
  Energiemessung erzeugen wir pro Aufgabe **eine große Eingabe** an der Obergrenze der
  Constraints (Seed `20261025`) und lösen sie mehrfach (EB: `R`-mal im Prozess, CLBG:
  Größe `N`), so dass C++ etwa 1 s läuft (E16).

## 3. Wie sehen die Prompts aus?

Es gibt **genau zwei Vorlagen** (`experiment/prompts/`), eine pro Aufgabentyp. In die
Platzhalter `{…}` werden Sprache, Aufgabentext und Code-Gerüst eingesetzt.

### 3.1 Vorlage für EB-Aufgaben (`template_function.txt`)

```text
Solve the following programming problem in {language}.

Complete the code skeleton given below. Your code will be combined with a test harness
that reads the input, calls your method, and prints the result. Therefore, do not read
from standard input, do not write to standard output, and do not add a main function.

Requirements:
- Return the complete `Solution` class, including any import or include statements it needs.
- Use only the {language} standard library.
- Do not use multiple threads or processes.
- {language_note}
- Respond with exactly one fenced code block containing the code, and nothing else.

Problem:

{problem}

Code skeleton:

```{fence}
{starter}
```
```

Das **Code-Gerüst** (`{starter}`) kommt aus EffiBench-X, z. B. für EB01 in Java:

```java
class Solution {
    public long maximumTotalDamage(int[] power) {

    }
}
```

### 3.2 Vorlage für CLBG-Aufgaben (`template_program.txt`)

```text
Write a complete {language} program that solves the following task.

Requirements:
- The program reads a single integer N from its first command-line argument.
- It writes its result to standard output, exactly in the format specified below.
- Use only the {language} standard library.
- Do not use multiple threads or processes.
- {language_note}
- Respond with exactly one fenced code block containing the code, and nothing else.

Task:

{problem}
```

### 3.3 Was sich zwischen den Sprachen unterscheidet (C11)

Nur drei Dinge – sonst ist der Prompt Wort für Wort gleich:

| | Python | Java | C++ |
|---|---|---|---|
| `{language}` | Python | Java | C++ |
| `{language_note}` | Target Python 3.14 (CPython). | Target Java 25 (OpenJDK). *(CLBG zusätzlich: The public class must be named `Main`.)* | Target C++20. The code is compiled with `g++ -O2 -std=c++20`. |
| Code-Gerüst (nur EB) | Python-Gerüst | Java-Gerüst | C++-Gerüst |

### 3.4 Warum die Prompts so gebaut sind

| Regel im Prompt | Warum |
|---|---|
| **Kein Wort über Effizienz oder Energie** | Wir wollen messen, wie effizient der Code *normalerweise* ist – nicht, wie gut ein LLM optimiert, wenn man es darum bittet (das wäre „Prompting“-Forschung, siehe Future Work). |
| **Zero-shot** (keine Beispiellösung) | Gleiche Bedingungen für alle LLMs, keine Beeinflussung durch unsere Beispiele |
| **Nur Standardbibliothek** | Keine Abhängigkeiten, die auf einer Plattform fehlen; kein „Schummeln“ mit NumPy o. Ä. |
| **Keine Threads/Prozesse** | Sonst misst man, wie viele Kerne eine Plattform hat, nicht wie gut der Code ist |
| **Sprachversion und Compiler-Flags genannt** | Das LLM soll wissen, welche Sprachfeatures es nutzen darf |
| **Genau ein Codeblock, sonst nichts** | Wir können den Code automatisch herausziehen, ohne zu raten |
| **Code wird nicht repariert** | Was das LLM liefert, wird so gemessen; fehlerhafte Programme zählen als falsch |

Alle **42 fertigen Prompts** (14 Aufgaben × 3 Sprachen) liegen in
`experiment/prompts/rendered/<Aufgabe>/<sprache>.txt` und sind mit SHA-256 gesichert (C12).
Die Vorlagen werden im Paper-Anhang **direkt aus diesen Dateien** eingebunden (C13), damit
Paper und Experiment nie auseinanderlaufen.

## 4. Wie wurden die Prompts an die LLMs geschickt?

- Über die **offiziellen Kommandozeilen-Tools** der Hersteller: Claude Code, Codex CLI,
  Antigravity CLI (`experiment/generate/generate.py`, Anleitung in `generate/ANLEITUNG.md`).
- **Nicht interaktiv**, in einem **leeren Ordner**, Werkzeuge (Dateien schreiben, Befehle
  ausführen) **aus- bzw. weggesperrt**, Aufwand („effort“) jeweils **medium**.
- Jede Kombination wurde **5-mal unabhängig** angefragt (`s1`–`s5`), weil LLMs bei
  gleicher Frage unterschiedlich antworten.
- Ergebnis: alle 630 Anfragen lieferten genau einen Codeblock. Gespeichert unter
  `experiment/generated/<llm>/<Aufgabe>/<sprache>/s<k>/` (Antwort, Code, Metadaten).

## 5. Was danach mit dem Code passiert

1. **Bauen** (Java/C++ kompilieren).
2. **Korrektheit prüfen:** EB – 30 Testfälle + große Eingabe muss das Gleiche liefern wie
   die Referenz; CLBG – offizielle Prüfausgabe + große Eingabe.
3. **Messen:** nur korrekte Programme, 3 Wiederholungen, Energie, Zeit, Speicher.

Bisher: Laptop 629/630 korrekt, Mac 628/630 (E18–E20).

## 6. Bekannte Schwächen (für die Diskussion)

- **Kontamination (C10):** Alle EB-Aufgaben sind von 2023/24 und öffentlich – die LLMs
  kennen sie wahrscheinlich. Das betrifft eher absolute Werte als den Vergleich der LLMs
  untereinander, weil alle gleich betroffen sind.
- **Wenige Aufgaben:** 14 Aufgaben decken nicht alle Arten von Software ab (keine
  Web-, I/O- oder Datenbank-Programme).
- **Ein Prompt-Stil:** Andere Formulierungen könnten andere Ergebnisse liefern.
