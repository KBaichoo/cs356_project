#!/usr/bin/env bash

PACKAGE_NAME="$1"

apt-get changelog "${PACKAGE_NAME}" |
    grep "\-\-" |
    tail -n 1 |
    cut -d ">" -f 2 |
    awk '{$1=$1};1' |
    xargs -I {} date -d {} +"%s"
