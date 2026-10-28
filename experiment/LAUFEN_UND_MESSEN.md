# Anleitung: Code ausführen und Energie messen (alle Plattformen)

**Kurz:** Du bekommst **eine ZIP-Datei**, entpackst sie auf der Plattform, startest **einen Befehl**,
und am Ende entsteht **eine Ergebnis-ZIP**, die du mir zurückgibst. Alles dazwischen macht das
Skript: bauen, testen, messen.

```
llm-energy-bundle.zip ──► entpacken ──► python3 run_platform.py run --name <plattform>
                                             │
                     1. bauen (630 Programme + Referenzen)
                     2. Korrektheit prüfen (30 Tests + große Eingabe)
                     3. messen (Energie, Zeit, Speicher), zufällige Reihenfolge
                     4. packen ──► results_<plattform>.zip  ──► an mich zurück
```

| Plattform | Energie-Messung | Stand |
|---|---|---|
| Linux-Laptop/PC (Intel/AMD) | RAPL (Zähler im Prozessor) | ✅ getestet |
| Server (Linux, echter Rechner) | RAPL, meist mit Arbeitsspeicher | ✅ wie Laptop |
| Mac (Apple Silicon, M4) | powermetrics (Schätzwerte von Apple) | ⚠️ auf echtem Mac noch nicht getestet |
| Raspberry Pi 5 | PMIC über `vcgencmd` | ⚠️ eingebaut, auf echtem Pi noch nicht getestet |
| Windows | – | ❌ geht nicht (siehe unten) |

---

## Schritt 1: Programmiersprachen installieren (einmal pro Plattform)

Damit die Plattformen vergleichbar sind, sollen **überall dieselben Versionen** laufen:
**Python 3.14, Java 25 (OpenJDK), GCC 14.** Das Skript prüft die Versionen und warnt, wenn sie
abweichen. Es misst trotzdem und schreibt die Versionen in die Ergebnisse.

**Linux (Ubuntu 24.04, Laptop und Server)**

```bash
sudo apt install g++-14 openjdk-25-jdk
sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.14
```

Falls `openjdk-25-jdk` nicht gefunden wird: Temurin 25 von https://adoptium.net installieren und
beim Start `--java-home /pfad/zum/jdk-25` angeben.

**Raspberry Pi 5 (Raspberry Pi OS 64 Bit, Debian 13)**

```bash
sudo apt install g++-14 openjdk-25-jdk python3
```

Python 3.14 gibt es dort nicht als Paket. Am einfachsten über `uv` (offizielle Installationsanleitung
auf https://docs.astral.sh/uv/), dann `uv python install 3.14` und beim Start
`--python $(uv python find 3.14)` angeben.

**Mac (Homebrew)**

```bash
brew install python@3.14 openjdk@25 gcc@14
```

Beim Start dann `--java-home $(brew --prefix openjdk@25)` angeben. Achtung: `g++` ist auf dem Mac
eigentlich Clang. Das Skript nimmt automatisch `g++-14` von Homebrew.

---

## Schritt 2: Paket entpacken und prüfen

```bash
unzip llm-energy-bundle.zip
cd llm-energy/bench
python3 run_platform.py check
```

`check` zeigt:
- die gefundenen Sprachversionen,
- ob Energie messbar ist,
- wie viel langsamer die Plattform als der Laptop ist,
- **wie lange die Messung ungefähr dauert.**

Es sollte **keine WARNING** zur Energie mehr erscheinen. **Schick mir beim ersten Mal die Ausgabe von
`check`**, vor allem vom Mac und vom Pi.

---

## Schritt 3: Plattform vorbereiten und starten

Allgemein: **Netzteil an, alle anderen Programme zu** (Browser, Chat, Claude-App, Updates), Rechner
während der Messung **nicht benutzen**, Ruhezustand aus.

### Linux-Laptop / PC / Server

```bash
# Vorbereitung (gilt bis zum Neustart)
sudo chmod a+r /sys/class/powercap/intel-rapl:*/energy_uj
sudo cpupower frequency-set -g performance
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo      # Intel; AMD: echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost

# Starten
cd llm-energy/bench
python3 run_platform.py run --name laptop          # Server: --name server

# Danach zurückstellen
sudo chmod o-r /sys/class/powercap/intel-rapl:*/energy_uj
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
sudo cpupower frequency-set -g powersave
```

**Server:** muss ein **echter Rechner** sein (keine VM oder Cloud, dort gibt es kein RAPL). Man braucht
sudo, und niemand sonst darf den Server währenddessen belasten.

> 🔒 Lesbare Energiezähler sind ein kleines Sicherheitsrisiko (CVE-2020-8694). Deshalb nach der
> Messung zurückstellen; spätestens ein Neustart macht es automatisch rückgängig.

### Mac (M4)

```bash
# Stromsparmodus aus, Netzteil an
sudo -v                                            # Passwort einmal eingeben
cd llm-energy/bench
caffeinate -i python3 run_platform.py run --name mac --java-home $(brew --prefix openjdk@25)
```

`powermetrics` wird beim Start einmal mit sudo gestartet und läuft dann durch.

### Raspberry Pi 5

Mit **offiziellem 27-W-Netzteil** und **aktivem Kühler**, am besten **ohne Bildschirm per SSH**:

```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
vcgencmd pmic_read_adc                             # muss Zeilen mit ..._A und ..._V zeigen
cd llm-energy/bench
nohup python3 run_platform.py run --name pi > pi.log 2>&1 &
tail -f pi.log                                     # Fortschritt ansehen (Strg+C beendet nur die Anzeige)
```

`nohup` sorgt dafür, dass die Messung weiterläuft, wenn die SSH-Verbindung abbricht.

### Windows ❌

Windows gibt die Energiezähler nicht ohne Spezialtreiber frei, auch nicht unter WSL. Das Skript
bricht dort ab. Wenn der Rechner unbedingt gebraucht wird: **Linux vom USB-Stick starten**
(Ubuntu Live) und wie beim Linux-Laptop messen.

---

## Unterbrechen und fortsetzen

- **Strg+C** stoppt jederzeit. **Derselbe Befehl** macht dort weiter, wo es aufgehört hat. Fertige
  Messungen werden nie wiederholt.
- Bauen und Testen werden beim Fortsetzen übersprungen, wenn sie schon fertig sind.
- Die Messung über mehrere Abende verteilen ist in Ordnung. Vor jedem Neustart die Vorbereitung
  (chmod, Governor, Turbo) wiederholen, weil ein Neustart sie zurücksetzt.

---

## Was am Ende herauskommt

Im Ordner `llm-energy/` liegt **`results_<name>.zip`**. **Diese Datei schickst du mir.** Darin:

| Datei | Inhalt |
|---|---|
| `environment_*.json` | Rechner, Betriebssystem, Sprachversionen, Energiemessung, Warnungen |
| `build.csv` | Welche Programme sich kompilieren ließen |
| `correctness.csv` | Welche Programme korrekt sind (`pass`) und warum nicht (`wrong`, `too_slow`, …) |
| `runs.csv` | **Die Messwerte**: eine Zeile pro Lauf mit Energie (brutto und netto), Zeit, Speicher |
| `idle.csv` | Grundverbrauch im Leerlauf, alle 30 Minuten gemessen |
| `log.txt` | Protokoll des Ablaufs |

---

## Was das Skript genau tut (fürs Paper)

| Schritt | Details |
|---|---|
| Bauen | EB-Aufgaben: generierte Funktion + Rahmenprogramm aus EffiBench-X + Standard-Imports + Wiederholungsschleife. CLBG: Programm unverändert. C++: `g++ -O2 -std=c++20`, Java: `javac`. |
| Korrektheit | 30 kleine Testfälle pro EB-Aufgabe (aus dem Datensatz-Generator, einmal auf dem Laptop erzeugt) bzw. die offizielle CLBG-Prüfausgabe, danach einmal die große Eingabe. Nur `pass` wird gemessen. |
| Große Eingabe | EB: eine Eingabe an der Obergrenze der Aufgabe, die **R-mal im selben Prozess** gelöst wird. CLBG: Parameter N. R und N sind auf allen Plattformen gleich (kalibriert auf dem Laptop). |
| Messen | Leerlauf 60 s, danach alle Läufe in fester Zufallsreihenfolge, 3 s Pause dazwischen, Leerlauf alle 30 min. Ein Programm, das die Zeitgrenze überschreitet, wird nicht weiter wiederholt. |

---

## Checkliste pro Plattform

| | Laptop | Server | Mac M4 | Pi 5 |
|---|---|---|---|---|
| Python 3.14 / Java 25 / GCC 14 installiert | | | | |
| `check` ohne Energie-WARNING | | | | |
| Ausgabe von `check` an Brisild/Claude geschickt | | | | |
| Governor/Turbo eingestellt | | | – | |
| Messung fertig | | | | |
| `results_<name>.zip` zurückgeschickt | | | | |
| Einstellungen zurückgestellt | | | – | |
