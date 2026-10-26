# Anleitung: Energie messen

Dieses Skript misst für jedes Programm **Energie (Joule)**, **Laufzeit (Sekunden)** und
**Speicher (MB)** und schreibt alles in eine CSV-Datei.

| Datei | Was ist das? |
|---|---|
| `measure.py` | Das Messskript |
| `energy.py` | Liest den Energiezähler (Linux: RAPL, Mac: powermetrics) |
| `jobs/*.json` | Liste der Programme, die gemessen werden sollen |
| `test_energy.py` | Selbsttest der Energie-Leser mit simulierten Daten |

Es wird nur Python 3 benötigt, keine Zusatzpakete.

---

## So funktioniert die Messung

```
Leerlauf messen (30 s)  →  Aufwärmlauf je Programm  →  alle Läufe in ZUFÄLLIGER Reihenfolge
(Grundverbrauch)           (nicht gezählt)              jeweils mit 5 s Pause dazwischen
                                                    →  Leerlauf erneut messen (30 s)
```

Für jeden Lauf wird gespeichert:
- `energy_<bereich>_j`: verbrauchte Energie während des Laufs (brutto)
- `net_energy_<bereich>_j`: dasselbe **minus Grundverbrauch**. Dieser Wert zählt für das Paper.
- `wall_s`, `user_s`, `sys_s`: Laufzeit und CPU-Zeit
- `maxrss_mb`: maximaler Arbeitsspeicher
- `stdout_sha256`: Fingerabdruck der Ausgabe. Damit lässt sich prüfen, ob das Programm richtig gerechnet hat.
- `temp_before_c`: CPU-Temperatur vor dem Lauf (nur Linux)

Zusätzlich entsteht eine `.json`-Datei mit Infos zum Rechner (CPU, Betriebssystem, Einstellungen).

---

## Linux (Intel- oder AMD-Laptop/PC/Server)

### 1. Vorbereitung (vor jeder Messsitzung)

```bash
# Energiezähler für normale Benutzer lesbar machen (gilt bis zum Neustart)
sudo chmod a+r /sys/class/powercap/intel-rapl:*/energy_uj

# CPU auf volle, gleichmäßige Leistung stellen
sudo cpupower frequency-set -g performance      # oder: powerprofilesctl set performance

# Turbo-Boost aus (weniger Schwankung; nur bei Intel)
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
```

Außerdem:
- **Netzteil anschließen**, alle anderen Programme schließen (Browser, Chat, Updates)
- Laptop auf einen **harten, kühlen Untergrund** stellen

> 🔒 **Sicherheitshinweis:** Lesbare Energiezähler lassen sich theoretisch für
> Seitenkanal-Angriffe missbrauchen (CVE-2020-8694). Deshalb sind sie standardmäßig nur für Root
> lesbar. Der Befehl oben gilt nur bis zum nächsten Neustart. Nach der Messung kannst du ihn mit
> `sudo chmod o-r /sys/class/powercap/intel-rapl:*/energy_uj` sofort zurücknehmen.

### 2. Prüfen, ob alles bereit ist

```bash
cd experiment/measure
python3 measure.py check
```

So sollte es aussehen (Werte unterscheiden sich):

```
Energy reader: rapl (RAPL counters readable)
  domains: package-0, core, uncore, psys
  idle power over 3 s: package-0=1.20 W, core=0.30 W, uncore=0.05 W, psys=3.10 W
```

Es sollte **keine WARNING** mehr erscheinen. `psys` misst die Leistung der ganzen
Plattform (Chip + Umgebung). `package-0` misst nur den Prozessor.

### 3. Messen

```bash
python3 measure.py run jobs/clbg_reference_python.json --reps 10 --out results/laptop_clbg_ref.csv --cpus 2
```

- `--reps 10`: 10 Wiederholungen pro Programm
- `--cpus 2`: Programme auf CPU-Kern 2 festpinnen (weniger Schwankung)
- `--idle 30`, `--cooldown 5`: Leerlauf- und Pausenzeiten (Standardwerte)

### 4. Danach zurückstellen

```bash
sudo chmod o-r /sys/class/powercap/intel-rapl:*/energy_uj
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
sudo cpupower frequency-set -g powersave        # bzw. vorheriger Modus
```

---

## macOS (Apple Silicon, z. B. M4)

> ⚠️ Die Mac-Version ist **noch nicht auf einem echten Mac getestet**, nur mit simulierten Daten.
> Bitte beim ersten Mal `check` laufen lassen und die Ausgabe zurückmelden.

### 1. Vorbereitung

- **Netzteil anschließen**, „Stromsparmodus“ in den Systemeinstellungen **aus**
- Alle anderen Programme schließen, Spotlight-Indexierung und Time Machine pausieren
- Damit der Mac nicht einschläft, die Messung mit `caffeinate` starten (siehe unten)

```bash
# Einmal das Passwort eingeben, danach darf das Skript powermetrics starten
sudo -v
```

### 2. Prüfen

```bash
cd experiment/measure
python3 measure.py check
```

Erwartet: `Energy reader: powermetrics (powermetrics running)` mit den Bereichen
`cpu, gpu, ane, combined`.

### 3. Messen

```bash
sudo -v && caffeinate -i python3 measure.py run jobs/clbg_reference_python.json --reps 10 --out results/mac_clbg_ref.csv
```

`--cpus` funktioniert auf dem Mac nicht (macOS erlaubt kein Festpinnen auf Kerne).

**Wichtig für das Paper:** `powermetrics` liefert **Schätzwerte** von Apple (Modell-basiert),
keine direkt gemessenen Werte. Sie werden alle 100 ms erfasst. Programme sollten deshalb
mindestens etwa 1 Sekunde laufen. Der Wert `combined` (CPU + GPU + Neural Engine) zählt.

`sudo -v` gilt nur einige Minuten. Bei sehr langen Messungen das Timeout von sudo verlängern
oder `sudo -v` vorher erneut ausführen.

---

## Eigene Programme messen (Jobs-Datei)

Eine Jobs-Datei ist eine Liste von Programmen im JSON-Format:

```json
[
  {
    "id": "CLBG01-python-ref",
    "cmd": ["python3", "-I", "../../tasks/CLBG01/reference/python3.py", "200000"],
    "stdin": null,
    "meta": {"task": "CLBG01", "language": "python", "source": "reference"}
  }
]
```

- `cmd`: der Befehl. Relative Pfade gelten ab dem Ordner der Jobs-Datei.
- `stdin`: optional eine Datei, die dem Programm als Eingabe gegeben wird
- `meta`: beliebige Zusatzinfos. Sie landen als Spalten in der CSV-Datei (z. B. `llm`, `language`, `task`).

Später erzeugt die Pipeline diese Jobs-Datei automatisch für alle generierten Programme.

---

## Selbsttest

```bash
python3 test_energy.py
```

Prüft mit simulierten Daten, ob die Energie korrekt berechnet wird, auch wenn der Zähler
überläuft (Linux) und wenn mehrere Messintervalle überlappen (Mac).

---

## Häufige Probleme

| Meldung | Lösung |
|---|---|
| `RAPL counters are root-only` | Schritt „Vorbereitung“ (chmod) ausführen; nach jedem Neustart erneut |
| `No energy reader available` | Auf diesem System gibt es keinen Energiezähler. Mit `--allow-no-energy` werden nur Zeit und Speicher gemessen. |
| `powermetrics failed (run sudo -v first)` | `sudo -v` ausführen und Passwort eingeben |
| `WARNING: CPU governor is 'powersave'` | `sudo cpupower frequency-set -g performance` |
| Werte schwanken stark | Andere Programme schließen, Netzteil anschließen, Turbo aus, `--cpus` nutzen |
