# Rust での OBS プラグイン実装

Rust で OBS プラグインを作成する場合、C API を直接 FFI で呼び出す。
`crate-type = ["cdylib"]` で共有ライブラリとしてビルドし、OBS が dlopen でロードする。

## Cargo.toml 設定

```toml
[package]
name = "my-obs-plugin"
version = "0.1.0"
edition = "2021"

[lib]
# 共有ライブラリとしてビルド（OBS が動的リンクでロード）
crate-type = ["cdylib"]

[dependencies]
libc = "0.2"

[build-dependencies]
# ヘッダーバインディング生成に bindgen を使う場合
bindgen = { version = "0.69", optional = true }

[features]
generate-bindings = ["bindgen"]
```

## FFI バインディングの定義

### 手動定義（最小限）

```rust
// src/ffi.rs
use std::ffi::{c_char, c_int, c_uint, c_void};

// OBS ソース種別
pub const OBS_SOURCE_TYPE_INPUT: u32  = 0;
pub const OBS_SOURCE_TYPE_FILTER: u32 = 1;
pub const OBS_SOURCE_TYPE_OUTPUT: u32 = 2;

// OBS 出力フラグ
pub const OBS_SOURCE_VIDEO: u32 = 1;
pub const OBS_SOURCE_AUDIO: u32 = 2;
pub const OBS_SOURCE_ASYNC: u32 = 4;

// ログレベル
pub const LOG_ERROR:   c_int = 100;
pub const LOG_WARNING: c_int = 200;
pub const LOG_INFO:    c_int = 300;
pub const LOG_DEBUG:   c_int = 400;

// 不透明ポインタ型
pub enum ObsSource {}
pub enum ObsData {}
pub enum GsEffect {}

/// OBS C 構造体（ABI互換）
#[repr(C)]
pub struct ObsSourceInfo {
    pub id: *const c_char,
    pub source_type: u32,
    pub output_flags: u32,
    pub get_name: Option<unsafe extern "C" fn(*mut c_void) -> *const c_char>,
    pub create: Option<unsafe extern "C" fn(*mut ObsData, *mut ObsSource) -> *mut c_void>,
    pub destroy: Option<unsafe extern "C" fn(*mut c_void)>,
    pub get_width: Option<unsafe extern "C" fn(*mut c_void) -> u32>,
    pub get_height: Option<unsafe extern "C" fn(*mut c_void) -> u32>,
    pub video_render: Option<unsafe extern "C" fn(*mut c_void, *mut GsEffect)>,
    pub update: Option<unsafe extern "C" fn(*mut c_void, *mut ObsData)>,
    pub get_properties: Option<unsafe extern "C" fn(*mut c_void) -> *mut c_void>,
    pub get_defaults: Option<unsafe extern "C" fn(*mut ObsData)>,
    // ... 他のフィールド（0で初期化）
    _padding: [u8; 256], // ABI変更への対応（大きめに確保）
}

// OBS API 関数
extern "C" {
    pub fn obs_register_source(info: *const ObsSourceInfo);
    pub fn blog(log_level: c_int, format: *const c_char, ...);
    pub fn obs_data_get_int(data: *mut ObsData, name: *const c_char) -> i64;
    pub fn obs_data_set_default_int(data: *mut ObsData, name: *const c_char, val: i64);
}
```

### bindgen での自動生成

```bash
# OBS ヘッダーからバインディングを生成
bindgen /usr/include/obs/obs-module.h \
    -- -I/usr/include/obs \
    > src/bindings.rs
```

## エントリポイントの実装

```rust
// src/lib.rs
mod ffi;
mod source;

use ffi::*;
use std::ffi::CStr;

// OBS モジュール識別子（必須）
static MODULE_NAME: &[u8] = b"my-obs-plugin\0";
static PLUGIN_VERSION: &[u8] = b"0.1.0\0";

/// OBS がプラグインロード時に呼び出す（必須）
#[no_mangle]
pub unsafe extern "C" fn obs_module_load() -> bool {
    obs_register_source(&source::SOURCE_INFO);

    let msg = b"my-obs-plugin loaded\0";
    blog(LOG_INFO, msg.as_ptr() as *const _);

    true
}

/// OBS がプラグインアンロード時に呼び出す（必須）
#[no_mangle]
pub unsafe extern "C" fn obs_module_unload() {
    let msg = b"my-obs-plugin unloaded\0";
    blog(LOG_INFO, msg.as_ptr() as *const _);
}
```

## ソース実装（安全な Rust パターン）

```rust
// src/source.rs
use crate::ffi::*;
use std::ffi::{c_char, c_void};

// Rust の安全な内部データ構造
struct MySourceData {
    width: u32,
    height: u32,
}

// SOURCE_INFO は static に配置（OBS が参照を保持するため）
pub static SOURCE_INFO: ObsSourceInfo = ObsSourceInfo {
    id: b"my_rust_source\0".as_ptr() as *const c_char,
    source_type: OBS_SOURCE_TYPE_INPUT,
    output_flags: OBS_SOURCE_VIDEO,
    get_name:       Some(source_get_name),
    create:         Some(source_create),
    destroy:        Some(source_destroy),
    get_width:      Some(source_get_width),
    get_height:     Some(source_get_height),
    video_render:   Some(source_render),
    update:         Some(source_update),
    get_properties: None,
    get_defaults:   Some(source_get_defaults),
    _padding: [0; 256],
};

unsafe extern "C" fn source_get_name(_type_data: *mut c_void) -> *const c_char {
    b"My Rust Source\0".as_ptr() as *const c_char
}

unsafe extern "C" fn source_create(settings: *mut ObsData, _source: *mut ObsSource) -> *mut c_void {
    let width  = obs_data_get_int(settings, b"width\0".as_ptr() as _) as u32;
    let height = obs_data_get_int(settings, b"height\0".as_ptr() as _) as u32;

    let data = Box::new(MySourceData { width, height });
    // raw ポインタとして OBS に渡す
    // OBS は destroy コールバックで返してくる
    Box::into_raw(data) as *mut c_void
}

unsafe extern "C" fn source_destroy(data_ptr: *mut c_void) {
    if !data_ptr.is_null() {
        // Box::from_raw で所有権を回収 → Drop で自動解放
        let _ = Box::from_raw(data_ptr as *mut MySourceData);
    }
}

unsafe extern "C" fn source_get_width(data_ptr: *mut c_void) -> u32 {
    let data = &*(data_ptr as *const MySourceData);
    data.width
}

unsafe extern "C" fn source_get_height(data_ptr: *mut c_void) -> u32 {
    let data = &*(data_ptr as *const MySourceData);
    data.height
}

unsafe extern "C" fn source_render(_data_ptr: *mut c_void, _effect: *mut GsEffect) {
    // 映像描画処理
}

unsafe extern "C" fn source_update(data_ptr: *mut c_void, settings: *mut ObsData) {
    let data = &mut *(data_ptr as *mut MySourceData);
    data.width  = obs_data_get_int(settings, b"width\0".as_ptr() as _) as u32;
    data.height = obs_data_get_int(settings, b"height\0".as_ptr() as _) as u32;
}

unsafe extern "C" fn source_get_defaults(settings: *mut ObsData) {
    obs_data_set_default_int(settings, b"width\0".as_ptr() as _, 1920);
    obs_data_set_default_int(settings, b"height\0".as_ptr() as _, 1080);
}
```

## CMake との連携（ハイブリッドビルド）

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(my-obs-plugin)

find_package(libobs REQUIRED)
find_package(Cargo REQUIRED)  # cargo-cmake 等

# Cargo でビルド
add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/libmy_obs_plugin.so
    COMMAND cargo build --release --manifest-path ${CMAKE_SOURCE_DIR}/Cargo.toml
    COMMAND cp ${CMAKE_SOURCE_DIR}/target/release/libmy_obs_plugin.so
               ${CMAKE_BINARY_DIR}/libmy_obs_plugin.so
    DEPENDS ${CMAKE_SOURCE_DIR}/src/*.rs ${CMAKE_SOURCE_DIR}/Cargo.toml
)

add_custom_target(my-obs-plugin ALL
    DEPENDS ${CMAKE_BINARY_DIR}/libmy_obs_plugin.so
)

install(
    FILES ${CMAKE_BINARY_DIR}/libmy_obs_plugin.so
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/obs-plugins"
    RENAME my-obs-plugin.so
)
```

## build.rs での OBS パス検出

```rust
// build.rs
fn main() {
    // OBS SDK のパスを環境変数から取得
    if let Ok(obs_lib) = std::env::var("OBS_LIB_DIR") {
        println!("cargo:rustc-link-search={}", obs_lib);
    }

    println!("cargo:rustc-link-lib=obs");
    println!("cargo:rerun-if-env-changed=OBS_LIB_DIR");
}
```

## 注意点

- `static SOURCE_INFO` に `unsafe impl Sync for ObsSourceInfo {}` が必要な場合がある
- `_padding` フィールドは OBS バージョン間の ABI 差を吸収するための余白
- `unsafe` ブロックを最小化し、FFI 境界を明確に分離する
- `Box::into_raw` / `Box::from_raw` のペアを必ず揃える（メモリリーク防止）
