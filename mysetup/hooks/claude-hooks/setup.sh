#!/bin/bash

# Claude Code Production Hooks Setup Script
# This script sets up the production hooks for Claude Code

set -e

echo "🚀 Setting up Claude Code Production Hooks..."

# Build the project
echo "📦 Building project..."
cargo build --release

# Create user bin directory if it doesn't exist
mkdir -p ~/bin

# Copy binary to user bin
echo "📋 Installing binary to ~/bin..."
cp target/release/production-hooks ~/bin/claude-production-hooks
chmod +x ~/bin/claude-production-hooks

# Create logs directory
mkdir -p ~/.claude/hook-logs

# Test the hook
echo "🧪 Testing the hook..."
echo '{"hook_event_name":"PreToolUse","session_id":"setup-test","transcript_path":"/tmp/test.md","cwd":"/tmp","tool_name":"Bash","tool_input":{"command":"echo Hello from hooks!"}}' | ~/bin/claude-production-hooks

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📊 Features enabled:"
echo "   💻 Bash command logging and monitoring"
echo "   🦀 Rust file lint/format automation"
echo "   🔌 MCP tool usage tracking"
echo "   📚 Information gathering recording"
echo "   📈 Session statistics and logging"
echo ""
echo "📂 Logs will be saved to: ~/.claude/hook-logs/"
echo "🔧 Binary installed at: ~/bin/claude-production-hooks"
echo ""
echo "🎯 Next steps:"
echo "   1. Start using Claude Code normally"
echo "   2. Your hooks will automatically run and log activities"
echo "   3. Check logs in ~/.claude/hook-logs/ for detailed statistics"
echo ""
echo "⚠️  Important: Restart Claude Code to activate the new hooks!"