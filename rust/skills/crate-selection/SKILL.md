---
name: crate-selection
description: This skill should be used when the user asks "recommend a crate", "what library should I use", "best crate for", "alternatives to", or mentions needing functionality like HTTP clients, serialization, async runtimes, CLI parsing, or database access.
version: 0.1.0
---

# Rust Crate Selection Guide

## Overview

This skill provides guidance for selecting high-quality Rust crates based on common use cases, with focus on ecosystem standards, maturity, and best practices.

## Selection Criteria

When choosing a crate, evaluate:

1. **Maturity** - Version >= 1.0, stable API
2. **Maintenance** - Recent commits, active issues/PRs
3. **Popularity** - Download count, GitHub stars
4. **Documentation** - Good docs.rs coverage, examples
5. **Dependencies** - Minimal, well-maintained deps
6. **Compatibility** - Works with your Rust version/targets
7. **License** - Compatible with your project

Check on crates.io and docs.rs for metrics.

## Common Use Cases and Recommendations

### Async Runtime

**tokio** - Industry standard, full-featured
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```
- Most popular, excellent docs
- Full ecosystem support
- Use for: Most async applications

**async-std** - Alternative async runtime
```toml
[dependencies]
async-std = { version = "1", features = ["attributes"] }
```
- Similar API to std library
- Use for: Projects wanting std-like API

### HTTP Client

**reqwest** - High-level, ergonomic
```toml
[dependencies]
reqwest = { version = "0.11", features = ["json"] }
```
- Built on hyper, easy to use
- Use for: Most HTTP client needs

**ureq** - Minimal, synchronous
```toml
[dependencies]
ureq = "2"
```
- No async required, smaller binary
- Use for: Simple sync HTTP requests

### Serialization

**serde** - De facto standard
```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"  # For JSON
```
- Supports many formats (JSON, YAML, TOML, etc.)
- Use for: All serialization needs

### CLI Parsing

**clap** - Feature-rich, derives support
```toml
[dependencies]
clap = { version = "4", features = ["derive"] }
```
- Powerful, excellent help generation
- Use for: Complex CLI apps

**pico-args** - Minimal, simple
```toml
[dependencies]
pico-args = "0.5"
```
- Tiny dependency, fast compile
- Use for: Simple argument parsing

### Database Access

**sqlx** - Async, compile-time checked SQL
```toml
[dependencies]
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio"] }
```
- Compile-time query validation
- Use for: PostgreSQL, MySQL, SQLite

**diesel** - ORM, type-safe queries
```toml
[dependencies]
diesel = { version = "2", features = ["postgres"] }
```
- Full ORM, migrations support
- Use for: When you want an ORM

### Error Handling

**anyhow** - Application errors
```toml
[dependencies]
anyhow = "1"
```
- Easy error propagation
- Use for: Applications (not libraries)

**thiserror** - Library errors
```toml
[dependencies]
thiserror = "1"
```
- Derive custom error types
- Use for: Libraries with custom errors

### Logging

**tracing** - Structured logging and tracing
```toml
[dependencies]
tracing = "0.1"
tracing-subscriber = "0.3"
```
- Async-aware, structured
- Use for: Modern applications, async code

**log** + **env_logger** - Simple logging
```toml
[dependencies]
log = "0.4"
env_logger = "0.11"
```
- Simple, widely supported
- Use for: Simple logging needs

### Testing

**proptest** - Property-based testing
```toml
[dev-dependencies]
proptest = "1"
```
- Generate test cases automatically
- Use for: Testing properties/invariants

**criterion** - Benchmarking
```toml
[dev-dependencies]
criterion = "0.5"
```
- Statistical benchmarking
- Use for: Performance testing

### Web Frameworks

**axum** - Modern, tokio-based
```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
```
- Ergonomic, type-safe
- Use for: New web services

**actix-web** - High performance
```toml
[dependencies]
actix-web = "4"
```
- Very fast, mature
- Use for: High-performance APIs

**rocket** - Batteries included
```toml
[dependencies]
rocket = "0.5"
```
- Easy to use, full-featured
- Use for: Rapid development

## Evaluation Workflow

1. **Search crates.io** - Find candidates by keywords
2. **Check metrics** - Downloads, version, recent updates
3. **Read docs** - Review docs.rs, examples
4. **Check dependencies** - Run `cargo tree` after adding
5. **Test it** - Try in small example first
6. **Monitor** - Watch for updates, security advisories

## Additional Resources

### Reference Files

For detailed crate comparisons:
- **`references/crate-categories.md`** - Comprehensive crate recommendations by category
- **`references/evaluation-checklist.md`** - Detailed crate evaluation criteria

Use these references to make informed decisions when selecting Rust crates for your project.
