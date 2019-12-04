#!/usr/bin/env bash

CONFIG_FILE="$1"
SOURCE_DIR="$2"
FEATURE="$3"

OUTPUT=$(../detector/runner.py \
             --config_file "$CONFIG_FILE" \
             --source_package_directory "$SOURCE_DIR" \
             -o "$FEATURE" 2> /dev/null)

echo "$OUTPUT" | grep "\"detected\": \"yes\"" > /dev/null 2>&1
DETECTED=$?

if [ "$DETECTED" != 0 ]; then
    # Feature NOT detected (BAD/OLD), exit 0
    exit 0
else
    # Feature IS detected (GOOD/NEW), exit 1
    exit 1
fi
