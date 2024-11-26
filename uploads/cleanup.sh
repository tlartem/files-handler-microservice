#!/bin/bash

DAYS_TO_KEEP=7

CURRENT_DIR=$(dirname "$(readlink -f "$0")")

SCRIPT_NAME=$(basename "$0")

find "$CURRENT_DIR" -type f -mtime +$DAYS_TO_KEEP ! -name "$SCRIPT_NAME" -exec rm -f {} \;

echo "Старые файлы удалены из $CURRENT_DIR"