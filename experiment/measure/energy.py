"""Platform-specific energy readers.

Every reader implements the same interface:

    reader.domains            -> list of domain names, e.g. ["package-0", "psys"]
    reader.start()            -> begin an interval
    reader.stop() -> dict     -> energy in joules per domain for the interval

Linux (Intel/AMD RAPL via /sys/class/powercap) reads cumulative hardware counters
before and after the interval. Raspberry Pi 5 (no RAPL) polls the PMIC via `vcgencmd`. macOS (Apple Silicon) samples `powermetrics` in the
background and integrates the reported power over the interval. `NullReader` measures
nothing and is used when no energy interface is available (time/memory only).
"""
from __future__ import annotations

import glob
import os
import platform
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

RAPL_ROOT = Path("/sys/class/powercap")


class NullReader:
    name = "none"
    domains: list[str] = []

    def start(self) -> None:
        pass

    def stop(self) -> dict[str, float]:
        return {}


class RaplReader:
    """Intel/AMD RAPL counters (microjoules) exposed by the powercap framework."""

    name = "rapl"

    def __init__(self) -> None:
        self._zones: list[tuple[str, Path, int]] = []
        seen = set()
        for zone in sorted(glob.glob(str(RAPL_ROOT / "intel-rapl:*"))):
            zone = Path(zone)
            name = (zone / "name").read_text().strip()
            if name in seen:  # mmio duplicates of package domains
                continue
            seen.add(name)
            max_range = int((zone / "max_energy_range_uj").read_text())
            self._zones.append((name, zone / "energy_uj", max_range))
        if not self._zones:
            raise RuntimeError("no RAPL zones under /sys/class/powercap")
        self._read()  # raises PermissionError if counters are root-only
        self.domains = [z[0] for z in self._zones]
        self._before: list[int] = []

    def _read(self) -> list[int]:
        return [int(path.read_text()) for _, path, _ in self._zones]

    def start(self) -> None:
        self._before = self._read()

    def stop(self) -> dict[str, float]:
        after = self._read()
        result = {}
        for (name, _, max_range), b, a in zip(self._zones, self._before, after):
            delta = a - b if a >= b else a + max_range - b  # one counter wrap
            result[name] = delta / 1e6
        return result


class PowermetricsReader:
    """Apple Silicon power estimates from `powermetrics` (requires sudo).

    `powermetrics` prints one block per sampling interval containing lines such as
    "CPU Power: 1234 mW" and "Combined Power (CPU + GPU + ANE): 1500 mW". A background
    thread timestamps each completed block; stop() integrates all samples that overlap
    the measured interval. Accuracy is limited by the interval length, so measured runs
    should last at least about one second.
    """

    name = "powermetrics"
    domains = ["cpu", "gpu", "ane", "combined"]
    _patterns = {
        "cpu": re.compile(r"^CPU Power:\s*([\d.]+)\s*mW"),
        "gpu": re.compile(r"^GPU Power:\s*([\d.]+)\s*mW"),
        "ane": re.compile(r"^ANE Power:\s*([\d.]+)\s*mW"),
        "combined": re.compile(r"^Combined Power \(CPU \+ GPU \+ ANE\):\s*([\d.]+)\s*mW"),
    }
    _elapsed = re.compile(r"\(([\d.]+)ms elapsed\)")

    def __init__(self, interval_ms: int = 100) -> None:
        self.interval_ms = interval_ms
        self._proc = subprocess.Popen(
            ["sudo", "-n", "powermetrics", "--samplers", "cpu_power",
             "-i", str(interval_ms)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        # (end_time, elapsed_s, {domain: watts})
        self._samples: list[tuple[float, float, dict[str, float]]] = []
        self._lock = threading.Lock()
        threading.Thread(target=self._consume, daemon=True).start()
        deadline = time.monotonic() + 5
        while not self._samples:
            if self._proc.poll() is not None:
                raise RuntimeError("powermetrics failed (run `sudo -v` first): "
                                   + self._proc.stderr.read().strip())
            if time.monotonic() > deadline:
                raise RuntimeError("powermetrics produced no samples within 5 s")
            time.sleep(0.05)
        self._t0 = 0.0

    def _consume(self) -> None:
        current: dict[str, float] = {}
        elapsed = self.interval_ms / 1000
        for line in self._proc.stdout:
            line = line.strip()
            if line.startswith("*** Sampled system activity"):
                m = self._elapsed.search(line)
                elapsed = float(m.group(1)) / 1000 if m else self.interval_ms / 1000
                current = {}
                continue
            for domain, pattern in self._patterns.items():
                m = pattern.match(line)
                if m:
                    current[domain] = float(m.group(1)) / 1000
            if "combined" in current and len(current) >= 2:
                with self._lock:
                    self._samples.append((time.monotonic(), elapsed, dict(current)))
                current = {}

    def start(self) -> None:
        self._t0 = time.monotonic()

    def stop(self) -> dict[str, float]:
        t1 = time.monotonic()
        # Wait until the sample covering t1 has been emitted.
        deadline = t1 + 3 * self.interval_ms / 1000 + 1
        while time.monotonic() < deadline:
            with self._lock:
                if self._samples and self._samples[-1][0] >= t1:
                    break
            time.sleep(self.interval_ms / 4000)
        energy = {d: 0.0 for d in self.domains}
        with self._lock:
            samples = list(self._samples)
        for end, elapsed, watts in samples:
            begin = end - elapsed
            overlap = min(end, t1) - max(begin, self._t0)
            if overlap > 0:
                for d, w in watts.items():
                    energy[d] += w * overlap
        return energy

    def close(self) -> None:
        self._proc.terminate()


class PmicReader:
    """Raspberry Pi 5 power-management IC via `vcgencmd pmic_read_adc`.

    The command prints one current ("..._A current(i)=x A") and one voltage
    ("..._V volt(j)=y V") per supply rail. A background thread polls it continuously;
    board power is the sum of current x voltage over all rails that report both. stop()
    integrates the samples (piecewise constant) over the interval. Rails before the PMIC
    (e.g. USB-C input losses) are not covered, and the polling itself costs some CPU,
    which is part of the idle baseline as well.
    """

    name = "pmic"
    domains = ["board"]
    _line = re.compile(r"^\s*(\S+)_([AV])\s+(?:current|volt)\(\d+\)=([\d.]+)[AV]")

    def __init__(self) -> None:
        self._samples: list[tuple[float, float]] = []  # (monotonic time, watts)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        watts = self._read()
        if watts is None:
            raise RuntimeError("vcgencmd pmic_read_adc gave no usable output")
        threading.Thread(target=self._poll, daemon=True).start()
        self._t0 = 0.0

    @classmethod
    def parse(cls, text: str) -> float | None:
        amps, volts = {}, {}
        for line in text.splitlines():
            m = cls._line.match(line)
            if m:
                (amps if m.group(2) == "A" else volts)[m.group(1)] = float(m.group(3))
        rails = set(amps) & set(volts)
        return sum(amps[r] * volts[r] for r in rails) if rails else None

    def _read(self) -> float | None:
        p = subprocess.run(["vcgencmd", "pmic_read_adc"], capture_output=True, text=True)
        return self.parse(p.stdout) if p.returncode == 0 else None

    def _poll(self) -> None:
        while not self._stop.is_set():
            watts = self._read()
            if watts is not None:
                with self._lock:
                    self._samples.append((time.monotonic(), watts))
                    if len(self._samples) > 200_000:
                        del self._samples[:100_000]

    def start(self) -> None:
        self._t0 = time.monotonic()

    def stop(self) -> dict[str, float]:
        t1 = time.monotonic()
        deadline = t1 + 1.0
        while time.monotonic() < deadline:  # wait for one sample after t1
            with self._lock:
                if self._samples and self._samples[-1][0] >= t1:
                    break
            time.sleep(0.01)
        with self._lock:
            samples = list(self._samples)
        energy = 0.0
        for (ta, wa), (tb, _) in zip(samples, samples[1:]):
            overlap = min(tb, t1) - max(ta, self._t0)
            if overlap > 0:
                energy += wa * overlap
        return {"board": energy}

    def close(self) -> None:
        self._stop.set()


def detect_reader(prefer: str = "auto"):
    """Return the best available energy reader and a note explaining the choice."""
    system = platform.system()
    if prefer in ("auto", "rapl") and system == "Linux" and glob.glob(
            str(RAPL_ROOT / "intel-rapl:*")):
        try:
            return RaplReader(), "RAPL counters readable"
        except PermissionError:
            note = ("RAPL counters are root-only; see ANLEITUNG.md "
                    "(sudo chmod a+r ...energy_uj)")
            if prefer == "rapl":
                raise RuntimeError(note)
        except RuntimeError as e:
            note = str(e)
            if prefer == "rapl":
                raise
    elif prefer in ("auto", "pmic") and system == "Linux" and shutil.which("vcgencmd"):
        try:
            return PmicReader(), "Raspberry Pi PMIC via vcgencmd"
        except RuntimeError as e:
            note = str(e)
            if prefer == "pmic":
                raise
    elif prefer in ("auto", "powermetrics") and system == "Darwin":
        try:
            return PowermetricsReader(), "powermetrics running"
        except RuntimeError as e:
            note = str(e)
            if prefer == "powermetrics":
                raise
    else:
        note = f"no supported energy interface on {system}"
    if prefer not in ("auto", "none"):
        raise RuntimeError(note)
    return NullReader(), note


def platform_info() -> dict[str, str]:
    info = {
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "cpu_count": str(os.cpu_count()),
    }
    if info["system"] == "Linux":
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith("model name"):
                    info["cpu"] = line.split(":", 1)[1].strip()
                    break
        except OSError:
            pass
        gov = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        if gov.exists():
            info["governor"] = gov.read_text().strip()
        no_turbo = Path("/sys/devices/system/cpu/intel_pstate/no_turbo")
        if no_turbo.exists():
            info["turbo"] = "off" if no_turbo.read_text().strip() == "1" else "on"
    elif info["system"] == "Darwin":
        try:
            info["cpu"] = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                         capture_output=True, text=True).stdout.strip()
        except OSError:
            pass
    return info


def cpu_temperature() -> float | None:
    """Highest CPU-related thermal zone temperature in deg C (Linux only)."""
    temps = []
    for zone in glob.glob("/sys/class/thermal/thermal_zone*"):
        try:
            kind = Path(zone, "type").read_text().strip().lower()
            if any(k in kind for k in ("x86_pkg", "cpu", "soc", "tcpu")):
                temps.append(int(Path(zone, "temp").read_text()) / 1000)
        except (OSError, ValueError):
            continue
    return max(temps) if temps else None
