#!/usr/bin/env bash

find . -executable -type f -path "*/bin/*" -exec file {} \; \
    | grep "ELF" | awk '{print $1;}' | sed 's/:$//' | cut -c 3-
