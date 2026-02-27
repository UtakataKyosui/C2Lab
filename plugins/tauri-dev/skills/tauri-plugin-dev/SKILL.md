---
name: Tauri Plugin Development
description: This skill should be used when the user wants to create, scaffold, implement, test, or debug a Tauri v2 plugin, or asks about Tauri plugin commands, TypeScript bindings, Rust backend patterns, or plugin structure. Covers the full Tauri v2 plugin development lifecycle.
version: 0.1.0
---

# Tauri v2 Plugin Development

## Overview

Tauri plugins extend Tauri applications with native capabilities. A plugin provides:
- **Rust backend**: Core logic, system API access, and command handlers
- **TypeScript bindings**: JavaScript API for frontend consumption
- **Build configuration**: Cargo.toml and build.rs for compilation

Plugins follow the naming convention `tauri-plugin-<name>`, with the corresponding crate name `tauri-plugin-<name>` and guest bindings at `@tauri-apps/plugin-<name>`.

## Creating a New Plugin

### Using the Official CLI (Recommended)

```bash
# Tauri CLI v2 required
cargo install tauri-cli
cargo tauri plugin new <plugin-name>
```

This generates the full project structure. Alternatively, use `npx @tauri-apps/cli plugin new <plugin-name>`.

The CLI creates:
```
tauri-plugin-<name>/
├── Cargo.toml               # Rust crate configuration
├── build.rs                 # Build script (generates permissions)
├── src/
│   ├── lib.rs               # Plugin implementation (entry point)
│   ├── commands.rs          # Command handlers
│   ├── models.rs            # Data types (optional)
│   └── error.rs             # Error types
├── permissions/
│   └── default.toml         # Default permission set
├── guest-js/
│   ├── package.json
│   ├── index.ts             # TypeScript API
│   └── tsconfig.json
└── examples/                # Example Tauri apps
```

See `references/plugin-structure.md` for detailed file-by-file breakdown.

## Core Rust Implementation

### Plugin Entry Point (lib.rs)

Every Tauri v2 plugin uses the `Builder` pattern:

```rust
use tauri::plugin::{Builder, TauriPlugin};
use tauri::{Manager, Runtime};

pub use models::*;
pub use error::{Error, Result};

mod commands;
mod error;
mod models;

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("<plugin-name>")
        .invoke_handler(tauri::generate_handler![
            commands::do_something,
        ])
        .setup(|app, api| {
            // Initialize plugin state
            app.manage(MyState::default());
            Ok(())
        })
        .build()
}
```

### Command Handlers (commands.rs)

Commands are async Rust functions exposed to the frontend:

```rust
use tauri::{command, AppHandle, Runtime, State};
use crate::{MyState, Result};

#[command]
pub(crate) async fn do_something<R: Runtime>(
    app: AppHandle<R>,
    state: State<'_, MyState>,
    payload: String,
) -> Result<String> {
    // Implementation
    Ok(format!("processed: {payload}"))
}
```

### Error Handling (error.rs)

```rust
use serde::{ser::Serializer, Serialize};

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Io(#[from] std::io::Error),
    #[error("{0}")]
    Custom(String),
}

impl Serialize for Error {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where S: Serializer {
        serializer.serialize_str(self.to_string().as_ref())
    }
}
```

See `references/rust-patterns.md` for state management, events, and advanced patterns.

## TypeScript Bindings

### Basic invoke() Pattern (guest-js/index.ts)

```typescript
import { invoke } from '@tauri-apps/api/core';

export async function doSomething(payload: string): Promise<string> {
  return await invoke<string>('plugin:<plugin-name>|do_something', {
    payload,
  });
}
```

**Important**: Tauri v2 uses `plugin:<name>|<command>` format for plugin commands.

### Event Listeners

```typescript
import { listen } from '@tauri-apps/api/event';

export async function onPluginEvent(
  handler: (data: MyEventData) => void,
): Promise<() => void> {
  return await listen<MyEventData>('plugin:<plugin-name>//my-event', handler);
}
```

See `references/typescript-bindings.md` for full API reference, type generation, and build setup.

## Cargo.toml Configuration

```toml
[package]
name = "tauri-plugin-<name>"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2", default-features = false }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "2"

[build-dependencies]
tauri-build = { version = "2", default-features = false, features = ["codegen"] }
```

## Registering in an App

```rust
// In the Tauri app's src-tauri/src/lib.rs
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_<name>::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```toml
# In the app's src-tauri/Cargo.toml
[dependencies]
tauri-plugin-<name> = { path = "../tauri-plugin-<name>" }
```

## Permissions System (Tauri v2)

Tauri v2 requires explicit permission declarations. Create `permissions/default.toml`:

```toml
[default]
description = "Default permissions for plugin-<name>"
permissions = ["allow-do-something"]
```

The `build.rs` auto-generates permission types from command names:

```rust
const COMMANDS: &[&str] = &["do_something"];

fn main() {
    tauri_build::mobile_entry_point_exists();
    tauri_build::try_build(
        tauri_build::Attributes::new()
            .plugin(
                tauri_build::PluginBuilder::new()
                    .commands(COMMANDS)
                    .build(),
            ),
    )
    .expect("failed to run tauri-build");
}
```

## Testing

### Rust Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_core_logic() {
        // Test plugin logic without Tauri runtime
        let result = process_data("input");
        assert_eq!(result, "expected");
    }
}
```

### Integration Testing

Use the `tauri::test` module for testing with a mock app handle:

```rust
#[cfg(test)]
mod tests {
    use tauri::test::{mock_app, MockRuntime};

    #[test]
    fn test_plugin_init() {
        let app = mock_app();
        // Test plugin integration
    }
}
```

See `references/testing-debugging.md` for full testing strategies and debugging techniques.

## Common Workflow

1. **Scaffold**: `cargo tauri plugin new <name>`
2. **Define models**: Add types to `models.rs`
3. **Implement commands**: Add handlers to `commands.rs`
4. **Register commands**: Update `lib.rs` invoke_handler
5. **Add permissions**: Create entries in `permissions/`
6. **Write TypeScript**: Implement bindings in `guest-js/index.ts`
7. **Test**: Write unit tests, then integration tests
8. **Integrate**: Add to test Tauri app in `examples/`

## Mobile Plugin Workflow

When targeting iOS or Android, extend the standard workflow with these steps:

1. **Split implementation**: Create `src/desktop.rs` (AppHandle-based) and `src/mobile.rs` (PluginHandle wrapper)
2. **Update lib.rs**: Add `#[cfg(desktop)]`/`#[cfg(mobile)]` module declarations and branch in `.setup()`
3. **Update Cargo.toml**: Add `mobile = []` feature and `[target.'cfg(any(target_os = "android", target_os = "ios"))'.dependencies]` section
4. **Add native code**: Create `android/` (Kotlin `@TauriPlugin` class) and/or `ios/` (Swift `Plugin` subclass)
5. **Initialize project**: Run `tauri android init` / `tauri ios init` to generate platform directories
6. **Develop**: Use `tauri android dev` / `tauri ios dev` for live development

See `references/mobile-support.md` for complete Kotlin/Swift examples, permission setup, and error troubleshooting.

## Additional Resources

### Reference Files

- **`references/plugin-structure.md`** - Detailed file structure and Cargo workspace setup
- **`references/rust-patterns.md`** - State management, events, mobile support, advanced patterns
- **`references/typescript-bindings.md`** - Full TypeScript API, type generation, npm packaging
- **`references/testing-debugging.md`** - Testing strategies, logging, common errors, troubleshooting
- **`references/mobile-support.md`** - Complete iOS/Android implementation: Kotlin, Swift, permissions, errors
