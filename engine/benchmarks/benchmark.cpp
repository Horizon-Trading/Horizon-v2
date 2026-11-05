#include "horizon.hpp"
#include <chrono>
#include <iostream>
#include <vector>
int main() {
    std::vector<double> returns;
    for(int i=0;i<60;++i) returns.push_back(i%2 ? .015 : -.01);
    const auto start = std::chrono::steady_clock::now();
    const auto result = horizon::simulate(returns,100000,20,42);
    const auto ms = std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
    std::cout << "paths=100000 days=20 elapsed_ms=" << ms << " expected_return=" << result.expected_return << '\n';
}
