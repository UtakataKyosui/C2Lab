# Workspace Organization Patterns

## When to Use Workspaces

### Single Crate (No Workspace)

Good for:
- Simple applications
- Small libraries
- Prototypes
- Projects unlikely to grow

Structure:
```
project/
├── Cargo.toml
├── src/
│   └── lib.rs or main.rs
└── tests/
```

### Workspace (Multiple Crates)

Good for:
- Applications with plugins/extensions
- Libraries with multiple components
- Monorepos with related projects
- Projects with binaries and libraries

## Common Workspace Patterns

### Pattern 1: Binary + Library

Separate application logic from library:

```
project/
├── Cargo.toml  (workspace root)
├── lib/
│   ├── Cargo.toml
│   └── src/lib.rs
└── bin/
    ├── Cargo.toml
    └── src/main.rs
```

Root Cargo.toml:
```toml
[workspace]
members = ["lib", "bin"]

[workspace.dependencies]
# Shared dependencies
serde = "1.0"
```

bin/Cargo.toml:
```toml
[package]
name = "my-app"

[dependencies]
my-lib = { path = "../lib" }
serde = { workspace = true }
```

**Benefits:**
- Library can be used independently
- Binary depends on library
- Easy to test library separate from CLI

### Pattern 2: Multiple Binaries + Shared Code

Multiple tools sharing common code:

```
project/
├── Cargo.toml
├── common/
│   └── Cargo.toml
├── tool-a/
│   └── Cargo.toml
├── tool-b/
│   └── Cargo.toml
└── tool-c/
    └── Cargo.toml
```

Root Cargo.toml:
```toml
[workspace]
members = ["common", "tool-*"]

[workspace.dependencies]
common = { path = "common" }
```

Each tool depends on `common`:
```toml
[dependencies]
common = { workspace = true }
```

**Benefits:**
- Shared code in one place
- Independent binaries
- Consistent dependency versions

### Pattern 3: Layered Architecture

Organize by architectural layers:

```
project/
├── Cargo.toml
├── domain/          # Core business logic
├── adapters/        # External integrations
│   ├── db/
│   ├── api/
│   └── cli/
└── app/             # Application composition
```

Root Cargo.toml:
```toml
[workspace]
members = [
    "domain",
    "adapters/*",
    "app",
]
```

Dependency flow: app → adapters → domain

**Benefits:**
- Clear architectural boundaries
- Domain layer has no external dependencies
- Easy to test layers independently

### Pattern 4: Feature-Based Organization

Organize by features/modules:

```
project/
├── Cargo.toml
├── core/
├── features/
│   ├── auth/
│   ├── storage/
│   └── api/
└── app/
```

Root Cargo.toml:
```toml
[workspace]
members = [
    "core",
    "features/*",
    "app",
]
```

**Benefits:**
- Features are independent modules
- Can enable/disable features easily
- Clear feature boundaries

### Pattern 5: Workspace with Examples and Tools

Separate examples and development tools:

```
project/
├── Cargo.toml
├── lib/
│   └── Cargo.toml
├── examples/
│   ├── example-a/
│   │   └── Cargo.toml
│   └── example-b/
│       └── Cargo.toml
└── tools/
    ├── codegen/
    │   └── Cargo.toml
    └── benchmarks/
        └── Cargo.toml
```

Root Cargo.toml:
```toml
[workspace]
members = [
    "lib",
    "examples/*",
    "tools/*",
]
```

**Benefits:**
- Examples are full crates (more realistic)
- Tools can have different dependencies
- Clean separation of concerns

## Dependency Management Patterns

### Pattern A: Centralized Versions

All version numbers in workspace root:

```toml
# Root Cargo.toml
[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
anyhow = "1.0"

# Member Cargo.toml
[dependencies]
serde = { workspace = true }
tokio = { workspace = true, features = ["rt"] }  # Can add more features
anyhow = { workspace = true }
```

**Benefits:**
- Single source of truth for versions
- Easy to update versions
- Prevents version conflicts

### Pattern B: Feature Inheritance

Centralize common feature combinations:

```toml
# Root Cargo.toml
[workspace.dependencies]
tokio = { version = "1.0", features = ["rt-multi-thread", "macros", "net"] }
serde = { version = "1.0", features = ["derive"] }

# Member can add more features
[dependencies]
tokio = { workspace = true, features = ["fs"] }  # Adds "fs" to inherited features
```

### Pattern C: Optional Dependencies

Handle optional dependencies in workspace:

```toml
# Root Cargo.toml
[workspace.dependencies]
optional-dep = { version = "1.0", optional = true }

# Member Cargo.toml
[dependencies]
optional-dep = { workspace = true }  # Not optional here

[features]
feature1 = ["dep:optional-dep"]
```

## Build Optimization Patterns

### Pattern 1: Shared Build Cache

Workspace members share build artifacts:

```toml
[profile.dev.package."*"]
opt-level = 2  # Optimize dependencies, not workspace code
```

All members benefit from optimized dependencies.

### Pattern 2: Incremental Member Builds

Build only changed members:

```bash
cargo build -p changed-crate
cargo test -p changed-crate
```

### Pattern 3: Parallel Builds

Cargo builds independent crates in parallel automatically:

```
A → B → D
  ↘ C ↗
```

B and C build in parallel, D waits for both.

## Testing Patterns

### Pattern 1: Integration Tests in Separate Crate

```
project/
├── Cargo.toml
├── lib/
│   └── Cargo.toml
└── integration-tests/
    ├── Cargo.toml
    └── tests/
```

integration-tests/Cargo.toml:
```toml
[package]
name = "integration-tests"
publish = false

[dev-dependencies]
lib = { path = "../lib" }
```

**Benefits:**
- Tests use public API only
- Clear separation
- Doesn't affect lib's build time

### Pattern 2: Shared Test Utilities

```
project/
├── Cargo.toml
├── lib/
├── test-utils/
│   └── Cargo.toml  (publish = false)
└── integration-tests/
    └── Cargo.toml
```

Both lib and integration-tests can depend on test-utils.

## Release Patterns

### Pattern 1: Versioned Together

All workspace members share version:

```toml
[workspace.package]
version = "1.0.0"

# All members
[package]
version.workspace = true
```

Release all together with same version.

### Pattern 2: Independent Versioning

Each crate has its own version:

```toml
# member-a/Cargo.toml
[package]
version = "1.0.0"

# member-b/Cargo.toml
[package]
version = "2.0.0"
```

Release independently when changed.

### Pattern 3: cargo-release

Use cargo-release for coordinated releases:

```bash
cargo install cargo-release
cargo release --workspace  # Release all changed
cargo release -p specific-crate  # Release one
```

## Common Mistakes and Solutions

### Mistake 1: Circular Dependencies

❌ **Bad:**
```
crate-a → crate-b
crate-b → crate-a
```

✅ **Solution:** Extract shared code to new crate:
```
crate-a → common
crate-b → common
```

### Mistake 2: Too Many Small Crates

❌ **Bad:** 20 tiny crates with 50 lines each

✅ **Better:** Fewer, well-organized crates:
```
core/         # 1000 lines
features/     # Multiple features, ~500 lines each
app/          # 200 lines
```

**Rule of thumb:** Create new crate when:
- Code is reused by multiple binaries
- Clear architectural boundary
- Different release cycles needed
- Compilation time becomes problem

### Mistake 3: Dependency Duplication

❌ **Bad:**
```toml
# crate-a/Cargo.toml
[dependencies]
serde = "1.0.100"

# crate-b/Cargo.toml
[dependencies]
serde = "1.0.150"
```

Result: Two versions of serde in build.

✅ **Solution:** Use workspace dependencies:
```toml
[workspace.dependencies]
serde = "1.0"  # All use same version
```

### Mistake 4: Publishing Workspace Root

❌ **Bad:**
```toml
# Root Cargo.toml
[package]  # Don't do this
name = "workspace-root"
```

✅ **Better:**
```toml
# Root Cargo.toml
[workspace]  # No [package] section
members = ["..."]
```

Workspace root shouldn't be a package unless it's also a member.

## Migration Strategies

### From Single Crate to Workspace

1. **Create workspace structure:**
```bash
mkdir lib
mv src lib/
mv Cargo.toml lib/
```

2. **Create root Cargo.toml:**
```toml
[workspace]
members = ["lib"]
```

3. **Extract components:**
```bash
cargo new --lib lib/extracted-component
# Move code
```

4. **Add dependencies:**
```toml
# lib/Cargo.toml
[dependencies]
extracted-component = { path = "../extracted-component" }
```

### From Multiple Repos to Monorepo

1. **Create workspace:**
```bash
mkdir monorepo
cd monorepo
```

2. **Add each repo as member:**
```bash
git clone ../repo-a crates/repo-a
git clone ../repo-b crates/repo-b
```

3. **Create root Cargo.toml:**
```toml
[workspace]
members = ["crates/*"]

[workspace.dependencies]
# Extract common versions
```

4. **Convert inter-repo dependencies:**
```toml
# Before: External dependency
other-repo = "1.0"

# After: Path dependency
other-repo = { path = "../other-repo" }
```

## Best Practices Summary

1. **Start simple:** Begin with single crate, add workspace when needed
2. **Clear boundaries:** Each crate should have single responsibility
3. **Centralize versions:** Use `[workspace.dependencies]`
4. **Optimize builds:** Use profiles, incremental compilation
5. **Test independently:** Each crate should be testable alone
6. **Document structure:** Explain organization in README
7. **Avoid cycles:** Extract shared code to break circular dependencies
8. **Right size:** Not too many tiny crates, not one huge crate
9. **Consistent naming:** Use clear, consistent crate names
10. **Publish wisely:** Use `publish = false` for internal crates

Choose workspace pattern based on:
- Project size and complexity
- Team structure
- Release requirements
- Build time constraints
- Code reuse needs
