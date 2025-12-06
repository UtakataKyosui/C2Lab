# Complete Cargo.toml Reference

## Package Metadata

```toml
[package]
name = "my-crate"
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
edition = "2021"                    # Rust edition: 2015, 2018, 2021
rust-version = "1.70"               # Minimum supported Rust version (MSRV)
description = "A short description"
documentation = "https://docs.rs/my-crate"
readme = "README.md"
homepage = "https://example.com"
repository = "https://github.com/user/repo"
license = "MIT OR Apache-2.0"
license-file = "LICENSE"            # Or use this for custom license
keywords = ["cli", "tool"]          # Max 5 keywords
categories = ["command-line-utilities"]  # See https://crates.io/categories
publish = false                     # Prevent accidental publishing
```

## Dependencies

### Basic Dependencies

```toml
[dependencies]
# From crates.io
serde = "1.0"
tokio = "1"

# Git dependency
my-lib = { git = "https://github.com/user/repo" }
my-lib = { git = "https://github.com/user/repo", branch = "main" }
my-lib = { git = "https://github.com/user/repo", tag = "v1.0.0" }
my-lib = { git = "https://github.com/user/repo", rev = "abc123" }

# Path dependency
my-lib = { path = "../my-lib" }

# With features
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
tokio = { version = "1", default-features = false, features = ["rt"] }

# Optional dependency (for features)
optional-dep = { version = "1.0", optional = true }

# Renamed dependency
actix-rt = { package = "tokio", version = "1" }
```

### Version Requirements

```toml
[dependencies]
# Caret (default): ^1.2.3 means >=1.2.3, <2.0.0
serde = "1.2.3"
serde = "^1.2.3"

# Tilde: ~1.2.3 means >=1.2.3, <1.3.0
serde = "~1.2.3"

# Exact
serde = "=1.2.3"

# Comparison
serde = ">= 1.2.3"
serde = ">= 1.2, < 1.5"

# Wildcard
serde = "1.*"
serde = "*"  # Any version (not recommended)
```

### Dependency Types

```toml
[dependencies]
# Normal runtime dependencies
serde = "1.0"

[dev-dependencies]
# Only for tests, examples, benchmarks
criterion = "0.5"
proptest = "1.0"

[build-dependencies]
# Only for build scripts
cc = "1.0"
```

## Features

```toml
[features]
# Default features enabled
default = ["std", "feature1"]

# Feature flags
std = []
feature1 = ["dep:optional-dep"]
feature2 = ["feature1", "serde/derive"]
full = ["feature1", "feature2"]

[dependencies]
optional-dep = { version = "1.0", optional = true }
serde = { version = "1.0", optional = true }
```

Using features:
```bash
cargo build                           # With default features
cargo build --no-default-features     # Without defaults
cargo build --features feature1       # With specific feature
cargo build --all-features            # With all features
```

## Workspace Configuration

### Root Cargo.toml

```toml
[workspace]
members = [
    "crate-a",
    "crate-b",
    "tools/*",
]
exclude = [
    "old-code",
    "experiments",
]

# Shared dependency versions
[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"

# Shared metadata
[workspace.package]
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
edition = "2021"
license = "MIT"
```

### Member Cargo.toml

```toml
[package]
name = "crate-a"
version.workspace = true
authors.workspace = true
edition.workspace = true

[dependencies]
# Inherit from workspace
serde = { workspace = true }
tokio = { workspace = true }

# Override features
serde = { workspace = true, features = ["rc"] }

# Add dependencies not in workspace
local-only = "1.0"
```

## Build Configuration

### Profiles

```toml
[profile.dev]
opt-level = 0              # 0=no optimization, 3=max optimization
debug = true               # Include debug info
debug-assertions = true    # Enable debug assertions
overflow-checks = true     # Check for integer overflow
lto = false                # Link-time optimization
panic = 'unwind'           # or 'abort'
incremental = true         # Incremental compilation
codegen-units = 256        # Parallel code generation units
rpath = false              # Runtime library search path

[profile.release]
opt-level = 3
debug = false
debug-assertions = false
overflow-checks = false
lto = true                 # or "fat", "thin"
panic = 'abort'
incremental = false
codegen-units = 1          # Better optimization
strip = true               # Strip symbols (1.59+)

# Optimize dependencies in dev mode
[profile.dev.package."*"]
opt-level = 2

# Custom profile
[profile.production]
inherits = "release"
lto = "fat"
codegen-units = 1
```

### Target-Specific Dependencies

```toml
[target.'cfg(unix)'.dependencies]
libc = "0.2"

[target.'cfg(windows)'.dependencies]
winapi = "0.3"

[target.'cfg(target_arch = "wasm32")'.dependencies]
wasm-bindgen = "0.2"
```

## Patch and Replace

### Patching Dependencies

```toml
[patch.crates-io]
# Replace crates.io version with git
serde = { git = "https://github.com/serde-rs/serde" }

# Replace with local path
tokio = { path = "../tokio" }

[patch.'https://github.com/user/repo']
# Patch git dependency
my-lib = { path = "../my-lib" }
```

### Replacing Dependencies

```toml
[replace]
# Deprecated, use [patch] instead
"foo:0.1.0" = { git = "https://github.com/user/foo" }
```

## Lints Configuration (1.74+)

```toml
[lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[lints.clippy]
all = "deny"
pedantic = "warn"
cargo = "warn"
nursery = "warn"

# Allow specific lints
enum_glob_use = "allow"

[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
all = "deny"
```

## Build Scripts

```toml
[package]
build = "build.rs"          # Build script path

[build-dependencies]
cc = "1.0"
```

build.rs:
```rust
fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    // Build logic here
}
```

## Metadata

Custom metadata for tools:

```toml
[package.metadata.docs.rs]
all-features = true
targets = ["x86_64-unknown-linux-gnu"]

[package.metadata.release]
sign-commit = true
```

## Bins, Libs, Examples

```toml
# Binary
[[bin]]
name = "my-bin"
path = "src/bin/my-bin.rs"
required-features = ["feature1"]

# Library
[lib]
name = "my_lib"
path = "src/lib.rs"
crate-type = ["lib"]  # or ["dylib"], ["staticlib"], ["cdylib"]

# Example
[[example]]
name = "demo"
path = "examples/demo.rs"
required-features = ["feature1"]

# Test
[[test]]
name = "integration"
path = "tests/integration.rs"

# Benchmark
[[bench]]
name = "perf"
path = "benches/perf.rs"
harness = false  # Don't use built-in test harness
```

## Badges

```toml
[badges]
maintenance = { status = "actively-developed" }
```

## Advanced Features

### Resolver

```toml
[package]
resolver = "2"  # Use new feature resolver

[workspace]
resolver = "2"
```

### Links

```toml
[package]
links = "foo"  # Only one crate can link to native library "foo"

[package.metadata.pkg-config]
foo = "1.0"
```

## Complete Example

```toml
[package]
name = "my-awesome-crate"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"
authors = ["Developer <dev@example.com>"]
description = "An awesome Rust crate"
license = "MIT OR Apache-2.0"
repository = "https://github.com/user/my-awesome-crate"
keywords = ["cli", "awesome"]
categories = ["command-line-utilities"]

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["rt-multi-thread", "macros"] }
anyhow = "1.0"
clap = { version = "4.0", features = ["derive"] }

[dev-dependencies]
criterion = "0.5"

[features]
default = ["full"]
full = ["feature1", "feature2"]
feature1 = []
feature2 = ["dep:optional-dep"]

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

[lints.clippy]
all = "deny"
pedantic = "warn"
```

## See Also

- Official Cargo Book: https://doc.rust-lang.org/cargo/
- Cargo Reference: https://doc.rust-lang.org/cargo/reference/
- Manifest Format: https://doc.rust-lang.org/cargo/reference/manifest.html
