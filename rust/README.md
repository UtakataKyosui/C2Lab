# Rust Development Plugin

Comprehensive Rust development toolkit for Claude Code with linting, formatting, type checking, dependency management, workspace support, and macro patterns.

## Features

### 🛠️ Commands
- `/rust:lint` - Run cargo clippy with automatic fixes
- `/rust:format` - Format code with cargo fmt
- `/rust:check` - Type check with cargo check
- `/rust:deps` - Check for outdated dependencies
- `/rust:fix` - Auto-fix common errors with cargo fix
- `/rust:build` - Build project and report errors
- `/rust:workspace` - Analyze and manage workspace structure
- `/rust:add-crate` - Add new crate to workspace
- `/rust:macro` - Generate common macro patterns (Builder, Error Type, Test Generator)

### 🤖 Agents
- **code-reviewer** - Reviews Rust code for correctness and best practices
- **code-debugger** - Debugs Rust code and macro expansion errors
- **code-optimizer** - Optimizes Rust code for performance
- **error-fixer** - Automatically fixes compilation errors (triggers on errors)
- **crate-advisor** - Recommends optimal crates for requirements (triggers on "recommend crate" queries)
- **workspace-architect** - Designs optimal workspace structure (triggers on workspace questions)

### 📚 Skills
- **rust-coder** - Idiomatic Rust coding patterns with macros
- **rust-debugger** - Debugging techniques and workspace debugging
- **cargo-tools** - Cargo commands and dependency management
- **error-patterns** - Common Rust errors and automatic fixes
- **crate-selection** - How to choose optimal crates/libraries
- **macro-patterns** - Declarative and procedural macro patterns
- **workspace-management** - Workspace configuration and crate organization

### 🪝 Hooks
- **PostToolUse** (Edit/Write) - Automatically formats and lints Rust files after editing
- **PreCompact** - Runs final validation checks before conversation ends

### 🔌 MCP Servers
- **crates-io** - Search crates, get latest versions and documentation
- **rustsec** - Check security advisories and vulnerabilities

## Installation

```bash
# Install from marketplace
cc plugin install rust-development-plugin

# Or install locally
cc --plugin-dir /path/to/rust-development-plugin
```

## Prerequisites

- Rust toolchain (rustc, cargo)
- cargo-outdated (optional, for dependency checking)
- cargo-audit (optional, for security checking)

Install optional tools:
```bash
cargo install cargo-outdated cargo-audit
```

## Configuration

Create `.claude/rust.local.md` in your project to configure plugin behavior:

```markdown
---
auto_format: true
auto_lint: true
auto_fix: false
clippy_level: "warn"
workspace_mode: "current"
crates_io_token: ""
---

# Rust Plugin Configuration

Additional project-specific notes...
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_format` | boolean | `true` | Automatically format Rust files on save |
| `auto_lint` | boolean | `true` | Automatically lint Rust files on save |
| `auto_fix` | boolean | `false` | Automatically apply fixes from clippy |
| `clippy_level` | string | `"warn"` | Clippy lint level: "warn" or "deny" |
| `workspace_mode` | string | `"current"` | Workspace scope: "current" or "all" |
| `crates_io_token` | string | `""` | Optional crates.io API token for higher rate limits |

## Usage Examples

### Linting and Formatting
```
User: Lint my code
Claude: [Runs /rust:lint, shows results in table format, auto-applies fixes]

User: Format this file
Claude: [Runs /rust:format on current file]
```

### Dependency Management
```
User: Check for outdated dependencies
Claude: [Runs /rust:deps, shows table of outdated crates with latest versions]

User: What's the best HTTP client for Rust?
Claude: [crate-advisor agent activates, recommends reqwest, ureq, hyper with comparisons]
```

### Workspace Management
```
User: How should I structure my workspace?
Claude: [workspace-architect agent activates, analyzes project, suggests structure]

User: Add a new crate called "api-client"
Claude: [Runs /rust:add-crate api-client, creates directory, updates Cargo.toml]
```

### Macro Generation
```
User: Generate a builder pattern macro
Claude: [Runs /rust:macro builder, generates macro_rules! for builder pattern]

User: I need an error type enum
Claude: [Runs /rust:macro error-type, generates error enum with From implementations]
```

### Error Fixing
```
User: Fix this compilation error
Claude: [error-fixer agent activates, analyzes error, applies automatic fixes]

[When editing Rust files]
Claude: [PostToolUse hook runs, auto-formats and lints, blocks if errors found]
```

## Hooks Behavior

The plugin uses command-based hooks that run automatically:

- **After editing Rust files**: Automatically runs `cargo fmt` and `cargo clippy`
- **On errors**: Blocks until errors are fixed (enforces code quality)
- **Before conversation ends**: Validates entire project

To disable hooks temporarily, adjust settings in `.claude/rust.local.md`.

## MCP Servers

### crates-io
Provides access to crates.io API:
- Search for crates by keyword
- Get latest versions and metadata
- Check download counts and popularity

### rustsec
Provides access to RustSec Advisory Database:
- Check dependencies for known vulnerabilities
- Get details on security advisories

No authentication required, but rate limits apply. Add `crates_io_token` in settings for higher limits.

## Troubleshooting

### Commands not appearing
- Verify plugin is enabled: `cc plugin list`
- Restart Claude Code session

### Hooks blocking too aggressively
- Adjust `auto_lint` and `auto_fix` in `.claude/rust.local.md`
- Set to `false` to disable automatic checks

### MCP servers not connecting
- Check Rust toolchain is installed
- Verify internet connection for API access

## License

MIT

## Contributing

Contributions welcome! Please submit issues and pull requests to the repository.
