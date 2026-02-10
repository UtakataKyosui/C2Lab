---
name: workspace-management
description: This skill should be used when the user asks about "workspace structure", "organize workspace", "add crate to workspace", "workspace dependencies", "monorepo setup", or mentions Cargo workspace configuration and multi-crate projects.
version: 0.1.0
---

# Cargo Workspace Management

## Overview

This skill provides guidance for creating, organizing, and managing Cargo workspaces for multi-crate Rust projects.

## Creating a Workspace

### Initial Setup

Create root `Cargo.toml` with workspace definition:

```toml
[workspace]
members = [
    "crate-a",
    "crate-b",
]
resolver = "2"  # Use new feature resolver
```

Directory structure:
```
my-workspace/
├── Cargo.toml       # Workspace root
├── Cargo.lock       # Shared lock file
├── crate-a/
│   ├── Cargo.toml
│   └── src/
└── crate-b/
    ├── Cargo.toml
    └── src/
```

### Adding Members

Use glob patterns for dynamic membership:

```toml
[workspace]
members = [
    "libs/*",
    "bins/*",
    "tools/*",
]
exclude = ["experimental"]
```

## Shared Dependencies

### Workspace Dependencies (Rust 1.64+)

Centralize dependency versions in root `Cargo.toml`:

```toml
[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"
```

Member crates inherit these:

```toml
# member/Cargo.toml
[dependencies]
serde = { workspace = true }
tokio = { workspace = true }
anyhow = { workspace = true }

# Can add features to inherited dependency
serde = { workspace = true, features = ["rc"] }
```

**Benefits:**
- Single source of truth for versions
- Prevents version conflicts
- Easy to update all at once

### Workspace Package Metadata

Share common metadata:

```toml
[workspace.package]
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
edition = "2021"
rust-version = "1.70"
license = "MIT OR Apache-2.0"

# member/Cargo.toml
[package]
name = "my-crate"
version.workspace = true
authors.workspace = true
edition.workspace = true
```

## Workspace Lints

Centralize lint configuration:

```toml
[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
all = "deny"
pedantic = "warn"

# member/Cargo.toml
[lints]
workspace = true
```

## Inter-Crate Dependencies

Members can depend on each other:

```toml
# crate-b/Cargo.toml
[dependencies]
crate-a = { path = "../crate-a" }

# Or with workspace dependencies
[workspace.dependencies]
crate-a = { path = "crate-a" }

# crate-b/Cargo.toml
[dependencies]
crate-a = { workspace = true }
```

## Workspace Commands

### Build and Test

```bash
cargo build --workspace           # Build all members
cargo test --workspace            # Test all members
cargo check --workspace           # Check all members
cargo clippy --workspace          # Lint all members

# Build specific member
cargo build -p crate-a

# Build all except one
cargo build --workspace --exclude crate-b
```

### Publishing

```bash
# Publish specific member
cargo publish -p crate-a

# Use cargo-workspaces for batch operations
cargo install cargo-workspaces
cargo workspaces publish
```

## Organization Patterns

### By Layer

Separate by architectural layer:

```
workspace/
├── Cargo.toml
├── domain/          # Business logic
├── infrastructure/  # External dependencies
└── application/     # App composition
```

### By Feature

Organize by features/modules:

```
workspace/
├── Cargo.toml
├── core/
├── auth/
├── storage/
└── api/
```

### Binary + Libraries

App with multiple binaries and shared lib:

```
workspace/
├── Cargo.toml
├── lib/             # Shared library
├── cli/             # CLI tool
├── server/          # Server binary
└── worker/          # Background worker
```

## Optimization

### Build Profiles

Optimize differently for different members:

```toml
[profile.dev.package.heavy-dep]
opt-level = 2  # Optimize this dependency in dev

[profile.release]
lto = true
codegen-units = 1
```

### Incremental Builds

Workspace shares build cache:
- Change one member → only rebuild affected crates
- Cargo determines build order automatically

### Parallel Builds

Independent crates build in parallel:

```
lib-a  →  app-a
  ↓         ↑
lib-b  →  app-b
```

lib-a and lib-b build in parallel.

## Common Workflows

### Adding New Crate

```bash
cd workspace-root
cargo new --lib libs/new-crate

# Add to workspace members if not using glob
# Edit root Cargo.toml:
# members = ["libs/*"]
```

### Updating Dependencies

```bash
# Update workspace lockfile
cargo update

# Update specific dependency
cargo update -p serde

# Check for outdated
cargo outdated --workspace
```

### Dependency Analysis

```bash
# View dependency tree
cargo tree --workspace

# Find duplicates
cargo tree --duplicates

# Check specific member
cargo tree -p crate-a
```

## Troubleshooting

### Dependency Conflicts

Use `[patch]` to override dependencies:

```toml
[patch.crates-io]
problematic-dep = { git = "https://github.com/user/fork" }
```

### Circular Dependencies

Avoid circular deps between members:

❌ Bad: A → B, B → A

✅ Good: Extract shared code to C, then A → C, B → C

### Build Order Issues

Cargo determines build order automatically. If issues arise:
- Check for circular dependencies
- Verify path dependencies are correct

## Additional Resources

### Reference Files

- **`references/workspace-patterns.md`** - Detailed organization patterns (already covered in cargo-tools)
- **`references/workspace-best-practices.md`** - Advanced workspace techniques

### Scripts

- **`scripts/workspace-info.sh`** - Display workspace structure (in cargo-tools)
- **`scripts/add-member.sh`** - Add new workspace member with template

Use these resources for advanced workspace management and organization strategies.
