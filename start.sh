#!/bin/bash
# Agent Zero startup script - ensures correct Python environment

cd "$(dirname "$0")"

# Use the Conda environment Python
PYTHON_BIN="./.conda/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Conda environment not found at $PYTHON_BIN"
    echo "Please run: conda create -n agent-zero-env python=3.12"
    echo "And: pip install -r requirements.txt"
    exit 1
fi

echo "Starting Agent Zero with Conda Python..."
exec "$PYTHON_BIN" run_ui.py --port=5555
