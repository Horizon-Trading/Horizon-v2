#include "horizon.hpp"
#include <algorithm>
#include <cmath>
#include <numeric>
#include <random>
#include <stdexcept>

namespace horizon {
Statistics statistics(std::span<const double> returns) {
    if (returns.size() < 2 || returns.size() > 10000) throw std::invalid_argument("require 2..10000 observations");
    double mean = 0, m2 = 0;
    std::size_t count = 0;
    for (double value : returns) {
        if (!std::isfinite(value) || std::abs(value) > 1) throw std::invalid_argument("invalid daily log return");
        ++count;
        const double delta = value - mean;
        mean += delta / static_cast<double>(count);
        m2 += delta * (value - mean);
    }
    const double sd = std::sqrt(std::max(0.0, m2 / static_cast<double>(count - 1)));
    return {mean, sd, sd * std::sqrt(252.0)};
}

std::vector<Statistics> rolling_statistics(std::span<const double> returns, std::size_t window) {
    if (window < 2 || window > returns.size()) throw std::invalid_argument("invalid rolling window");
    std::vector<Statistics> result;
    result.reserve(returns.size() - window + 1);
    for (std::size_t end = window; end <= returns.size(); ++end) result.push_back(statistics(returns.subspan(end - window, window)));
    return result;
}

Simulation simulate(std::span<const double> returns, std::size_t paths, std::size_t days, std::uint64_t seed) {
    if (paths < 1000 || paths > 100000 || days < 1 || days > 30) throw std::invalid_argument("simulation bounds exceeded");
    const auto stats = statistics(returns);
    std::mt19937_64 rng(seed);
    std::normal_distribution<double> standard_normal(0, 1);
    std::vector<double> terminal(paths);
    std::size_t profitable = 0;
    for (auto& value : terminal) {
        double log_return = 0;
        for (std::size_t day = 0; day < days; ++day) log_return += stats.mean + stats.sample_stddev * standard_normal(rng);
        value = std::expm1(log_return);
        if (!std::isfinite(value)) throw std::overflow_error("nonfinite simulated return");
        if (value > 0) ++profitable;
    }
    const double expected = std::accumulate(terminal.begin(), terminal.end(), 0.0) / static_cast<double>(paths);
    std::sort(terminal.begin(), terminal.end());
    const auto quantile = [&](double probability) {
        const double index = probability * static_cast<double>(paths - 1);
        const auto lower = static_cast<std::size_t>(index);
        const auto upper = std::min(lower + 1, paths - 1);
        return terminal[lower] + (index - static_cast<double>(lower)) * (terminal[upper] - terminal[lower]);
    };
    constexpr std::size_t bins = 20;
    const double low = terminal.front(), high = terminal.back();
    std::vector<double> edges(bins + 1);
    std::vector<std::size_t> counts(bins, 0);
    for (std::size_t i = 0; i <= bins; ++i) edges[i] = low + (high - low) * static_cast<double>(i) / bins;
    for (double value : terminal) {
        const auto bin = high == low ? std::size_t{0} : std::min(bins - 1, static_cast<std::size_t>((value - low) / (high - low) * bins));
        ++counts[bin];
    }
    return {stats, expected, static_cast<double>(profitable) / paths,
            quantile(.05), quantile(.5), quantile(.95), edges, counts};
}
}
