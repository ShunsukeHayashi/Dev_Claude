#!/bin/bash
# YAML Context Engineering MCP Server startup script

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set Python path
export PYTHONPATH="$SCRIPT_DIR/src"

# Set output directory (can be overridden by environment)
if [ -z "$MCP_OUTPUT_DIRECTORY" ]; then
    export MCP_OUTPUT_DIRECTORY="$HOME/generated_contexts"
fi

# Create output directory if it doesn't exist
mkdir -p "$MCP_OUTPUT_DIRECTORY"

# Ensure log directory exists
mkdir -p "$HOME/.claude/logs"

echo "🚀 Starting YAML Context Engineering MCP Server"
echo "📁 Output directory: $MCP_OUTPUT_DIRECTORY"
echo "📝 Logs: $HOME/.claude/logs/yaml-context-engineering.log"

# Run the server
python3 -m yaml_context_engineering.main "$@"