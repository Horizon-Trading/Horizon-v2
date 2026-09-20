cmake_minimum_required(VERSION 3.20)

project(
  horizon_engine
  VERSION 0.1.0
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(horizon_engine)

target_include_directories(
  horizon_engine
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_sources(
  horizon_engine
  PRIVATE
    src/horizon.cpp
)

if (MSVC)
  target_compile_options(horizon_engine PRIVATE /W4)
else()
  target_compile_options(horizon_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()
