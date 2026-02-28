# TypeScript Bindings for Tauri v2 Plugins

## Command Invocation

### Basic invoke() Pattern

```typescript
import { invoke } from '@tauri-apps/api/core';

// Plugin commands use the format: plugin:<plugin-name>|<command_name>
export async function greet(name: string): Promise<string> {
  return await invoke<string>('plugin:my-plugin|greet', { name });
}
```

**Note**: Command names use snake_case in Rust but are invoked as-is. The `|` separator is unique to plugin commands (app commands use the command name directly).

### Typed Parameters and Responses

```typescript
export interface MyConfig {
  optionA: string;
  optionB?: boolean;
}

export interface MyResponse {
  success: boolean;
  data?: string;
}

export async function configure(config: MyConfig): Promise<MyResponse> {
  return await invoke<MyResponse>('plugin:my-plugin|configure', { config });
}
```

**Serialization**: Rust structs with `#[serde(rename_all = "camelCase")]` map to camelCase TypeScript types.

### Error Handling

```typescript
export class PluginError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'PluginError';
  }
}

export async function riskyOperation(input: string): Promise<string> {
  try {
    return await invoke<string>('plugin:my-plugin|risky_operation', { input });
  } catch (err) {
    // Tauri serializes Rust errors as strings
    throw new PluginError(String(err));
  }
}
```

## Event Listeners

### Listen for Plugin Events

```typescript
import { listen, type UnlistenFn } from '@tauri-apps/api/event';

export interface ProgressPayload {
  taskId: string;
  percent: number;
}

// Returns an unlisten function to clean up
export async function onProgress(
  handler: (payload: ProgressPayload) => void,
): Promise<UnlistenFn> {
  return await listen<ProgressPayload>('plugin:my-plugin//progress', (event) => {
    handler(event.payload);
  });
}
```

**Note**: Plugin events use `plugin:<name>//<event-name>` format with double slash.

### React/Solid Integration Pattern

```typescript
import { useEffect, useState } from 'react';
import { onProgress, type ProgressPayload } from '@tauri-apps/plugin-my-plugin';

export function TaskProgress({ taskId }: { taskId: string }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let unlisten: (() => void) | undefined;

    onProgress((payload) => {
      if (payload.taskId === taskId) {
        setProgress(payload.percent);
      }
    }).then((fn) => {
      unlisten = fn;
    });

    return () => {
      unlisten?.();
    };
  }, [taskId]);

  return <progress value={progress} max={100} />;
}
```

## Complete index.ts Structure

```typescript
import { invoke } from '@tauri-apps/api/core';
import { listen, type UnlistenFn } from '@tauri-apps/api/event';

// Re-export types
export type { MyConfig, MyResponse };

// Types
export interface MyConfig {
  optionA: string;
  optionB?: boolean;
}

export interface MyResponse {
  success: boolean;
  data?: string;
}

// Commands
export async function doSomething(payload: string): Promise<string> {
  return await invoke<string>('plugin:my-plugin|do_something', { payload });
}

export async function getCount(): Promise<number> {
  return await invoke<number>('plugin:my-plugin|get_count');
}

// Events
export async function onComplete(
  handler: (taskId: string) => void,
): Promise<UnlistenFn> {
  return await listen<string>('plugin:my-plugin//complete', (event) => {
    handler(event.payload);
  });
}
```

## Build Setup

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "declaration": true,
    "declarationDir": "./dist-js",
    "outDir": "./dist-js"
  },
  "include": ["*.ts"]
}
```

### rollup.config.js

```javascript
import typescript from '@rollup/plugin-typescript';
import { readFileSync } from 'fs';

const pkg = JSON.parse(readFileSync('./package.json', 'utf8'));

export default {
  input: 'index.ts',
  output: [
    {
      file: pkg.exports['.'].import,
      format: 'esm',
    },
  ],
  plugins: [typescript()],
  external: [/^@tauri-apps\//],
};
```

### Building

```bash
cd guest-js
pnpm install
pnpm build  # Outputs to dist-js/
```

## Using the Plugin in a Tauri App

### Installation

```bash
# Install the JS bindings
pnpm add @tauri-apps/plugin-my-plugin

# Or for local development
pnpm add ../path/to/tauri-plugin-my-plugin/guest-js
```

### Frontend Usage

```typescript
// In your frontend code
import { doSomething, onComplete } from '@tauri-apps/plugin-my-plugin';

// Call a command
const result = await doSomething('hello');
console.log(result);

// Listen for events
const unlisten = await onComplete((taskId) => {
  console.log('Task completed:', taskId);
});

// Cleanup when done
unlisten();
```

## Type Generation from Rust (specta)

For automatic TypeScript type generation from Rust types, use `specta`:

```toml
# Cargo.toml
[dependencies]
specta = "2"
tauri-specta = { version = "2", features = ["javascript", "typescript"] }
```

```rust
use specta::Type;
use tauri_specta::{collect_commands, ts};

#[derive(Type, Serialize, Deserialize)]
pub struct MyType {
    pub field: String,
}

// Generate types
fn export_types() {
    ts::export(collect_commands![greet, do_something], "../guest-js/bindings.ts")
        .expect("Failed to export bindings");
}
```

This generates TypeScript interfaces directly from Rust structs, eliminating manual type duplication.

## Capability Configuration

The consuming app must declare permissions in its capabilities:

```json
// src-tauri/capabilities/default.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "tauri-plugin-my-plugin:default",
    "tauri-plugin-my-plugin:allow-get-count"
  ]
}
```

## Common Patterns

### Polling with Cleanup

```typescript
export function startPolling(
  intervalMs: number,
  handler: (data: DataItem) => void,
): () => void {
  const id = setInterval(async () => {
    const data = await getData();
    handler(data);
  }, intervalMs);

  return () => clearInterval(id);
}
```

### Command with Timeout

```typescript
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Command timed out')), timeoutMs),
  );
  return Promise.race([promise, timeout]);
}

export async function doSomethingWithTimeout(payload: string): Promise<string> {
  return withTimeout(doSomething(payload), 5000);
}
```
