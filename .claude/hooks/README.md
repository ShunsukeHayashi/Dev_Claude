# Claude Code Hooks Documentation

## Overview

This directory contains hook scripts for the YAML Context Engineering Agent project. These hooks integrate with Claude Code to provide logging, formatting, and notification capabilities.

## Available Hooks

### 1. Pre-Tool Use Hooks

#### `pre-tool-use-bash.sh`
- **Trigger**: Before any Bash command execution
- **Purpose**: 
  - Log all command executions
  - Validate commands for safety
  - Block potentially dangerous operations
- **Log Location**: 
  - `~/.claude/logs/execution.log` (global)
  - `.claude/logs/bash-commands.log` (project-specific)

#### `pre-tool-use-write.sh`
- **Trigger**: Before Write tool execution
- **Purpose**:
  - Log write operations
  - Prepare for post-write formatting
- **Log Location**: `.claude/logs/write-operations.log`

### 2. Post-Tool Use Hooks

#### `post-tool-use-file.sh`
- **Trigger**: After Edit, Write, or MultiEdit operations
- **Purpose**:
  - Log file modifications
  - Run Prettier formatting on supported files
  - Track git status changes
  - Update context indexes for generated_contexts
- **Log Location**: 
  - `~/.claude/changes.log` (global)
  - `.claude/logs/file-changes.log` (project-specific)
- **Supported Prettier formats**: `.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.scss`, `.md`, `.yaml`, `.yml`

### 3. Notification Hook

#### `notification-hook.sh`
- **Trigger**: When Claude needs user input
- **Purpose**:
  - Send desktop notifications
  - Play sound alerts (macOS)
  - Support multiple notification systems
- **Log Location**: `.claude/logs/notifications.log`
- **Supported Systems**:
  - macOS: `osascript` (primary), `terminal-notifier` (fallback)
  - Linux: `notify-send`

### 4. Session Hooks

#### Stop Hook (inline in settings.json)
- **Trigger**: Main agent response completion
- **Purpose**: Log session completion
- **Log Location**: `.claude/logs/session.log`

#### SubagentStop Hook (inline in settings.json)
- **Trigger**: Sub-agent completion
- **Purpose**: Log sub-agent execution
- **Log Location**: `.claude/logs/subagent.log`

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash /path/to/pre-tool-use-bash.sh"
          }
        ]
      }
    ]
  }
}
```

## Testing

Run the test script to verify all hooks are working:

```bash
./test-hooks.sh
```

## Security Features

1. **Command Validation**: The Bash pre-hook blocks dangerous commands like:
   - `rm -rf`
   - `format`
   - `dd if=/dev/zero`

2. **Path Validation**: All file operations use proper path handling

3. **Logging**: Comprehensive logging for audit trails

## Log Files

All logs are stored in structured directories:

```
.claude/logs/
├── bash-commands.log      # All Bash commands executed
├── write-operations.log   # Pre-write operations
├── file-changes.log       # Post-write modifications
├── notifications.log      # Notification history
├── session.log           # Session completions
└── subagent.log          # Sub-agent executions

~/.claude/logs/
├── execution.log         # Global command log
└── changes.log          # Global file changes
```

## Best Practices

1. **Regular Log Rotation**: Implement log rotation to prevent disk space issues
2. **Custom Validation**: Add project-specific command validation rules
3. **Error Handling**: All hooks exit gracefully on errors
4. **Performance**: Hooks are designed to be lightweight and fast

## Troubleshooting

### Hooks not executing
1. Check file permissions: `chmod +x *.sh`
2. Verify paths in settings.json are absolute
3. Check Claude Code logs for errors

### Prettier not formatting
1. Ensure prettier is installed: `npm install -g prettier`
2. Check file extensions are supported
3. Review logs for prettier errors

### Notifications not appearing
1. Check system notification permissions
2. Try alternative notification tools
3. Review notification log for errors

## Extending Hooks

To add custom functionality:

1. Create a new hook script in this directory
2. Make it executable: `chmod +x your-hook.sh`
3. Add configuration to settings.json
4. Test using test-hooks.sh

## Related Documentation

- [Claude Code Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [YAML Context Engineering Agent README](../../README.md)
- [MCP Server Documentation](../../mcp-server/README.md)