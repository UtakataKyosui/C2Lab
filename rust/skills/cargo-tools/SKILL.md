---
name: cargo-tools
description: This skill should be used when the user asks to "run cargo", "manage dependencies", "check for outdated crates", "audit dependencies", "add a dependency", "update Cargo.toml", or mentions cargo commands like clippy, fmt, check, build, test, or dependency management.
version: 0.1.0
---

# Cargo Tools and Dependency Management

## Overview

This skill provides comprehensive guidance for using Cargo, Rust's package manager and build system, with focus on dependency management, workspace operations, and common tooling workflows.

## Core Cargo Commands

### Build and Check

**cargo check** - Fast compilation check without producing binary:
```bash
cargo check                    # Check current package
cargo check --all-targets      # Check all targets (lib, bins, tests, benches)
cargo check --workspace        # Check all workspace members
```

Use `cargo check` during development for rapid feedback on compilation errors.

**cargo build** - Compile the project:
```bash
cargo build                    # Debug build
cargo build --release          # Optimized release build
cargo build --workspace        # Build all workspace members
cargo build -p crate-name      # Build specific workspace member
```

**cargo test** - Run tests:
```bash
cargo test                     # Run all tests
cargo test test_name           # Run specific test
cargo test --workspace         # Test all workspace members
cargo test -- --nocapture      # Show println! output
```

### Code Quality

**cargo clippy** - Rust linter for catching common mistakes:
```bash
cargo clippy                               # Run clippy
cargo clippy --all-targets --all-features  # Comprehensive check
cargo clippy --fix                         # Auto-apply fixes
cargo clippy -- -D warnings                # Treat warnings as errors
```

Configure clippy in `Cargo.toml` or `.cargo/config.toml`:
```toml
[lints.clippy]
all = "deny"
pedantic = "warn"
```

**cargo fmt** - Format code according to Rust style guidelines:
```bash
cargo fmt                      # Format current package
cargo fmt --all               # Format all workspace members
cargo fmt -- --check          # Check without modifying (CI mode)
```

Configure rustfmt via `.rustfmt.toml` or `rustfmt.toml`.

**cargo fix** - Automatically fix compiler warnings:
```bash
cargo fix                      # Fix current package
cargo fix --edition           # Migrate to new edition
cargo fix --allow-dirty       # Fix without clean working directory
```

## Dependency Management

### Adding Dependencies

Add dependencies to `Cargo.toml`:

```toml
[dependencies]
serde = "1.0"                         # Latest 1.x version
tokio = { version = "1.0", features = ["full"] }  # With features
reqwest = { version = "0.11", default-features = false }  # No defaults

[dev-dependencies]
criterion = "0.5"                     # Only for tests/benches

[build-dependencies]
cc = "1.0"                            # Only for build scripts
```

**Use `cargo add` for convenience:**
```bash
cargo add serde                       # Add latest version
cargo add tokio --features full       # Add with features
cargo add --dev criterion             # Add dev dependency
```

### Version Specifications

Understand semantic versioning in Cargo:

- `"1.0"` or `"^1.0"` - Compatible with 1.0 (1.x.x, but not 2.0)
- `"=1.0.5"` - Exact version only
- `"~1.0.5"` - Patch-level changes (1.0.x)
- `">=1.0, <2.0"` - Range specification
- `"*"` - Any version (not recommended)

**Lock versions with Cargo.lock:**
- Commit `Cargo.lock` for binaries/applications
- Do not commit for libraries (let downstream choose versions)

### Checking Dependencies

**cargo tree** - View dependency graph:
```bash
cargo tree                            # Show full tree
cargo tree -p serde                   # Focus on specific package
cargo tree --duplicates               # Show duplicate dependencies
cargo tree -i tokio                   # Show reverse dependencies (who depends on tokio)
```

**cargo outdated** - Check for outdated dependencies (requires installation):
```bash
cargo install cargo-outdated
cargo outdated                        # Show outdated dependencies
cargo outdated --workspace            # Check entire workspace
cargo outdated --root-deps-only       # Only direct dependencies
```

**cargo audit** - Check for security vulnerabilities (requires installation):
```bash
cargo install cargo-audit
cargo audit                           # Check for known vulnerabilities
cargo audit fix                       # Update vulnerable dependencies
```

**cargo update** - Update dependencies within version constraints:
```bash
cargo update                          # Update all dependencies
cargo update -p serde                 # Update specific package
cargo update --workspace              # Update workspace dependencies
```

### Dependency Features

Control optional functionality via features:

```toml
[features]
default = ["feature1"]
feature1 = []
feature2 = ["dep:optional-dep"]

[dependencies]
optional-dep = { version = "1.0", optional = true }
```

Build with specific features:
```bash
cargo build --features feature1,feature2
cargo build --all-features
cargo build --no-default-features
```

## Workspace Management

### Workspace Structure

Define workspace in root `Cargo.toml`:

```toml
[workspace]
members = [
    "crate-a",
    "crate-b",
    "lib/*",
]
exclude = ["old-code"]

[workspace.dependencies]
serde = "1.0"                # Shared dependency versions
```

Member crates can inherit workspace dependencies:

```toml
# In member Cargo.toml
[dependencies]
serde = { workspace = true }
```

### Workspace Commands

Most cargo commands support workspace operations:

```bash
cargo check --workspace              # Check all members
cargo test --workspace               # Test all members
cargo build --workspace --release    # Build all members
cargo clippy --workspace             # Lint all members

cargo build -p specific-crate        # Build specific member
```

**List workspace members:**
```bash
cargo metadata --format-version 1 | jq '.workspace_members'
```

### Workspace Dependencies Optimization

Use workspace dependencies to:
- Ensure consistent versions across members
- Reduce duplicate dependencies
- Centralize dependency management

```toml
# Root Cargo.toml
[workspace.dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

# Member Cargo.toml
[dependencies]
tokio = { workspace = true }
serde = { workspace = true }
```

## Performance Optimization

### Compilation Speed

**Use cargo-watch for auto-rebuild:**
```bash
cargo install cargo-watch
cargo watch -x check                 # Auto-run check on changes
cargo watch -x test                  # Auto-run tests
```

**Configure linker for faster builds** (Linux):

In `.cargo/config.toml`:
```toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
```

Requires mold linker:
```bash
# Ubuntu/Debian
sudo apt install mold

# Arch Linux
sudo pacman -S mold
```

**Use sccache for caching:**
```bash
cargo install sccache

# Set in .cargo/config.toml or environment
export RUSTC_WRAPPER=sccache
```

**Profile compilation:**
```bash
cargo build --timings              # Generate compilation timing report
```

### Build Profiles

Customize build profiles in `Cargo.toml`:

```toml
[profile.dev]
opt-level = 0                      # No optimization (fast compile)

[profile.dev.package."*"]
opt-level = 2                      # Optimize dependencies (faster runtime)

[profile.release]
lto = true                         # Link-time optimization
codegen-units = 1                  # Better optimization, slower compile
strip = true                       # Strip symbols (smaller binary)

[profile.bench]
inherits = "release"
```

## Common Workflows

### Creating New Projects

```bash
cargo new my-project               # Binary project
cargo new --lib my-lib             # Library project
cargo init                         # Initialize in existing directory
```

### Adding to Workspace

```bash
cd workspace-root
cargo new --lib crates/new-member
# Add to workspace members in root Cargo.toml
```

### Dependency Audit Workflow

```bash
# Check for outdated dependencies
cargo outdated

# Check for security vulnerabilities
cargo audit

# Update dependencies within constraints
cargo update

# View dependency tree
cargo tree --duplicates
```

### Publishing Workflow

```bash
# Validate package
cargo package --list              # Show what will be packaged

# Build and test package
cargo package                     # Create .crate file
cargo publish --dry-run           # Validate without publishing

# Publish
cargo login                       # Authenticate with crates.io
cargo publish                     # Publish to crates.io
```

## Troubleshooting

### Clean Build

```bash
cargo clean                       # Remove target/ directory
cargo build                       # Fresh build
```

### Dependency Conflicts

```bash
cargo tree --duplicates           # Find duplicate versions
cargo update -p conflicting-dep   # Try updating
```

If version conflicts persist, use `[patch]` section in `Cargo.toml`:

```toml
[patch.crates-io]
problematic-dep = { git = "https://github.com/user/fork" }
```

### Compilation Errors

```bash
cargo clean && cargo check        # Clean build
cargo check --verbose             # Verbose output
rustc --version                   # Verify toolchain version
```

## Additional Resources

### Reference Files

For detailed information, consult:
- **`references/cargo-reference.md`** - Complete Cargo.toml reference and advanced features
- **`references/workspace-patterns.md`** - Workspace organization patterns and best practices

### Scripts

Utility scripts available:
- **`scripts/check-deps.sh`** - Comprehensive dependency health check (outdated + audit)
- **`scripts/workspace-info.sh`** - Display workspace structure and member information

## Best Practices

1. **Dependency versions**: Use `^` (default) for libraries, consider `=` for applications
2. **Cargo.lock**: Commit for binaries, don't commit for libraries
3. **Features**: Use features for optional functionality, keep defaults minimal
4. **Workspaces**: Use for multi-crate projects, centralize common dependencies
5. **Security**: Run `cargo audit` regularly, update vulnerable dependencies promptly
6. **Performance**: Use `cargo check` during development, optimize linker, cache with sccache
7. **CI**: Run `cargo clippy -- -D warnings` and `cargo test --workspace` in CI

Apply these cargo workflows to maintain healthy, performant Rust projects with well-managed dependencies.
