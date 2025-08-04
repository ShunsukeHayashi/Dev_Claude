#!/bin/bash
# Test script for Claude Code hooks

echo "🧪 Testing Claude Code Hooks"
echo "=========================="

# Test directories
TEST_DIR="/tmp/claude-hooks-test"
mkdir -p "$TEST_DIR"

# Test 1: Pre-Tool Use Bash Hook
echo -e "\n📝 Test 1: Pre-Tool Use Bash Hook"
export TOOL_INPUT="echo 'Hello from test'"
bash /Users/shunsuke/Dev/Dev_Claude/.claude/hooks/pre-tool-use-bash.sh
if [ $? -eq 0 ]; then
    echo "✅ Pre-Tool Use Bash Hook: PASSED"
else
    echo "❌ Pre-Tool Use Bash Hook: FAILED"
fi

# Test 2: Pre-Tool Use Write Hook
echo -e "\n📝 Test 2: Pre-Tool Use Write Hook"
export TOOL_INPUT_PATH="$TEST_DIR/test.js"
bash /Users/shunsuke/Dev/Dev_Claude/.claude/hooks/pre-tool-use-write.sh "$TEST_DIR/test.js"
if [ $? -eq 0 ]; then
    echo "✅ Pre-Tool Use Write Hook: PASSED"
else
    echo "❌ Pre-Tool Use Write Hook: FAILED"
fi

# Test 3: Post-Tool Use File Hook
echo -e "\n📝 Test 3: Post-Tool Use File Hook"
echo "console.log('test');" > "$TEST_DIR/test.js"
export TOOL_OUTPUT_PATH="$TEST_DIR/test.js"
bash /Users/shunsuke/Dev/Dev_Claude/.claude/hooks/post-tool-use-file.sh "$TEST_DIR/test.js"
if [ $? -eq 0 ]; then
    echo "✅ Post-Tool Use File Hook: PASSED"
else
    echo "❌ Post-Tool Use File Hook: FAILED"
fi

# Test 4: Notification Hook
echo -e "\n📝 Test 4: Notification Hook"
bash /Users/shunsuke/Dev/Dev_Claude/.claude/hooks/notification-hook.sh "Test" "This is a test notification"
if [ $? -eq 0 ]; then
    echo "✅ Notification Hook: PASSED"
else
    echo "❌ Notification Hook: FAILED"
fi

# Test 5: Check logs
echo -e "\n📊 Log Files:"
echo "- Execution log: ~/.claude/logs/execution.log"
echo "- Project logs: /Users/shunsuke/Dev/Dev_Claude/.claude/logs/"

if [ -f ~/.claude/logs/execution.log ]; then
    echo -e "\n📄 Recent execution log entries:"
    tail -n 5 ~/.claude/logs/execution.log
fi

if [ -f /Users/shunsuke/Dev/Dev_Claude/.claude/logs/bash-commands.log ]; then
    echo -e "\n📄 Recent bash commands:"
    tail -n 5 /Users/shunsuke/Dev/Dev_Claude/.claude/logs/bash-commands.log
fi

# Cleanup
rm -rf "$TEST_DIR"

echo -e "\n✅ Hook testing completed!"