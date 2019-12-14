#!/usr/bin/env bash

set -e
set -x

if [ "$1" == "-r" ]; then
    export RENDER_LOCAL=1
fi

# C++ Version
./src/graph_generator.py results/query_data/cpp_version.csv results/graphs/cpp_version.png bar \
                         "C++ Version" "C++ version" "Count" &

# Binary Hardening Others
./src/graph_generator.py results/query_data/binary_hardening_others.csv \
                         results/graphs/binary_hardening_others.png grouped_bar \
                         "Binary Hardening Usage" "" "Count" --groups "Yes" "No" &

# Binary Hardening Fortified Source Functions
./src/graph_generator.py results/query_data/binary_hardening_fsf.csv \
                         results/graphs/binary_hardening_fsf.png bar \
                         "Fortified Source Function Usage" "" "Count" --cycle-colors &

# CDF test
./src/graph_generator.py results/query_data/cdf_test.csv results/graphs/cdf_test.png cdf \
                         "Smart Pointer Occurrences" "Occurrences" "Cumulative probability" \
                         --color "blue" &

# Introduction Smart Ptr
./src/graph_generator.py results/query_data/introduction_smart_ptr.csv \
                         results/graphs/introduction_smart_ptr.png bar \
                         "Smart Pointer Introduction Year" "" "Count" --slant &

# Introduction Named Cast
./src/graph_generator.py results/query_data/introduction_named_cast.csv \
                         results/graphs/introduction_named_cast.png bar \
                         "Named Cast Introduction Year" "" "Count" --slant &

# Project Creation Year
./src/graph_generator.py results/query_data/project_creation.csv \
                         results/graphs/project_creation.png bar \
                         "Project Creation Year" "" "Count" --slant --color "blue" &

# Ubuntu popularity Google Trends
./src/graph_generator.py results/query_data/google_trends_ubuntu.csv \
                         results/graphs/google_trends_ubuntu.png bar \
                         "Google Trends Ubuntu Search Term" "" "Popularity units" \
                         --slant --color "orange" &

# Days between creation and smart pointer introduction
./src/graph_generator.py results/query_data/creation_smart_ptr.csv \
                         results/graphs/creation_smart_ptr.png cdf \
                         "Days between project creation and smart pointer introduction" \
                         "Days" "CDF of days" \
                         --color "blue" &

# Days between creation and named cast introduction
./src/graph_generator.py results/query_data/creation_named_cast.csv \
                         results/graphs/creation_named_cast.png cdf \
                         "Days between project creation and named cast introduction" \
                         "Days" "CDF of days" \
                         --color "blue" &

# Named Cast Count
./src/graph_generator.py results/query_data/namedcast_count.csv \
                         results/graphs/namedcast_count.png bar \
                         "Named Casts Detected in Package" "At least a single usage detected" \
                         "Count" --cycle-colors &

# SmartPointer Count
./src/graph_generator.py results/query_data/smart_ptr_detected.csv \
                         results/graphs/smart_ptr_detected.png bar \
                         "Smart Pointer Detected in Package" "At least a single usage detected" \
                         "Count" --cycle-colors &

# Maintainer Count
./src/graph_generator.py results/query_data/maintainer_count.csv \
                         results/graphs/maintainer_count.png bar \
                         "Distribution of Number of Maintainers and the Packages Managed" \
                         "Packages managed" "Number of maintainers" --color "orange" &

# Package Scores Distribution
./src/graph_generator.py results/query_data/scores_distribution.csv \
                         results/graphs/scores_distribution.png bar \
                         "Distribution of Package Scores" "Package score" "Number of packages" \
                         --color "blue" &

# Security Features Deployed
./src/graph_generator.py results/query_data/common_security_features.csv \
                         results/graphs/common_security_features.png bar \
                         "Cumulative Points for Security Features Deployed" \
                         "Security feature" \
                         "Points" --color "green" --slant 9 &

# CDF of Maintainer Scores
./src/graph_generator.py results/query_data/maintainer_scores_cdf.csv \
                         results/graphs/maintainer_scores_cdf.png cdf \
                         "CDF of Maintainer Scores" \
                         "Scores" "CDF of scores" --num-bins 8 --fixed-bins \
                         --color "blue" &

wait
