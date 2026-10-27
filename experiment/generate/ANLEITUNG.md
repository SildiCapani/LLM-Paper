# Anleitung: Code generieren mit Claude Code, Codex CLI und Antigravity CLI (Gemini)

> **Hinweis:** Die Gemini CLI funktioniert seit dem 18.06.2026 nicht mehr mit privaten Google-Konten
> (auch nicht mit Google AI Pro). Google hat sie durch die **Antigravity CLI** (`agy`) ersetzt.
> Im Skript heißt das Werkzeug weiterhin `gemini`, weil es um die Gemini-Modelle geht.

Das Skript `generate.py` schickt die 42 Prompts je 5-mal an alle drei KI-Werkzeuge, insgesamt
630 Anfragen, und zwar für alle unter **exakt denselben Bedingungen**. Die Regeln dahinter stehen
im Entscheidungsprotokoll (`notes/entscheidungsprotokoll.md`, Abschnitt F).

| Datei | Was ist das? |
|---|---|
| `generate.py` | Das Generierungsskript |
| `config.json` | Einstellungen: Modelle, Befehle, Zeitlimits, Wiederholungen |
| `homes/` | **Eigene Konfigurationsordner der drei CLIs** mit euren Login-Daten. ⚠️ Niemals teilen oder in Git einchecken (steht in `.gitignore`). |
| `../generated/` | Ergebnisse: generierter Code, Rohantworten, Protokolle |

---

## Was das Skript automatisch für gleiche Bedingungen tut

| Regel | Umsetzung |
|---|---|
| Neue Sitzung pro Anfrage | Jeder Aufruf ist ein eigener, nicht-interaktiver CLI-Start ohne Verlauf |
| Kein Projektkontext | Jede Anfrage läuft in einem **neuen, leeren Ordner in `/tmp`**, außerhalb des Projekts |
| Keine persönlichen Einstellungen | Jedes CLI nutzt **nur seinen Ordner in `homes/`**, nicht deine normale Installation |
| Gleicher Prompt | Wird aus `prompts/rendered/` gelesen und über die SHA-256-Prüfsumme kontrolliert |
| Keine Werkzeuge | Claude: `--tools ""`; Codex: Websuche, Shell, Bildgenerierung, Browser, Plugins per `--disable` aus, nur Leserechte; Antigravity: `--sandbox`, Dateizugriff nur im leeren Ordner. Alle Werkzeugaufrufe werden protokolliert. |
| Feste Reihenfolge | Alle 630 Anfragen in einer festen, zufälligen Reihenfolge (`generated/plan.json`) |
| Ehrliche Wiederholungen | Nur bei technischen Fehlern; „kein Code“ ist ein endgültiges Ergebnis |
| Alles wird gespeichert | Rohantwort, Code, Modell, Version, Tokens, Werkzeugaufrufe, Zeitstempel |

---

## Schritt 1: CLIs installieren (einmalig)

Node.js ist bei dir schon installiert (über nvm). Die Versionen werden **fest** installiert,
damit sich das Werkzeug während der Erhebung nicht ändert:

```bash
npm install -g @anthropic-ai/claude-code@2.1.311 @openai/codex@0.164.0
```

Die **Antigravity CLI** gibt es nicht über npm, sondern über Googles offizielles Installationsskript.
Es installiert das Programm nach `~/.local/bin/agy`:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Prüfen:

```bash
claude --version && codex --version && agy --version
```

> Diese Versionen nicht aktualisieren, bis alle 630 Anfragen fertig sind. Bei einem Update
> würde ein anderes Werkzeug gemessen.

## Schritt 2: Experiment-Konfiguration anlegen (einmalig)

```bash
cd ~/Documents/LLM-Paper/experiment/generate
python3 generate.py setup
```

Das legt `homes/claude`, `homes/codex` und `homes/gemini` an.

## Schritt 3: In jedem CLI anmelden (einmalig, macht ihr selbst)

Wichtig: **Immer mit der Variable davor starten**, damit der Login im Experiment-Ordner landet
und nicht in deiner normalen Installation.

**Claude Code** (mit dem Claude-Pro-Konto):

```bash
CLAUDE_CONFIG_DIR=$PWD/homes/claude claude
```

Im Programm `/login` eingeben, „Claude account with subscription“ wählen und im Browser bestätigen.
Danach mit `/exit` beenden.

**Codex CLI** (mit dem ChatGPT-Konto):

```bash
CODEX_HOME=$PWD/homes/codex codex login
```

Den Login im Browser bestätigen.

**Antigravity CLI** (mit dem Google-Konto, auf dem Google AI Pro läuft):

```bash
mkdir -p /tmp/agy-login && cd /tmp/agy-login && HOME=$OLDPWD/homes/gemini agy; cd -
```

Beim ersten Start fragt `agy` nach Farbschema und Darstellung (egal was) und ob du dem Ordner vertraust
(ja; das ist nur ein leerer Login-Ordner). Danach öffnet sich der Browser für den Google-Login.
Anschließend mit `/exit` (oder Strg+C) beenden.

> Die Antigravity CLI speichert den Login im **Schlüsselbund des Betriebssystems**, nicht in
> `homes/gemini`. Getrennt sind nur ihre Einstellungen. Das ist für das Experiment in Ordnung.

## Schritt 4: Modelle festlegen

**Codex:** Nachsehen, welches das beste verfügbare Modell ist:

```bash
CODEX_HOME=$PWD/homes/codex codex
```

Im Programm `/model` eingeben. Den Namen des stärksten Modells notieren (z. B. `gpt-6.1-sol`)
und in `config.json` bei `"codex"` → `"model"` eintragen (statt `null`).

**Gemini (Antigravity):** Die verfügbaren Modelle anzeigen:

```bash
HOME=$PWD/homes/gemini agy models
```

Das stärkste Gemini-Modell (z. B. „Gemini 4 Argon“, genaue Schreibweise aus der Liste) in
`config.json` bei `"gemini"` → `"model"` eintragen (statt `null`).

**Claude:** `claude-opus-5-5` ist schon eingetragen.

> ✅ **Codex:** `gpt-6.1-sol` ist eingetragen (Stand 27.10.2026; Liste aller Modelle:
> `CODEX_HOME=$PWD/homes/codex codex debug models`).
> ✅ **Gemini:** `gemini-4-argon-medium` ist eingetragen (Stand 27.10.2026).
> **Effort:** Alle drei Werkzeuge laufen mit derselben Denk-Stufe **„medium“** (`reasoning_effort` in
> `config.json`). Bei Antigravity steckt die Stufe im Modellnamen, deshalb das `-medium`.
> Für Codex also ein Modell **ohne** Stufe im Namen eintragen; die Stufe setzt das Skript.

## Schritt 5: Probe (Überprüfung der Isolation)

```bash
python3 generate.py versions
python3 generate.py probe
```

Jedes Werkzeug wird gefragt, welches Modell es ist, ob es zusätzliche Anweisungen hat und welche
Werkzeuge es sieht. **Schick mir die Ausgabe.** Dann prüfe ich, ob

- die Isolation greift (keine CLAUDE.md, AGENTS.md oder GEMINI.md, keine Memory),
- die Werkzeuge wirklich aus sind,
- die JSON-Ausgabe der echten CLIs richtig gelesen wird.

Die Probe-Ergebnisse landen in `generated/_probe/` und sind **keine** Studiendaten.

> ✅ **Probe am 27.10.2026 bestanden:** keine Kontextdateien, leerer Arbeitsordner, 0 Werkzeugaufrufe.
> Codex und Antigravity haben trotzdem noch einige Werkzeuge (z. B. Sub-Agenten, bei Antigravity
> auch Websuche), die sich nicht abschalten lassen. Darum zählt das Skript jeden Werkzeugaufruf
> (`tool_calls` in `meta.json` und `requests_log.csv`).

## Schritt 6: Pilotlauf (18 Anfragen)

Zwei Aufgaben × 3 Sprachen × 3 Werkzeuge × 1 Durchlauf:

```bash
python3 generate.py run --tasks EB03 CLBG01 --samples 1
```

Danach den Stand prüfen:

```bash
python3 generate.py status
```

## Schritt 7: Hauptlauf (alle 630 Anfragen)

```bash
python3 generate.py run
```

- **Unterbrechen ist kein Problem** (Strg+C). Beim nächsten Start macht das Skript dort weiter,
  wo es aufgehört hat. Fertige Anfragen werden nie wiederholt.
- **Bei einem Nutzungslimit** pausiert das Skript das betroffene Werkzeug und macht mit den
  anderen weiter. Später einfach denselben Befehl erneut starten.
- **Möglichst in einem kurzen Zeitraum** (z. B. innerhalb von 1–2 Wochen) fertig werden.

Den Laptop dabei nicht in den Ruhezustand gehen lassen. Die Generierung braucht keine
Messbedingungen: Andere Programme dürfen nebenher laufen.

---

## Wo landen die Ergebnisse?

```
generated/
├── plan.json                 feste Reihenfolge aller 630 Anfragen
├── requests_log.csv          eine Zeile pro Anfrage (Status, Dauer, Modell, Werkzeugaufrufe)
├── session_*.json            CLI-Versionen pro Sitzung
├── _probe/                   Probe-Anfragen (keine Studiendaten)
└── <tool>/<Aufgabe>/<Sprache>/s<Nr>/
    ├── code.<py|java|cpp>    der extrahierte Code (erster Codeblock)
    ├── response.md           die komplette Antwort des Modells
    ├── stdout.raw            die rohe JSON-Ausgabe des CLIs
    ├── stderr.txt            Fehlermeldungen des CLIs
    └── meta.json             alle Metadaten (Status, Modell, Version, Tokens, Versuche …)
```

**Status-Werte:**

| Status | Bedeutung | Wird wiederholt? |
|---|---|---|
| `ok` | Antwort mit Code erhalten | nein |
| `no_code` | Antwort ohne Codeblock, zählt als Fehlschlag | nein |
| `rate_limited` | Nutzungslimit erreicht | ja, beim nächsten Start |
| `technical_error` | Absturz, Timeout oder leere Antwort (nach 2 Wiederholungen) | ja, beim nächsten Start |

---

## Häufige Probleme

| Problem | Lösung |
|---|---|
| `No model configured for 'codex'` | Schritt 4: Modell in `config.json` eintragen |
| `command not found: claude` (o. ä.) | Schritt 1 wiederholen; prüfen, ob `npm`-Programme im `PATH` liegen |
| `command not found: agy` | `~/.local/bin` fehlt im `PATH`: `export PATH=$HOME/.local/bin:$PATH` (oder Terminal neu öffnen) |
| `authentication required` (agy) | Login in Schritt 3 wiederholen |
| „This client is no longer supported for Gemini Code Assist“ | Das ist die alte Gemini CLI. Stattdessen `agy` verwenden (Schritt 1) |
| Probe meldet „nicht angemeldet“ | Schritt 3 für dieses Werkzeug wiederholen, **mit** der Variable davor |
| Viele `rate_limited` | Abo-Limit erreicht: einige Stunden warten und denselben Befehl erneut starten |
| `Prompt … does not match its SHA-256` | Ein Prompt wurde verändert. Das darf während der Erhebung nicht passieren. |
