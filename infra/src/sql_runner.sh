#!/usr/bin/env bash

DB="results/detection_results_v6.db"
INPUT_PATH="results/query_data/$1.sql"
OUTPUT_PATH="results/query_data/$1.csv"

sqlite3 -csv "$DB" < "$INPUT_PATH" > "$OUTPUT_PATH"
