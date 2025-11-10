#!/bin/bash
# Wrapper script to run the menubar app with Python directly

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script
cd "$SCRIPT_DIR"
exec /usr/bin/python3 menubar_app.py
