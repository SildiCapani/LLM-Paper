# Anleitung: Generierten Code ausführen und Energie messen

Diese Anleitung beschreibt den Weg von den 630 generierten Programmen bis zu den Messwerten auf
allen Plattformen. Details zum Messskript selbst stehen in `measure/ANLEITUNG.md`.

> **Stand 28.10.2026:** Die Generierung ist abgeschlossen (630/630 `ok`, 0 Werkzeugaufrufe).
> Einige Schritte unten brauchen noch Skripte, die **noch nicht gebaut** sind. Sie sind mit
> 🛠 markiert. Alles mit ✅ funktioniert schon.

---

## Der Ablauf im Überblick

```
1. Bauen & testen      2. Workload festlegen   3. Jobs-Datei        4. Messen              5. Auswerten
(einmal, Linux-PC)     (Pilot, einmal)         (pro Plattform)      (auf JEDER Plattform)  (einmal)
generated/ ──► nur korrekte ──► große Eingabe ──► jobs/*.json ──► results/<plattform>_*.csv ──► Statistik
               Programme        pro Aufgabe
```

| Schritt | Wo? | Was passiert? | Stand |
|---|---|---|---|
| 1. Bauen & testen | einmal auf dem Linux-Laptop | Java und C++ kompilieren, jedes Programm gegen die Testfälle prüfen. Nur **korrekte** Programme werden gemessen. | 🛠 |
| 2. Workload | einmal (Pilot) | Pro Aufgabe **eine** große Eingabe festlegen, die bei allen gleich ist (z. B. ≥ 5 s Laufzeit) | 🛠 (CLBG: N steht fest, EB: noch nicht) |
| 3. Jobs-Datei | pro Plattform | Liste aller zu messenden Programme für `measure.py` | 🛠 |
| 4. Messen | auf jeder Plattform | `measure.py run …`, Ergebnis als CSV | ✅ Linux, ⚠️ Mac ungetestet, 🛠 Pi, ❌ Windows |
| 5. Auswerten | einmal | Mixed-Effects-Modell, Rangvergleiche (RQ1–RQ5) | 🛠 |

**Wichtig:** Korrektheit wird **einmal** geprüft, nicht auf jeder Plattform. Gemessen wird dann auf
allen Plattformen **dieselbe Liste** korrekter Programme mit **derselben Eingabe**.

---

## Schritt 0: Projekt auf die Plattform bringen (jede Plattform)

Der generierte Code liegt **nicht in Git** (siehe `.gitignore`). Deshalb zwei Teile kopieren:

```bash
# 1. Projekt holen
git clone <repo-url> LLM-Paper

# 2. Generierten Code vom Laptop kopieren (ca. 17 MB), z. B. per scp/rsync oder USB-Stick
rsync -a smartrollerz@<laptop-ip>:~/Documents/LLM-Paper/experiment/generated/ LLM-Paper/experiment/generated/
```

Auf **jeder** Plattform werden dieselben Versionen der Sprachen benötigt (Python, Java, C++-Compiler).
Geplant ist dafür ein gemeinsames Docker-Image (amd64 + arm64), damit überall exakt dieselben
Versionen laufen. 🛠 Das Image ist noch nicht gebaut.

| Sprache | Version (geplant, siehe Paper, Plattform-Tabelle in §5) |
|---|---|
| Python | CPython 3.14 |
| Java | OpenJDK 25 |
| C++ | GCC 14, `-O2 -std=c++20` |

---

## Schritt 1–3 (einmal): Bauen, testen, Jobs erzeugen 🛠

Diese Schritte laufen einmal auf dem Linux-Laptop. Geplante Befehle (Skripte folgen):

```bash
cd ~/Documents/LLM-Paper/experiment
python3 check/check.py        # 🛠 kompilieren + testen → generated/correctness.csv
python3 check/make_jobs.py    # 🛠 Jobs-Datei für alle korrekten Programme → measure/jobs/main.json
```

- EffiBench-Aufgaben (EB01–EB10): Der Code ist nur eine Funktion. Er wird mit dem Rahmenprogramm
  aus `tasks/EBxx/runner/` zusammengesetzt und gegen die Testfälle geprüft.
- CLBG-Aufgaben: Die Ausgabe wird mit `tasks/CLBGxx/expected/` verglichen.
- ⚠️ `test_generator.py` und `evaluator.py` stammen aus dem Datensatz und laufen **nur in einer
  Sandbox** (Docker), nie direkt.

---

## Schritt 4: Messen auf den Plattformen

Allgemein für **alle** Plattformen:

- Netzteil anschließen, alle anderen Programme schließen (Browser, Chat, Claude-App, Updates)
- Rechner nicht anfassen, während gemessen wird
- Erst `measure.py check`, dann `measure.py run`
- Ergebnisdateien nach Plattform benennen: `results/<plattform>_main.csv`

Gemessen wird in einer **Messsitzung pro Plattform** mit derselben Jobs-Datei:

```bash
cd LLM-Paper/experiment/measure
python3 measure.py check
python3 measure.py run jobs/main.json --reps 10 --out results/<plattform>_main.csv
```

> Dauer grob geschätzt: ca. 600 korrekte Programme × 10 Wiederholungen × (5 s Lauf + 5 s Pause)
> ≈ **17 Stunden pro Plattform**. Das Skript kann noch nicht fortsetzen, wenn man es abbricht.
> 🛠 Fortsetzen/Aufteilen auf mehrere Abende wird noch eingebaut.

### 4a. Linux-PC / Laptop (Intel/AMD) ✅

Energiequelle: **RAPL** (Zähler im Prozessor). Getestet auf dem i7-1185G7.

```bash
# Vorbereitung (gilt bis zum Neustart)
sudo chmod a+r /sys/class/powercap/intel-rapl:*/energy_uj
sudo cpupower frequency-set -g performance
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo     # nur Intel

# Prüfen und messen
cd LLM-Paper/experiment/measure
python3 measure.py check
python3 measure.py run jobs/main.json --reps 10 --cpus 2 --out results/laptop_main.csv

# Danach zurückstellen
sudo chmod o-r /sys/class/powercap/intel-rapl:*/energy_uj
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
sudo cpupower frequency-set -g powersave
```

Bei **AMD**-Prozessoren heißt der Turbo-Schalter anders:
`echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost`.

### 4b. Server (Linux) ✅ (wie 4a, mit Besonderheiten)

Energiequelle: **RAPL**, auf Servern meist **mit DRAM-Bereich** (Arbeitsspeicher).

- ⚠️ Es muss ein **echter Rechner** sein (bare metal). In einer **virtuellen Maschine oder Cloud-Instanz
  gibt es kein RAPL**. Dann bricht `check` mit „No energy reader available“ ab.
- Man braucht **sudo-Rechte** (für chmod, Governor, Turbo). Sonst den Admin bitten.
- Bei **zwei Prozessoren** (2 Sockel) zeigt `check` `package-0` und `package-1`. Das Programm mit
  `--cpus` auf einen Kern **im Sockel 0** pinnen.
- Während der Messung dürfen **keine anderen Nutzer oder Dienste** Last erzeugen
  (`htop` prüfen, Cronjobs pausieren).

```bash
python3 measure.py check            # erwartet: package-0, (package-1), dram
python3 measure.py run jobs/main.json --reps 10 --cpus 2 --out results/server_main.csv
```

Bitte die Ausgabe von `check` und `lscpu` an mich schicken; dann trage ich den Server ins Paper ein.

### 4c. Mac (Apple Silicon, M4) ⚠️ noch nicht auf echtem Mac getestet

Energiequelle: **powermetrics** (Schätzwerte von Apple, alle 100 ms).

```bash
# Netzteil an, Stromsparmodus aus, andere Programme schließen
sudo -v
cd LLM-Paper/experiment/measure
python3 measure.py check            # erwartet: powermetrics, Bereiche cpu, gpu, ane, combined
sudo -v && caffeinate -i python3 measure.py run jobs/main.json --reps 10 --out results/mac_main.csv
```

- `--cpus` gibt es auf dem Mac nicht.
- `sudo -v` läuft nach einigen Minuten ab. Für eine lange Messung vorher einmalig
  `sudo visudo` → `Defaults timestamp_timeout=600` setzen (oder in Blöcken messen).
- **Beim ersten Mal** die Ausgabe von `check` an mich schicken.

### 4d. Raspberry Pi 5 🛠 Messung noch nicht eingebaut

Energiequelle: **PMIC** (Strom- und Spannungsmesser auf der Platine), abgefragt über `vcgencmd`.

```bash
# Prüfen, ob die Werte lesbar sind (Raspberry Pi OS, 64 Bit)
vcgencmd pmic_read_adc
```

- Der Leser für `energy.py` ist **noch nicht gebaut**. Schick mir die Ausgabe des Befehls oben,
  dann baue ich ihn passend ein.
- Den Pi mit dem **offiziellen 27-W-Netzteil** und **aktivem Kühler** betreiben, sonst drosselt er.
- Governor auf `performance`: `echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
- Ohne Bildschirm/Desktop messen (per SSH), damit der Grundverbrauch klein bleibt.

### 4e. Windows ❌ keine Energiemessung möglich

Windows gibt die RAPL-Zähler **nicht ohne Kernel-Treiber** frei; auch WSL sieht sie nicht.
Optionen:

| Option | Bewertung |
|---|---|
| Windows-Rechner nicht verwenden | Empfohlen. Laut Design nur im Notfall (Entscheidungsprotokoll D2). |
| Linux vom USB-Stick starten (Live-System) und wie 4a messen | Gut, wenn der Rechner als weitere x86-Plattform gebraucht wird |
| Nur Zeit und Speicher messen: `--allow-no-energy` | Nur als Zusatz; keine Energie, also nicht für die Hauptfragen |

---

## Schritt 5: Ergebnisse zurückbringen

Die CSV- und JSON-Dateien aus `measure/results/` von jeder Plattform auf den Laptop kopieren
(gleicher Ordner, Dateinamen mit Plattform-Präfix). Sie sind klein und dürfen in Git.

```bash
rsync -a <plattform>:LLM-Paper/experiment/measure/results/ ~/Documents/LLM-Paper/experiment/measure/results/
```

**Nie** absolute Joule zwischen Plattformen vergleichen: Jede Plattform misst einen anderen Bereich
(Prozessor, Platine, Schätzung). Verglichen werden Rangfolgen und Verhältnisse innerhalb einer Plattform.

---

## Checkliste pro Plattform

| | Linux-Laptop | Server | Mac M4 | Raspberry Pi 5 |
|---|---|---|---|---|
| Projekt + `generated/` kopiert | | | | |
| Gleiche Sprachversionen (Docker) | | | | |
| `measure.py check` ohne WARNING | | | | |
| Governor/Turbo eingestellt | | | – | |
| Andere Programme geschlossen | | | | |
| Messung fertig, CSV zurückkopiert | | | | |
| Einstellungen zurückgestellt | | | – | |

---

## Was noch gebaut werden muss (Reihenfolge)

1. 🛠 **Korrektheitsprüfung** (`check/check.py`): bauen + testen in Docker
2. 🛠 **Workload-Kalibrierung** für EB01–EB10 (große Eingabe pro Aufgabe)
3. 🛠 **Jobs-Erzeugung** (`check/make_jobs.py`) und **Fortsetzen** in `measure.py`
4. 🛠 **Docker-Image** mit festen Sprachversionen (amd64 + arm64)
5. 🛠 **Pi-Leser** in `energy.py` (sobald die `vcgencmd`-Ausgabe vorliegt)
6. 🛠 **Auswertung** (Statistik für RQ1–RQ5)
