# Horizon quantitative engine

Build from the repository root (C++20 compiler and CMake 3.20+):

```sh
cmake -S engine -B build/engine
cmake --build build/engine --config Release
ctest --test-dir build/engine -C Release --output-on-failure
```

Run `build/engine/Release/horizon_benchmark.exe` on Windows multi-config builds,
or `build/engine/horizon_benchmark` on Linux. A local MSVC Release run simulated
100,000 paths of 20 sessions in approximately 33 ms; this is a measurement on one
development machine, not a performance guarantee.

The stateless C++ API in `include/horizon.hpp` calculates sample statistics,
rolling statistics, annualized volatility, and seeded Monte Carlo outcomes.
The `horizon_quant` executable reads `count paths horizon_days seed` followed by
daily log returns from stdin and emits JSON. Python invokes it without a shell,
with bounded input and a timeout. Set `QUANT_ENGINE_PATH` for a custom location.

Monte Carlo fits the sample mean and standard deviation of prior completed
daily log returns, draws independent normal log returns, and compounds over the
configured horizon. The output includes mean terminal return, profit frequency,
5th/50th/95th percentiles, a histogram, and rolling five-session volatility.
Seeds reproduce results with the same C++ standard-library implementation;
normal-distribution sequences need not match across compiler vendors.

This is a historical-return model, not evidence that news causes price changes.
Twenty observations give a noisy drift estimate. IID normal returns omit fat
tails, changing regimes, fees, slippage and liquidity. Model probabilities are
not calibrated forecasts. The signal combines 20% keyword attention and 80%
model profit frequency; its confidence field is explicitly history count / 60,
not probability of being correct. Baseline signals remain watch-only when
history is insufficient. Actual paper-entry rules add independent risk checks.

Market features use split-adjusted IEX data, not consolidated market volume.
Only sessions strictly before the New York capture date are used, including
when capture occurs after market close. Relative volume compares the last full
session with the preceding 20 full sessions. Return and benchmark adjustment
use aligned close-to-close sessions. Volatility is sample standard deviation
of 20 daily log returns multiplied by sqrt(252). Market cap/float stay null.

To explicitly enrich already stored events and record updated signal analysis:

```sh
cd workers
uv run python -m core.reanalyze --limit 40
```

This reuses original snapshot capture cutoffs and does not fetch historical news.
Recovered/reanalyzed observations are not fresh live-trading signals merely
because their analysis was updated. Trading must check original event age and
observed price freshness.
