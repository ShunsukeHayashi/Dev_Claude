#!/bin/bash
# Run shunsuke-scout-mcp with virtual environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set Python path
export PYTHONPATH="$SCRIPT_DIR/src"

# Use virtual environment's Python directly
exec "$SCRIPT_DIR/venv/bin/python" -m yaml_context_engineering.main "$@"