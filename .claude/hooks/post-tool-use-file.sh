#!/bin/bash
# Post-Tool Use Hook for File modifications (Edit/Write)
# This hook logs file changes and runs prettier

# Get file path from environment
FILE_PATH="$1"
if [ -z "$FILE_PATH" ]; then
    FILE_PATH="$TOOL_OUTPUT_PATH"
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
CHANGES_LOG="$HOME/.claude/changes.log"
PROJECT_LOG="$(pwd)/.claude/logs/file-changes.log"

# Create log directories if they don't exist
mkdir -p "$(dirname "$CHANGES_LOG")"
mkdir -p "$(dirname "$PROJECT_LOG")"

# Log the file modification
echo "[$TIMESTAMP] File modified: $FILE_PATH" >> "$CHANGES_LOG"
echo "[$TIMESTAMP] File modified: $FILE_PATH" >> "$PROJECT_LOG"

# Run prettier if applicable and available
if [[ "$FILE_PATH" =~ \.(js|jsx|ts|tsx|json|css|scss|md|yaml|yml)$ ]]; then
    if command -v prettier &> /dev/null; then
        echo "[$TIMESTAMP] Running prettier on: $FILE_PATH" >> "$PROJECT_LOG"
        prettier --write "$FILE_PATH" 2>> "$PROJECT_LOG" || {
            echo "[$TIMESTAMP] Prettier formatting failed for: $FILE_PATH" >> "$PROJECT_LOG"
        }
    fi
fi

# Track file changes in git (if in a git repo)
if [ -d ".git" ] && command -v git &> /dev/null; then
    # Get git status of the file
    GIT_STATUS=$(git status --porcelain "$FILE_PATH" 2>/dev/null)
    if [ -n "$GIT_STATUS" ]; then
        echo "[$TIMESTAMP] Git status: $GIT_STATUS" >> "$PROJECT_LOG"
    fi
fi

# Update YAML Context Engineering index if in generated_contexts
if [[ "$FILE_PATH" =~ generated_contexts/.+\.md$ ]]; then
    echo "[$TIMESTAMP] Updating context index for: $FILE_PATH" >> "$PROJECT_LOG"
    # Trigger index update (placeholder for actual implementation)
    echo "[$TIMESTAMP] TODO: Trigger MCP file_system_manager index update" >> "$PROJECT_LOG"
fi

exit 0