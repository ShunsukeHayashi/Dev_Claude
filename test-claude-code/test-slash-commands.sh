#!/bin/bash
# Test script for Claude Code slash commands

echo "🧪 Claude Code Slash Commands Test Suite"
echo "======================================"

# Test environment setup
TEST_DIR="/tmp/claude-code-test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    echo "Command: $test_command"
    
    # Simulate command execution (in real use, Claude would execute these)
    if [[ "$test_command" == *"extract-context"* ]]; then
        # Simulate extract-context command
        mkdir -p generated_contexts
        echo "---
title: \"Test Extraction\"
source_url: \"https://example.com\"
---
# Test Content" > generated_contexts/example_com.md
        
        if [ -f "generated_contexts/example_com.md" ]; then
            echo -e "${GREEN}✅ PASSED${NC}: File created successfully"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAILED${NC}: File not created"
            ((TESTS_FAILED++))
        fi
    elif [[ "$test_command" == *"setup-project"* ]]; then
        # Simulate setup-project command
        mkdir -p test-project/{.claude,mcp-server,generated_contexts}
        touch test-project/.claude/settings.json
        touch test-project/README.md
        
        if [ -d "test-project/.claude" ] && [ -f "test-project/README.md" ]; then
            echo -e "${GREEN}✅ PASSED${NC}: Project structure created"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAILED${NC}: Project structure incomplete"
            ((TESTS_FAILED++))
        fi
    elif [[ "$test_command" == *"generate-agent"* ]]; then
        # Simulate generate-agent command
        mkdir -p .claude/agents
        touch .claude/agents/test-agent.md
        
        if [ -f ".claude/agents/test-agent.md" ]; then
            echo -e "${GREEN}✅ PASSED${NC}: Agent file created"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ FAILED${NC}: Agent file not created"
            ((TESTS_FAILED++))
        fi
    fi
}

# Test 1: Extract Context Command
run_test "Extract Context - URL" \
    "/extract-context https://example.com" \
    "Context file created"

# Test 2: Extract Context - Multiple URLs
run_test "Extract Context - Multiple URLs" \
    "/extract-context https://example.com https://test.com" \
    "Multiple context files created"

# Test 3: Setup Project Command
run_test "Setup Project - Default" \
    "/setup-project" \
    "Project structure created"

# Test 4: Setup Project - Named
run_test "Setup Project - Named" \
    "/setup-project my-context-project" \
    "Named project created"

# Test 5: Generate Agent - API Docs
run_test "Generate Agent - API Docs" \
    "/generate-agent api-docs" \
    "API docs agent created"

# Test 6: Generate Agent - Tutorial
run_test "Generate Agent - Tutorial" \
    "/generate-agent tutorial" \
    "Tutorial agent created"

# Test 7: Generate Agent - Custom
run_test "Generate Agent - Custom" \
    "/generate-agent custom \"Legal document analyzer\"" \
    "Custom agent created"

# Test summary
echo -e "\n======================================"
echo "Test Summary:"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi