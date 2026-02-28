# Testing & Debugging Tauri v2 Plugins

## Rust Unit Testing

### Testing Pure Logic (No Tauri)

Keep business logic separate from Tauri types for easy unit testing:

```rust
// business_logic.rs - Tauri-free module
pub fn process_data(input: &str) -> Result<String, String> {
    if input.is_empty() {
        return Err("Input cannot be empty".to_string());
    }
    Ok(format!("processed: {input}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_data_success() {
        let result = process_data("hello").unwrap();
        assert_eq!(result, "processed: hello");
    }

    #[test]
    fn test_process_data_empty() {
        let result = process_data("");
        assert!(result.is_err());
    }
}
```

### Testing with Tokio

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tokio::test;

    #[tokio::test]
    async fn test_async_operation() {
        let result = async_process("input").await.unwrap();
        assert_eq!(result, "expected");
    }
}
```

### Testing State

```rust
#[cfg(test)]
mod tests {
    use std::sync::Mutex;
    use super::*;

    #[test]
    fn test_state_update() {
        let state = PluginState {
            count: Mutex::new(0),
        };

        *state.count.lock().unwrap() += 1;
        assert_eq!(*state.count.lock().unwrap(), 1);
    }
}
```

## Integration Testing with Tauri

### Using tauri::test Module

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tauri::test::{mock_app, MockRuntime};

    #[test]
    fn test_plugin_registers() {
        let app = mock_app();
        // Verify plugin state is registered
        let state = app.state::<PluginState>();
        assert_eq!(*state.count.lock().unwrap(), 0);
    }
}
```

### Testing Commands with MockRuntime

```rust
#[cfg(test)]
mod tests {
    use tauri::test::{mock_app, MockRuntime};
    use super::commands;

    #[tokio::test]
    async fn test_greet_command() {
        let app = mock_app();
        // Direct function call (not through invoke)
        let result = commands::greet::<MockRuntime>(
            app.handle().clone(),
            "World".to_string(),
        ).await;
        assert_eq!(result.unwrap(), "Hello, World!");
    }
}
```

## Running Tests

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_process_data

# Run tests for a specific module
cargo test commands::tests

# Watch mode (requires cargo-watch)
cargo watch -x test
```

## Logging for Debugging

### Setup in Plugin

```rust
use log::{debug, error, info, trace, warn};

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("<name>")
        .setup(|app, _api| {
            info!("Plugin initialized");
            debug!("Debug mode active: {}", cfg!(debug_assertions));
            Ok(())
        })
        .build()
}
```

### Setup in Test App

Add `tauri-plugin-log` to the example app:

```toml
# examples/tauri-app/src-tauri/Cargo.toml
[dependencies]
tauri-plugin-log = "2"
```

```rust
// examples/tauri-app/src-tauri/src/lib.rs
pub fn run() {
    tauri::Builder::default()
        .plugin(
            tauri_plugin_log::Builder::default()
                .level(log::LevelFilter::Debug)
                .build()
        )
        .plugin(tauri_plugin_myname::init())
        .run(tauri::generate_context!())
        .expect("error running app");
}
```

### View Logs

```bash
# macOS: Logs appear in Console.app or terminal stdout
# Enable with RUST_LOG environment variable
RUST_LOG=debug cargo tauri dev
```

## Common Errors & Solutions

### Error: "IPC handler not found"

**Cause**: Command not registered in `invoke_handler!`

**Solution**:
```rust
.invoke_handler(tauri::generate_handler![
    commands::my_command,  // Ensure this is listed
])
```

### Error: "Permission denied" / "Command not allowed"

**Cause**: Capability file missing permission for command

**Solution**: Add to `src-tauri/capabilities/default.json`:
```json
{
  "permissions": [
    "tauri-plugin-<name>:allow-my-command"
  ]
}
```

### Error: "Failed to serialize response"

**Cause**: Return type doesn't implement `Serialize`, or Error type missing `Serialize`

**Solution**: Check `error.rs` has:
```rust
impl Serialize for Error {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where S: Serializer {
        serializer.serialize_str(self.to_string().as_ref())
    }
}
```

### Error: Type mismatch between Rust and TypeScript

**Cause**: Naming convention mismatch (`snake_case` vs `camelCase`)

**Solution**: Add `#[serde(rename_all = "camelCase")]` to Rust structs:
```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MyConfig {
    pub option_a: String,  // Serializes as "optionA"
}
```

### Error: Plugin state not found (panics)

**Cause**: State not managed before command executes

**Solution**: Ensure state is registered in setup:
```rust
.setup(|app, _api| {
    app.manage(MyState::default());  // Must be called
    Ok(())
})
```

### Build Error: "cannot find function `mobile_entry_point_exists`"

**Cause**: Old `tauri-build` version

**Solution**: Update `build-dependencies`:
```toml
[build-dependencies]
tauri-build = { version = "2", features = ["codegen"] }
```

## Debugging in VS Code

### launch.json for debugging

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Debug Tauri App",
      "cargo": {
        "args": ["build", "--manifest-path=./examples/tauri-app/src-tauri/Cargo.toml"],
        "filter": { "name": "tauri-app", "kind": "bin" }
      },
      "args": [],
      "cwd": "${workspaceFolder}/examples/tauri-app"
    }
  ]
}
```

### Using RUST_BACKTRACE

```bash
RUST_BACKTRACE=1 cargo tauri dev
# Full backtrace
RUST_BACKTRACE=full cargo tauri dev
```

## Testing TypeScript Bindings

### Vitest Setup

```typescript
// guest-js/index.test.ts
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock Tauri's invoke
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

import { invoke } from '@tauri-apps/api/core';
import { greet } from './index';

describe('greet', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls invoke with correct parameters', async () => {
    (invoke as ReturnType<typeof vi.fn>).mockResolvedValue('Hello, World!');

    const result = await greet('World');

    expect(invoke).toHaveBeenCalledWith('plugin:my-plugin|greet', { name: 'World' });
    expect(result).toBe('Hello, World!');
  });

  it('propagates errors from invoke', async () => {
    (invoke as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'));

    await expect(greet('World')).rejects.toThrow('Network error');
  });
});
```

```bash
# Run TypeScript tests
cd guest-js
pnpm test
```

## CI Configuration

### .github/workflows/test.yml

```yaml
name: Tests

on: [push, pull_request]

jobs:
  rust-tests:
    runs-on: ubuntu-latest
    steps:
      # セキュリティ強化: 本番CIではSHAピン留めを推奨 (例: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683)
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test --all-features

  typescript-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: |
          cd guest-js
          npm install
          npm test
```
