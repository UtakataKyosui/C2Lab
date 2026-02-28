# Rust Implementation Patterns for Tauri v2 Plugins

## State Management

### Basic State Pattern

```rust
// models.rs
use std::sync::Mutex;

pub struct PluginState {
    pub config: Mutex<PluginConfig>,
    pub data: Mutex<Vec<DataItem>>,
}

impl Default for PluginState {
    fn default() -> Self {
        Self {
            config: Mutex::new(PluginConfig::default()),
            data: Mutex::new(Vec::new()),
        }
    }
}
```

Register state in `lib.rs`:

```rust
.setup(|app, _api| {
    app.manage(PluginState::default());
    Ok(())
})
```

Access in commands:

```rust
#[command]
pub async fn update_config<R: Runtime>(
    _app: AppHandle<R>,
    state: State<'_, PluginState>,
    new_config: PluginConfig,
) -> Result<()> {
    *state.config.lock().unwrap() = new_config;
    Ok(())
}
```

### Async State with Tokio

For non-blocking state access:

```rust
use tokio::sync::RwLock;

pub struct PluginState {
    pub data: RwLock<HashMap<String, DataItem>>,
}

// In command:
#[command]
pub async fn get_item<R: Runtime>(
    _app: AppHandle<R>,
    state: State<'_, PluginState>,
    key: String,
) -> Result<Option<DataItem>> {
    let data = state.data.read().await;
    Ok(data.get(&key).cloned())
}
```

## Event Emission

### Emit from Commands

```rust
use tauri::{Emitter, Window};

#[command]
pub async fn do_work<R: Runtime>(
    window: Window<R>,
    task_id: String,
) -> Result<()> {
    // Emit progress events
    window.emit("plugin:<name>//progress", ProgressPayload {
        task_id: task_id.clone(),
        percent: 50,
    })?;

    // Emit completion
    window.emit("plugin:<name>//complete", &task_id)?;
    Ok(())
}
```

### Emit from Background Tasks

```rust
#[command]
pub async fn start_background<R: Runtime>(
    app: AppHandle<R>,
) -> Result<()> {
    let app_clone = app.clone();
    tauri::async_runtime::spawn(async move {
        loop {
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
            let _ = app_clone.emit("plugin:<name>//tick", ());
        }
    });
    Ok(())
}
```

## Extension Trait Pattern

Provide ergonomic API via extension trait:

```rust
// In lib.rs
use tauri::{AppHandle, Manager, Runtime};
use crate::PluginState;

pub trait MyPluginExt<R: Runtime> {
    fn my_plugin(&self) -> &PluginState;
}

impl<R: Runtime, T: Manager<R>> MyPluginExt<R> for T {
    fn my_plugin(&self) -> &PluginState {
        self.state::<PluginState>().inner()
    }
}
```

Usage in app code:

```rust
// Consumer can access plugin state via extension trait
let state = app.my_plugin();
```

## Mobile Support

### Platform-Specific Implementation

For mobile, Tauri v2 proxies commands through `PluginHandle` to native Kotlin (Android) or Swift (iOS) code. Desktop platforms access the OS directly via `AppHandle`.

Split the implementation into `desktop.rs` and `mobile.rs`, unified through `lib.rs` with `#[cfg]` attributes.

```
src/
├── lib.rs        # cfg branching, plugin entry point
├── desktop.rs    # AppHandle-based desktop implementation
├── mobile.rs     # PluginHandle wrapper (JNI / ObjC bridge)
└── commands.rs
```

**mobile.rs — supports both Android and iOS:**

```rust
use serde::de::DeserializeOwned;
use tauri::{
    plugin::{PluginHandle, PluginApi},
    AppHandle, Runtime,
};
use crate::models::*;

pub fn init<R: Runtime, C: DeserializeOwned>(
    _app: &AppHandle<R>,
    api: PluginApi<R, C>,
) -> crate::Result<ExamplePlugin<R>> {
    #[cfg(target_os = "android")]
    let handle = api.register_android_plugin("com.example.plugin", "ExamplePlugin")?;
    #[cfg(target_os = "ios")]
    let handle = api.register_ios_plugin(init_plugin_example)?;
    Ok(ExamplePlugin(handle))
}

pub struct ExamplePlugin<R: Runtime>(PluginHandle<R>);

impl<R: Runtime> ExamplePlugin<R> {
    pub fn do_something(
        &self,
        payload: DoSomethingRequest,
    ) -> crate::Result<DoSomethingResponse> {
        self.0
            .run_mobile_plugin("doSomething", payload)
            .map_err(Into::into)
    }
}
```

**desktop.rs — AppHandle-based implementation:**

```rust
use tauri::{AppHandle, Runtime};
use crate::models::*;

pub fn init<R: Runtime>(
    app: &AppHandle<R>,
    _api: tauri::plugin::PluginApi<R, ()>,
) -> crate::Result<ExamplePlugin<R>> {
    Ok(ExamplePlugin(app.clone()))
}

pub struct ExamplePlugin<R: Runtime>(AppHandle<R>);

impl<R: Runtime> ExamplePlugin<R> {
    pub fn do_something(
        &self,
        payload: DoSomethingRequest,
    ) -> crate::Result<DoSomethingResponse> {
        Ok(DoSomethingResponse {
            value: format!("done: {}", payload.input),
        })
    }
}
```

**lib.rs — `#[cfg]` branching:**

```rust
#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("example")
        .setup(|app, api| {
            #[cfg(mobile)]
            let plugin = mobile::init(app, api)?;
            #[cfg(desktop)]
            let plugin = desktop::init(app, api)?;
            app.manage(plugin);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![commands::do_something])
        .build()
}
```

**Cargo.toml — mobile feature and target-specific deps:**

```toml
[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
mobile = []

[target.'cfg(any(target_os = "android", target_os = "ios"))'.dependencies]
tauri = { version = "2", default-features = false }
```

For Android (Kotlin) and iOS (Swift) native implementations, see `references/mobile-support.md`.

## Configuration from Plugin Options

Accept configuration at initialization:

```rust
#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PluginOptions {
    pub timeout_secs: Option<u64>,
    pub verbose: Option<bool>,
}

pub fn init<R: Runtime>(options: PluginOptions) -> TauriPlugin<R> {
    Builder::<R, PluginOptions>::new("<name>")
        .invoke_handler(tauri::generate_handler![/* ... */])
        .setup(move |app, api| {
            let config = api.config();
            // config contains the Tauri.toml plugin config
            app.manage(MyState::new(options));
            Ok(())
        })
        .build()
}
```

App usage:

```rust
.plugin(tauri_plugin_myname::init(PluginOptions {
    timeout_secs: Some(30),
    verbose: Some(true),
}))
```

## File System Access

```rust
use tauri::path::BaseDirectory;
use tauri::Manager;

#[command]
pub async fn read_config<R: Runtime>(app: AppHandle<R>) -> Result<String> {
    let path = app.path().resolve("config.json", BaseDirectory::AppConfig)?;
    let content = std::fs::read_to_string(path)?;
    Ok(content)
}
```

## Handling Long-Running Operations

Pattern for cancellable tasks:

```rust
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

pub struct TaskState {
    pub running: Arc<AtomicBool>,
}

#[command]
pub async fn start_long_task<R: Runtime>(
    window: Window<R>,
    state: State<'_, TaskState>,
) -> Result<()> {
    let running = state.running.clone();
    running.store(true, Ordering::SeqCst);

    tauri::async_runtime::spawn(async move {
        while running.load(Ordering::SeqCst) {
            // Do work...
            window.emit("plugin:<name>//progress", ()).ok();
            tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        }
        window.emit("plugin:<name>//stopped", ()).ok();
    });
    Ok(())
}

#[command]
pub async fn stop_long_task<R: Runtime>(
    _app: AppHandle<R>,
    state: State<'_, TaskState>,
) -> Result<()> {
    state.running.store(false, Ordering::SeqCst);
    Ok(())
}
```

## Common Third-Party Dependencies

```toml
[dependencies]
# Async runtime (Tauri includes tokio)
tokio = { version = "1", features = ["full"] }

# HTTP client
reqwest = { version = "0.12", features = ["json"] }

# Serialization
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Error handling
thiserror = "2"
anyhow = "1"  # For internal errors

# Logging
log = "0.4"
```

## Logging Best Practices

```rust
use log::{debug, error, info, warn};

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("<name>")
        .setup(|_app, _api| {
            info!("Plugin <name> initialized");
            Ok(())
        })
        .build()
}

#[command]
pub async fn do_something<R: Runtime>(_app: AppHandle<R>, input: String) -> Result<String> {
    debug!("do_something called with: {input}");
    let result = process(input)?;
    info!("do_something succeeded");
    Ok(result)
}
```

Enable logs in consumer app:

```rust
// App's lib.rs
tauri::Builder::default()
    .plugin(tauri_plugin_log::Builder::default()
        .level(log::LevelFilter::Info)
        .build())
    .plugin(tauri_plugin_myname::init())
```
