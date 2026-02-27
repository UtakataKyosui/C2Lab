# Tauri v2 Plugin Structure Reference

## Generated Directory Layout

Running `cargo tauri plugin new <name>` generates:

```
tauri-plugin-<name>/
├── .github/
│   └── workflows/
│       └── test.yml          # CI configuration
├── examples/
│   └── tauri-app/            # Example app to test the plugin
│       ├── src/
│       ├── src-tauri/
│       │   ├── Cargo.toml
│       │   └── src/
│       │       └── lib.rs    # Plugin registered here
│       └── package.json
├── guest-js/                 # TypeScript/JavaScript bindings
│   ├── index.ts
│   ├── package.json
│   └── tsconfig.json
├── permissions/              # Permission definitions (Tauri v2 feature)
│   └── default.toml
├── src/                      # Rust source
│   ├── commands.rs
│   ├── error.rs
│   ├── lib.rs
│   └── models.rs
├── Cargo.toml
├── build.rs
└── README.md
```

## Cargo.toml Deep Dive

### Minimal Configuration

```toml
[package]
name = "tauri-plugin-<name>"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
description = "A Tauri plugin that..."
license = "MIT OR Apache-2.0"
repository = "https://github.com/you/tauri-plugin-<name>"

[dependencies]
tauri = { version = "2", default-features = false }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "2"

[build-dependencies]
tauri-build = { version = "2", default-features = false, features = ["codegen"] }
```

### Adding Features (for feature flags)

```toml
[features]
default = []
desktop = []
mobile = []

[target.'cfg(any(target_os = "android", target_os = "ios"))'.dependencies]
# Mobile-specific deps
```

### Workspace Setup (for monorepo)

If developing within a workspace:

```toml
# workspace Cargo.toml
[workspace]
members = [
    "tauri-plugin-<name>",
    "examples/tauri-app/src-tauri",
]
resolver = "2"
```

## Source Files

### lib.rs — Plugin Entry Point

```rust
// Re-export public types
pub use models::*;
pub use error::{Error, Result};

mod commands;
mod error;
mod models;

// Optional: platform-specific modules
#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

use tauri::{
    plugin::{Builder, TauriPlugin},
    Manager, Runtime,
};

/// Initialize the plugin.
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("<name>")
        .invoke_handler(tauri::generate_handler![
            commands::command_one,
            commands::command_two,
        ])
        .setup(|app, api| {
            #[cfg(mobile)]
            let handle = mobile::init(app, api)?;
            #[cfg(desktop)]
            let handle = desktop::init(app, api)?;

            app.manage(handle);
            Ok(())
        })
        .on_event(|_app, event| {
            // Handle app lifecycle events
            if let tauri::RunEvent::Exit = event {
                // Cleanup
            }
        })
        .build()
}
```

### commands.rs — Command Handlers

```rust
use tauri::{command, AppHandle, Runtime, State, Window};
use crate::{MyPluginExt, Result};

/// Simple command with typed return
#[command]
pub(crate) async fn greet<R: Runtime>(
    _app: AppHandle<R>,
    name: String,
) -> Result<String> {
    Ok(format!("Hello, {name}!"))
}

/// Command accessing plugin state
#[command]
pub(crate) async fn get_count<R: Runtime>(
    _app: AppHandle<R>,
    state: State<'_, MyState>,
) -> Result<u32> {
    Ok(*state.count.lock().unwrap())
}

/// Command that emits events
#[command]
pub(crate) async fn start_task<R: Runtime>(
    window: Window<R>,
    task_id: String,
) -> Result<()> {
    tauri::async_runtime::spawn(async move {
        // Do work...
        window.emit("plugin:<name>//task-complete", &task_id).ok();
    });
    Ok(())
}
```

### models.rs — Data Types

```rust
use serde::{Deserialize, Serialize};

/// Plugin configuration passed from JS
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MyConfig {
    pub option_a: String,
    pub option_b: Option<bool>,
}

/// Plugin state managed by Tauri
#[derive(Default)]
pub struct MyState {
    pub count: std::sync::Mutex<u32>,
}

/// Response type for commands
#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MyResponse {
    pub success: bool,
    pub data: Option<String>,
}
```

### error.rs — Error Types

```rust
use serde::{ser::Serializer, Serialize};

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Io(#[from] std::io::Error),
    #[error("Plugin error: {0}")]
    PluginError(String),
    // Add domain-specific variants
}

// Required: Tauri serializes errors to send to JS
impl Serialize for Error {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.to_string().as_ref())
    }
}
```

## build.rs — Permission Code Generation

```rust
const COMMANDS: &[&str] = &["greet", "get_count", "start_task"];

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

This auto-generates `allow-greet`, `allow-get-count`, `allow-start-task` permission identifiers.

## Permissions Directory

### permissions/default.toml

```toml
[default]
description = "Allows all plugin commands by default."
permissions = [
    "allow-greet",
    "allow-get-count",
]
# Note: Don't include dangerous commands in default
```

### Custom Permission Sets

Create additional `.toml` files in `permissions/`:

```toml
# permissions/read-only.toml
[[permission]]
identifier = "read-only"
description = "Allows only read operations."
commands.allow = ["get_count"]
```

## guest-js/package.json

```json
{
  "name": "@tauri-apps/plugin-<name>",
  "version": "0.1.0",
  "description": "Tauri plugin <name> bindings",
  "module": "./dist-js/index.mjs",
  "exports": {
    ".": {
      "import": "./dist-js/index.mjs"
    }
  },
  "files": ["dist-js"],
  "scripts": {
    "build": "rollup -c",
    "dev": "rollup -c --watch"
  },
  "dependencies": {
    "@tauri-apps/api": "^2"
  },
  "devDependencies": {
    "rollup": "^4",
    "typescript": "^5"
  }
}
```

## Registering in Consumer App

### src-tauri/Cargo.toml (App)

```toml
[dependencies]
# Local development
tauri-plugin-<name> = { path = "../../" }

# Or from crates.io
# tauri-plugin-<name> = "0.1"

# Or from git
# tauri-plugin-<name> = { git = "https://github.com/user/tauri-plugin-<name>" }
```

### src-tauri/src/lib.rs (App)

```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_<name>::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### src-tauri/capabilities/default.json (App)

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities",
  "windows": ["main"],
  "permissions": [
    "tauri-plugin-<name>:default"
  ]
}
```
