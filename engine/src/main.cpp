#include "horizon.hpp"
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

int main() {
    try {
        std::size_t count, paths, days;
        std::uint64_t seed;
        if (!(std::cin >> count >> paths >> days >> seed) || count < 2 || count > 10000) throw std::invalid_argument("invalid header");
        std::vector<double> returns(count);
        for (auto& value : returns) if (!(std::cin >> value)) throw std::invalid_argument("invalid return");
        const auto result = horizon::simulate(returns, paths, days, seed);
        const auto rolling = horizon::rolling_statistics(returns, std::min(std::size_t{5}, count));
        std::cout << std::setprecision(17)
            << "{\"mean_daily_log_return\":" << result.statistics.mean
            << ",\"daily_volatility\":" << result.statistics.sample_stddev
            << ",\"annualized_volatility\":" << result.statistics.annualized_volatility
            << ",\"expected_return\":" << result.expected_return
            << ",\"probability_profit\":" << result.probability_profit
            << ",\"p05\":" << result.p05 << ",\"median\":" << result.median << ",\"p95\":" << result.p95
            << ",\"histogram_edges\":[";
        for (std::size_t i=0; i<result.histogram_edges.size(); ++i) std::cout << (i ? "," : "") << result.histogram_edges[i];
        std::cout << "],\"histogram_counts\":[";
        for (std::size_t i=0; i<result.histogram_counts.size(); ++i) std::cout << (i ? "," : "") << result.histogram_counts[i];
        std::cout << "],\"rolling_5_session_volatility\":[";
        for (std::size_t i=0; i<rolling.size(); ++i) std::cout << (i ? "," : "") << rolling[i].annualized_volatility;
        std::cout << "]}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
