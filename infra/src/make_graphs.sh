#!/usr/bin/env bash

set -e
set -x

# C++ Version
./src/graph_generator.py results/query_data/cpp_version.csv results/graphs/cpp_version.png bar \
                         "C++ Version" "C++ version" "Count"

# Binary Hardening Others
./src/graph_generator.py results/query_data/binary_hardening_others.csv \
                         results/graphs/binary_hardening_others.png grouped_bar \
                         "Binary Hardening Usage" "" "Count" --groups "yes" "no"

# Binary Hardening Fortified Source Functions
./src/graph_generator.py results/query_data/binary_hardening_fsf.csv \
                         results/graphs/binary_hardening_fsf.png bar \
                         "Fortified Source Function Usage" "" "Count" --cycle-colors

# CDF test
./src/graph_generator.py results/query_data/cdf_test.csv results/graphs/cdf_test.png cdf \
                         "Smart Pointer Occurrences" "Occurrences" "Percentage of occurrences" \
                         --color "blue"

# Introduction Smart Ptr
./src/graph_generator.py results/query_data/introduction_smart_ptr.csv \
                         results/graphs/introduction_smart_ptr.png bar \
                         "Smart Pointer Introduction Commits" "" "Count" --slant

# Introduction Named Cast
./src/graph_generator.py results/query_data/introduction_named_cast.csv \
                         results/graphs/introduction_named_cast.png bar \
                         "Named Cast Introduction Commits" "" "Count" --slant