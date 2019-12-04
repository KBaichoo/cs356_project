#!/usr/bin/env bash

NEW_COMMIT="$1"
OLD_COMMIT="$2"
DETECTOR_BISECT="$3"
DETECTOR_RUNNER="$4"
CONFIG_FILE="$5"
SOURCE_DIR="$6"
FEATURE="$7"

git bisect start > /dev/null 2>&1
git bisect new "$NEW_COMMIT" > /dev/null 2>&1
git bisect old "$OLD_COMMIT" > /dev/null 2>&1

OUTPUT=$(git bisect run \
             "$DETECTOR_BISECT" \
             "$DETECTOR_RUNNER" \
             "$CONFIG_FILE" \
             "$SOURCE_DIR" \
             "$FEATURE" 2> /dev/null)
COMMIT_OUTPUT=$(echo "$OUTPUT" | grep "is the first new commit")
echo "$COMMIT_OUTPUT" | cut -d " " -f1

git bisect reset > /dev/null 2>&1
