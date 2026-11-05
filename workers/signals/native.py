import json
import math
from pathlib import Path
import subprocess


def engine_path() -> Path:
    from config import settings
    if settings.quant_engine_path:
        return Path(settings.quant_engine_path).resolve()
    root = Path(__file__).resolve().parents[2] / "build" / "engine"
    candidates = [root / "Release" / "horizon_quant.exe", root / "horizon_quant", root / "horizon_quant.exe"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Build horizon_quant or configure QUANT_ENGINE_PATH")


def run_quant(returns: list[float], paths: int = 10000, days: int = 5, seed: int = 42) -> dict:
    if not 2 <= len(returns) <= 10000 or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or abs(x) > 1 for x in returns):
        raise ValueError("Invalid daily log-return observations")
    if not 1000 <= paths <= 100000 or not 1 <= days <= 30 or not 0 <= seed < 2**64:
        raise ValueError("Invalid simulation bounds")
    payload = f"{len(returns)} {paths} {days} {seed}\n" + " ".join(map(str, returns)) + "\n"
    result = subprocess.run([str(engine_path())], input=payload, text=True,
                            capture_output=True, timeout=30, check=True)
    output = json.loads(result.stdout)
    for key in ("expected_return", "probability_profit", "annualized_volatility", "p05", "median", "p95"):
        if not isinstance(output[key], (float, int)) or not math.isfinite(output[key]):
            raise ValueError("Invalid native model output")
    if not 0 <= output["probability_profit"] <= 1:
        raise ValueError("Invalid native probability")
    return {**output, "paths": paths, "horizon_days": days, "seed": seed, "observations": len(returns),
            "assumptions": "IID normal daily log returns fitted to prior completed sessions. Historical drift is noisy; no news causality, fees or slippage modeled. Model probabilities are not calibrated forecasts."}
