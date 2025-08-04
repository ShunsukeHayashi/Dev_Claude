#!/bin/bash
# Notification Hook for Claude Code
# This hook sends macOS notifications when Claude needs input

# Get notification details from environment
NOTIFICATION_TYPE="$1"
NOTIFICATION_MESSAGE="$2"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$(pwd)/.claude/logs/notifications.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Log the notification
echo "[$TIMESTAMP] Notification: $NOTIFICATION_TYPE - $NOTIFICATION_MESSAGE" >> "$LOG_FILE"

# Default message if not provided
if [ -z "$NOTIFICATION_MESSAGE" ]; then
    NOTIFICATION_MESSAGE="Claude needs your input"
fi

# Send macOS notification
if command -v osascript &> /dev/null; then
    osascript -e "display notification \"$NOTIFICATION_MESSAGE\" with title \"Claude Code\" subtitle \"$NOTIFICATION_TYPE\""
    echo "[$TIMESTAMP] macOS notification sent" >> "$LOG_FILE"
else
    # Fallback for non-macOS systems
    echo "[$TIMESTAMP] osascript not available, notification not sent" >> "$LOG_FILE"
    
    # Try alternative notification methods
    if command -v notify-send &> /dev/null; then
        # Linux with libnotify
        notify-send "Claude Code" "$NOTIFICATION_MESSAGE"
        echo "[$TIMESTAMP] Linux notification sent via notify-send" >> "$LOG_FILE"
    elif command -v terminal-notifier &> /dev/null; then
        # macOS with terminal-notifier (if installed via homebrew)
        terminal-notifier -title "Claude Code" -message "$NOTIFICATION_MESSAGE"
        echo "[$TIMESTAMP] Notification sent via terminal-notifier" >> "$LOG_FILE"
    fi
fi

# Sound alert (optional)
if [ -f "/System/Library/Sounds/Glass.aiff" ]; then
    afplay "/System/Library/Sounds/Glass.aiff" 2>/dev/null &
fi

exit 0