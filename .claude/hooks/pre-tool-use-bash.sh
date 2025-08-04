#!/bin/bash
# Pre-Tool Use Hook for Bash commands
# This hook logs all Bash tool executions

# Get the command from TOOL_INPUT environment variable
COMMAND="$TOOL_INPUT"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$HOME/.claude/logs/execution.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log the command execution
echo "[$TIMESTAMP] Executing Bash command: $COMMAND" >> "$LOG_FILE"

# Optional: Add command validation or security checks here
# Example: Block dangerous commands
if [[ "$COMMAND" =~ (rm -rf|format|dd if=/dev/zero) ]]; then
    echo "[$TIMESTAMP] WARNING: Potentially dangerous command blocked: $COMMAND" >> "$LOG_FILE"
    echo "Error: This command has been blocked for safety reasons."
    exit 1
fi

# Log to project-specific log as well
PROJECT_LOG="$(pwd)/.claude/logs/bash-commands.log"
if [ -d "$(pwd)/.claude" ]; then
    mkdir -p "$(dirname "$PROJECT_LOG")"
    echo "[$TIMESTAMP] $COMMAND" >> "$PROJECT_LOG"
fi

# Exit successfully to allow command execution
exit 0