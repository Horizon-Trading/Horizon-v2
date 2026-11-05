#pragma once
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace horizon {
struct Statistics { double mean; double sample_stddev; double annualized_volatility; };
struct Simulation {
    Statistics statistics;
    double expected_return;
    double probability_profit;
    double p05;
    double median;
    double p95;
    std::vector<double> histogram_edges;
    std::vector<std::size_t> histogram_counts;
};
Statistics statistics(std::span<const double> returns);
std::vector<Statistics> rolling_statistics(std::span<const double> returns, std::size_t window);
Simulation simulate(std::span<const double> returns, std::size_t paths, std::size_t days, std::uint64_t seed);
}
