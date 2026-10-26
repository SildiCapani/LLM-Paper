"""Offline tests of the energy readers with simulated hardware data.

Run: python3 test_energy.py
"""
import io
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import energy


def make_zone(root: Path, zone: str, name: str, value: int, max_range: int) -> Path:
    d = root / zone
    d.mkdir()
    (d / "name").write_text(name + "\n")
    (d / "energy_uj").write_text(f"{value}\n")
    (d / "max_energy_range_uj").write_text(f"{max_range}\n")
    return d / "energy_uj"


class RaplReaderTest(unittest.TestCase):
    def test_delta_and_wraparound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = make_zone(root, "intel-rapl:0", "package-0", 1_000_000, 10_000_000)
            psys = make_zone(root, "intel-rapl:1", "psys", 9_500_000, 10_000_000)
            make_zone(root, "intel-rapl-mmio:0", "package-0", 0, 10_000_000)  # duplicate
            with mock.patch.object(energy, "RAPL_ROOT", root):
                reader = energy.RaplReader()
                self.assertEqual(reader.domains, ["package-0", "psys"])
                reader.start()
                pkg.write_text("3500000\n")   # +2.5 J
                psys.write_text("500000\n")   # wraps: 0.5 J to max + 0.5 J = 1.0 J
                result = reader.stop()
        self.assertAlmostEqual(result["package-0"], 2.5)
        self.assertAlmostEqual(result["psys"], 1.0)


POWERMETRICS_SAMPLE = """\
*** Sampled system activity (Sat Oct 25 22:00:00 2026 +0200) (100.12ms elapsed) ***

**** Processor usage ****

CPU Power: 2000 mW
GPU Power: 100 mW
ANE Power: 0 mW
Combined Power (CPU + GPU + ANE): 2100 mW
"""


class PowermetricsParserTest(unittest.TestCase):
    def test_parse_and_integrate(self):
        reader = object.__new__(energy.PowermetricsReader)
        reader.interval_ms = 100
        reader._samples = []
        reader._lock = __import__("threading").Lock()
        reader._proc = mock.Mock(stdout=io.StringIO(POWERMETRICS_SAMPLE * 3))
        reader._consume()
        self.assertEqual(len(reader._samples), 3)
        _, elapsed, watts = reader._samples[0]
        self.assertAlmostEqual(elapsed, 0.10012)
        self.assertEqual(watts, {"cpu": 2.0, "gpu": 0.1, "ane": 0.0, "combined": 2.1})

        # Three back-to-back 0.1 s samples at 2.1 W, interval covers the middle 0.2 s.
        now = time.monotonic()
        reader._samples = [(now - 0.2, 0.1, watts), (now - 0.1, 0.1, watts),
                           (now, 0.1, watts)]
        reader._t0 = now - 0.25
        with mock.patch.object(energy.time, "monotonic", return_value=now - 0.05):
            result = reader.stop()
        self.assertAlmostEqual(result["combined"], 2.1 * 0.2, places=6)
        self.assertAlmostEqual(result["cpu"], 2.0 * 0.2, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
