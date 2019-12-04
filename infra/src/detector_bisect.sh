#!/usr/bin/env bash

DETECTOR_RUNNER="$1"
CONFIG_FILE="$2"
SOURCE_DIR="$3"
FEATURE="$4"

OUTPUT=$("$DETECTOR_RUNNER" \
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
