#include "horizon.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>

void require(bool value) { if (!value) throw std::runtime_error("assertion failed"); }
template<class Function> void rejects(Function function) {
    bool rejected = false;
    try { function(); } catch (const std::invalid_argument&) { rejected = true; }
    require(rejected);
}
int main() {
    try {
        std::vector<double> input{-.02, 0, .02};
        const auto stats = horizon::statistics(input);
        require(std::abs(stats.mean) < 1e-12);
        require(std::abs(stats.sample_stddev - .02) < 1e-12);
        require(std::abs(stats.annualized_volatility - .02*std::sqrt(252.0)) < 1e-12);
        require(horizon::rolling_statistics(input, 2).size() == 2);
        const auto first = horizon::simulate(input, 100000, 5, 42);
        const auto second = horizon::simulate(input, 100000, 5, 42);
        require(first.expected_return == second.expected_return);
        require(std::abs(first.probability_profit - .5) < .01);
        require(std::abs(first.expected_return - std::expm1(.5*.02*.02*5)) < .001);
        require(first.p05 < first.median && first.median < first.p95);
        require(std::accumulate(first.histogram_counts.begin(),first.histogram_counts.end(),std::size_t{0}) == 100000);
        std::vector<double> fixed(20,.01);
        const auto constant = horizon::simulate(fixed,1000,5,42);
        require(std::abs(constant.expected_return - std::expm1(.05)) < 1e-12);
        require(constant.probability_profit == 1 && constant.p05 == constant.p95);
        rejects([&]{ horizon::simulate(input,1,5,42); });
        rejects([&]{ horizon::simulate(input,1000,0,42); });
        rejects([&]{ horizon::rolling_statistics(input,1); });
        input[0] = std::numeric_limits<double>::quiet_NaN();
        rejects([&]{ horizon::statistics(input); });
        std::cout << "statistics, rolling windows, seeded simulation, analytic moments and invalid inputs passed\n";
    } catch(const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
