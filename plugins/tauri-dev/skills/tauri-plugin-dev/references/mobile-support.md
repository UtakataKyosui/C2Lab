# Mobile Support for Tauri v2 Plugins

## Architecture Overview

Tauri v2 uses a bridge architecture to invoke native mobile code from Rust:

```
TypeScript (invoke) → Rust PluginHandle::run_mobile_plugin
  → Android: JNI → Kotlin @TauriPlugin class (@Command methods)
  → iOS:     ObjC bridge → Swift Plugin class (@objc func)
```

Desktop platforms (`cfg(desktop)`) use direct `AppHandle` access. Mobile platforms (`cfg(mobile)`) proxy calls through `PluginHandle` to the native layer.

---

## Directory Structure

A mobile-capable plugin requires additional directories alongside the standard Rust crate:

```
tauri-plugin-example/
├── android/
│   ├── build.gradle.kts
│   └── src/main/
│       ├── AndroidManifest.xml
│       └── kotlin/com/example/plugin/ExamplePlugin.kt
├── ios/
│   ├── Package.swift
│   └── Sources/ExamplePlugin/ExamplePlugin.swift
├── src/
│   ├── lib.rs        # cfg branching to unify desktop/mobile
│   ├── desktop.rs    # Desktop-only implementation
│   ├── mobile.rs     # PluginHandle wrapper for mobile
│   ├── commands.rs   # Tauri command handlers
│   ├── models.rs     # Shared data types
│   └── error.rs      # Error types
└── Cargo.toml
```

---

## Rust Side

### mobile.rs — Complete Implementation

```rust
use serde::de::DeserializeOwned;
use tauri::{
    plugin::{PluginHandle, PluginApi},
    AppHandle, Runtime,
};
use crate::models::*;

pub fn init<R: Runtime, C: DeserializeOwned>(
    app: &AppHandle<R>,
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

**Key points:**
- `register_android_plugin` takes `(package_name, class_name)` — must match Kotlin exactly.
- `register_ios_plugin` takes a function pointer `init_plugin_example` — must match the `@_cdecl` name in Swift exactly.
- Each method maps to a mobile command name (camelCase string) and typed request/response structs.

### desktop.rs — Complete Implementation

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
        // Desktop-native implementation using AppHandle
        Ok(DoSomethingResponse {
            value: format!("done: {}", payload.input),
        })
    }
}
```

### lib.rs — cfg Branching

```rust
#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

mod commands;
mod error;
mod models;

pub use error::{Error, Result};
pub use models::*;

#[cfg(desktop)]
use desktop::ExamplePlugin;
#[cfg(mobile)]
use mobile::ExamplePlugin;

pub fn init<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R> {
    tauri::plugin::Builder::new("example")
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

### Cargo.toml — Mobile Feature and Target-Specific Deps

```toml
[package]
name = "tauri-plugin-example"
version = "0.1.0"
edition = "2021"

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]
mobile = []

[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
thiserror = "2"
tauri = { version = "2", default-features = false }

[target.'cfg(any(target_os = "android", target_os = "ios"))'.dependencies]
tauri = { version = "2", default-features = false }

[build-dependencies]
tauri-build = { version = "2", default-features = false, features = ["codegen"] }
```

---

## Android (Kotlin)

### ExamplePlugin.kt — Complete Implementation

```kotlin
package com.example.plugin

import android.app.Activity
import app.tauri.annotation.Command
import app.tauri.annotation.TauriPlugin
import app.tauri.plugin.Invoke
import app.tauri.plugin.JSObject
import app.tauri.plugin.Plugin

@TauriPlugin
class ExamplePlugin(private val activity: Activity) : Plugin(activity) {

    @Command
    fun doSomething(invoke: Invoke) {
        val args = invoke.parseArgs(DoSomethingArgs::class.java)
        val result = JSObject()
        result.put("value", "done: ${args.input}")
        invoke.resolve(result)
    }
}

data class DoSomethingArgs(val input: String = "")
```

**Key points:**
- The `package` declaration must match the first argument to `register_android_plugin` in `mobile.rs`.
- The class name must match the second argument to `register_android_plugin`.
- Each `@Command` method name corresponds to the string passed to `run_mobile_plugin` (camelCase).
- `invoke.reject("message")` is used for errors; `invoke.resolve(jsObject)` for success.

### build.gradle.kts

```kotlin
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.plugin"
    compileSdk = 34
    defaultConfig {
        minSdk = 24
    }
}

dependencies {
    implementation("app.tauri:tauri-android:2.+")
}
```

### AndroidManifest.xml — Permission Examples

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Camera access -->
    <uses-permission android:name="android.permission.CAMERA" />
    <!-- Fine location -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <!-- Coarse location (less precise, lower permission tier) -->
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <!-- Internet access (no user prompt required) -->
    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
```

Request runtime permissions in your `@Command` method using the standard Android `ActivityCompat.requestPermissions` API or the Tauri `requestPermissions` helper when available.

---

## iOS (Swift)

### ExamplePlugin.swift — Complete Implementation

```swift
import SwiftRs
import Tauri
import UIKit
import WebKit

class DoSomethingArgs: Decodable {
    let input: String
}

class ExamplePlugin: Plugin {
    @objc public func doSomething(_ invoke: Invoke) throws {
        let args = try invoke.parseArgs(DoSomethingArgs.self)
        invoke.resolve(["value": "done: \(args.input)"])
    }
}

// Rust calls this C-symbol to obtain the plugin instance
@_cdecl("init_plugin_example")
func initPlugin() -> Plugin {
    return ExamplePlugin()
}
```

**Key points:**
- The `@_cdecl` symbol name must match the function pointer passed to `register_ios_plugin` in `mobile.rs`.
- Each `@objc public func` name corresponds to the camelCase string in `run_mobile_plugin`.
- `invoke.reject("message")` for errors; `invoke.resolve([...])` for success.
- `SwiftRs` and `Tauri` packages are provided by the Tauri iOS SDK.

### Package.swift

```swift
// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "ExamplePlugin",
    platforms: [.iOS(.v13)],
    products: [
        .library(
            name: "ExamplePlugin",
            targets: ["ExamplePlugin"]
        )
    ],
    dependencies: [
        .package(name: "Tauri", path: "../.tauri/tauri-api")
    ],
    targets: [
        .target(
            name: "ExamplePlugin",
            dependencies: [
                .product(name: "Tauri", package: "Tauri")
            ],
            path: "Sources/ExamplePlugin"
        )
    ]
)
```

### Info.plist — Permission Examples

```xml
<!-- Camera access -->
<key>NSCameraUsageDescription</key>
<string>This plugin uses the camera to ...</string>

<!-- Location access (when-in-use) -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>This plugin uses your location to ...</string>

<!-- Microphone access -->
<key>NSMicrophoneUsageDescription</key>
<string>This plugin uses the microphone to ...</string>
```

---

## Development Commands

```bash
# Android
tauri android init          # Generate android/ directory
tauri android dev           # Launch on emulator / connected device
tauri android build         # Build APK or AAB

# iOS (macOS + Xcode required)
tauri ios init              # Generate ios/ directory
tauri ios dev               # Launch on simulator / connected device
tauri ios build             # Build IPA
```

---

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ClassNotFoundException: com.example.plugin.ExamplePlugin` | Android package/class name mismatch | Ensure Kotlin `package` declaration and class name match the arguments in `register_android_plugin` |
| `undefined symbol: init_plugin_example` | iOS init function name mismatch | Ensure `@_cdecl("init_plugin_example")` matches the function pointer passed to `register_ios_plugin` |
| `mobile_entry_point_exists` build error | Outdated `tauri-build` | Update `tauri-build` to `"2"` in `Cargo.toml` |
| `NDK is not installed` | Android NDK missing | Install via Android Studio → SDK Manager → NDK (Side by side) |
| `cargo: no such command: ndk` | `cargo-ndk` not installed | Run `cargo install cargo-ndk`, then retry |
| `PluginApi` method not found | Wrong Tauri v2 API version | Confirm `tauri = "2"` in `Cargo.toml`; check for alpha/beta suffix |
| Swift compiler error on `@_cdecl` | Missing `SwiftRs` import | Add `import SwiftRs` at the top of the Swift file |
