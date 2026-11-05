import math
import unittest
from pathlib import Path
from unittest.mock import patch
from signals.native import run_quant


class NativeTests(unittest.TestCase):
    def test_invalid_input_is_rejected_before_process_launch(self):
        with self.assertRaises(ValueError):
            run_quant([float("nan"), .01])
        with self.assertRaises(ValueError):
            run_quant([.01, .02], paths=1000000)

    def test_compiled_engine_matches_known_constant_return(self):
        root = Path(__file__).resolve().parents[2] / "build" / "engine"
        binary = next((path for path in (root / "Release/horizon_quant.exe", root / "horizon_quant", root / "horizon_quant.exe") if path.exists()), None)
        if binary is None:
            self.skipTest("Build the C++ engine first to run native integration")
        with patch("signals.native.engine_path", return_value=binary):
            result = run_quant([.01] * 20, paths=1000)
        self.assertAlmostEqual(result["expected_return"], math.expm1(.05), places=12)
        self.assertEqual(result["probability_profit"], 1)
        self.assertEqual(sum(result["histogram_counts"]), 1000)
