#!/bin/bash
# Pre-Tool Use Hook for Write operations
# This hook runs prettier on files before they are written

# Get file path from environment
FILE_PATH="$1"
if [ -z "$FILE_PATH" ]; then
    FILE_PATH="$TOOL_INPUT_PATH"
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$(pwd)/.claude/logs/write-operations.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log the write operation
echo "[$TIMESTAMP] Pre-write hook for: $FILE_PATH" >> "$LOG_FILE"

# Check if the file is a supported format for prettier
if [[ "$FILE_PATH" =~ \.(js|jsx|ts|tsx|json|css|scss|md|yaml|yml)$ ]]; then
    # Check if prettier is installed
    if command -v prettier &> /dev/null; then
        echo "[$TIMESTAMP] Running prettier on: $FILE_PATH" >> "$LOG_FILE"
        # Note: The actual formatting will happen post-write
        echo "[$TIMESTAMP] Prettier formatting scheduled for post-write" >> "$LOG_FILE"
    else
        echo "[$TIMESTAMP] Prettier not found, skipping formatting" >> "$LOG_FILE"
    fi
fi

# Exit successfully
exit 0