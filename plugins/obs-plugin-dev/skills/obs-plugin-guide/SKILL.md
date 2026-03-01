---
name: obs-plugin-guide
description: "OBS Studio プラグイン開発ガイド。C/C++またはRustでのOBSプラグイン作成、obs_module_load/unload実装、ソース・フィルター・出力・エンコーダープラグインの構造、CMakeLists.txt設定、OBS SDK APIの使い方、RustでのFFIアプローチに関する質問時に使用する。"
version: 0.1.0
globs:
  - "**/CMakeLists.txt"
  - "**/*.c"
  - "**/*.cpp"
  - "**/*.h"
  - "**/Cargo.toml"
  - "**/build.rs"
---

# OBS Studio プラグイン開発ガイド

## プラグインの種類

OBS Studio には以下の種類のプラグインがある:

| 種類 | 用途 | 主要構造体 |
|------|------|-----------|
| **ソースプラグイン** | カメラ・キャプチャなど映像/音声源 | `obs_source_info` |
| **フィルタープラグイン** | 映像/音声のエフェクト処理 | `obs_source_info` (type=FILTER) |
| **出力プラグイン** | 配信・録画先の定義 | `obs_output_info` |
| **エンコーダープラグイン** | 映像/音声エンコード | `obs_encoder_info` |

## 言語選択: C/C++ vs Rust

### C/C++ アプローチ（推奨・実績多）

**メリット**:
- OBS SDK がネイティブ C API
- `obs-plugintemplate` などテンプレートが充実
- コミュニティサポートが豊富

**デメリット**:
- 手動メモリ管理（`bzalloc`/`bfree` の使用が必要）
- バッファオーバーフロー等のリスク

### Rust アプローチ（安全性重視）

**メリット**:
- メモリ安全性（コンパイル時保証）
- `unsafe` ブロックで FFI 境界を明示

**デメリット**:
- FFI バインディングの手動実装が必要
- `obs-rs` 等のラッパーは発展途上
- CMake との連携設定が複雑

---

## C/C++ アプローチ

### プロジェクト構造（obs-plugintemplate ベース）

```
my-obs-plugin/
├── CMakeLists.txt
├── src/
│   ├── plugin-main.c      # obs_module_load / obs_module_unload
│   └── my-source.c        # ソース実装
├── data/
│   └── locale/
│       └── en-US.ini      # 文字列リソース
└── buildspec.json         # OBS ビルドシステム設定
```

### 必須エントリポイント

```c
// plugin-main.c
#include <obs-module.h>

OBS_DECLARE_MODULE()
OBS_MODULE_USE_DEFAULT_LOCALE("my-plugin", "en-US")

bool obs_module_load(void)
{
    // ソース・フィルター等を登録
    obs_register_source(&my_source_info);
    blog(LOG_INFO, "Plugin loaded successfully");
    return true;
}

void obs_module_unload(void)
{
    blog(LOG_INFO, "Plugin unloaded");
}
```

### obs_source_info 構造体（ソースプラグイン）

```c
struct obs_source_info my_source_info = {
    .id            = "my_source",           // 一意な ID（必須）
    .type          = OBS_SOURCE_TYPE_INPUT, // プラグイン種別
    .output_flags  = OBS_SOURCE_VIDEO,      // 出力フラグ
    .get_name      = my_source_get_name,    // 表示名取得
    .create        = my_source_create,      // インスタンス生成
    .destroy       = my_source_destroy,     // インスタンス破棄
    .update        = my_source_update,      // プロパティ変更時
    .get_properties = my_source_properties, // UI プロパティ定義
    .video_render  = my_source_render,      // 映像描画（毎フレーム）
    .get_width     = my_source_get_width,
    .get_height    = my_source_get_height,
};
```

### メモリ管理の基本

OBS では標準の `malloc`/`free` ではなく `bzalloc`/`bfree` を使う:

```c
// 確保: bzalloc でゼロ初期化
struct my_data *data = bzalloc(sizeof(struct my_data));

// 解放: bfree で解放
bfree(data);

// 文字列の複製
char *name = bstrdup(source_name);
bfree(name); // 使い終わったら解放
```

### CMakeLists.txt の基本設定

詳細: `references/cmake-setup.md`

```cmake
cmake_minimum_required(VERSION 3.16)
project(my-obs-plugin VERSION 0.1.0)

find_package(libobs REQUIRED)

add_library(my-obs-plugin MODULE
    src/plugin-main.c
    src/my-source.c
)

target_link_libraries(my-obs-plugin
    OBS::libobs
)
```

---

## Rust アプローチ

### Cargo.toml 設定

```toml
[package]
name = "my-obs-plugin"
version = "0.1.0"
edition = "2021"

[lib]
# 共有ライブラリとしてビルド（OBS が dlopen でロード）
crate-type = ["cdylib"]

[dependencies]
# OBS との FFI には libc を使用
libc = "0.2"
```

### エントリポイントの実装

```rust
// src/lib.rs
use std::ffi::c_int;

/// OBS がプラグインロード時に呼び出す
#[no_mangle]
pub unsafe extern "C" fn obs_module_load() -> bool {
    // ソース情報を登録
    unsafe {
        obs_register_source(&MY_SOURCE_INFO);
    }
    true
}

/// OBS がプラグインアンロード時に呼び出す
#[no_mangle]
pub unsafe extern "C" fn obs_module_unload() {
    // クリーンアップ処理
}
```

### obs_source_info を Rust で定義

```rust
use std::ffi::{c_char, c_void};

// OBS の C 構造体と ABI 互換にするため repr(C) が必須
#[repr(C)]
pub struct ObsSourceInfo {
    pub id: *const c_char,
    pub source_type: u32,
    pub output_flags: u32,
    pub get_name: Option<unsafe extern "C" fn(type_data: *mut c_void) -> *const c_char>,
    pub create: Option<unsafe extern "C" fn(settings: *mut c_void, source: *mut c_void) -> *mut c_void>,
    pub destroy: Option<unsafe extern "C" fn(data: *mut c_void)>,
    // ... 他のフィールド
}

static MY_SOURCE_INFO: ObsSourceInfo = ObsSourceInfo {
    id: b"my_rust_source\0".as_ptr() as *const c_char,
    source_type: OBS_SOURCE_TYPE_INPUT,
    output_flags: OBS_SOURCE_VIDEO,
    get_name: Some(my_source_get_name),
    create: Some(my_source_create),
    destroy: Some(my_source_destroy),
    // ...
};
```

### メモリ管理（Rust の場合）

```rust
// Box を使ってデータを管理
unsafe extern "C" fn my_source_create(
    settings: *mut ObsData,
    source: *mut ObsSource,
) -> *mut c_void {
    let data = Box::new(MySourceData {
        source,
        width: 1920,
        height: 1080,
    });
    // raw ポインタとして OBS に渡す（OBS が destroy で返してくる）
    Box::into_raw(data) as *mut c_void
}

unsafe extern "C" fn my_source_destroy(data_ptr: *mut c_void) {
    // Box::from_raw で所有権を回収 → スコープ終了時に自動解放
    let _ = Box::from_raw(data_ptr as *mut MySourceData);
}
```

### build.rs での OBS SDK パス検出

```rust
// build.rs
fn main() {
    // OBS SDK のヘッダーパスを環境変数から取得
    let obs_include = std::env::var("OBS_INCLUDE_DIR")
        .unwrap_or_else(|_| "/usr/include/obs".to_string());

    println!("cargo:rerun-if-env-changed=OBS_INCLUDE_DIR");
    println!("cargo:include={}", obs_include);
}
```

詳細: `references/rust-approach.md`

---

## インストール先（プラットフォーム別）

| OS | インストールパス |
|----|---------------|
| Linux | `~/.config/obs-studio/plugins/<plugin-name>/bin/64bit/` |
| macOS | `~/Library/Application Support/obs-studio/plugins/<plugin-name>/bin/` |
| Windows | `%APPDATA%\obs-studio\plugins\<plugin-name>\bin\64bit\` |

システム全体にインストールする場合:
- Linux: `/usr/lib/obs-plugins/`
- macOS: `/Library/Application Support/obs-studio/plugins/`

---

## 参考ファイル

- **`references/cmake-setup.md`** - CMakeLists.txt の詳細設定・find_package/FetchContent
- **`references/source-plugin.md`** - ソースプラグイン実装例（C/C++）
- **`references/filter-plugin.md`** - フィルタープラグイン実装例（C/C++）
- **`references/api-reference.md`** - OBS API リファレンス（obs-module.h / obs.h 等）
- **`references/rust-approach.md`** - Rust での FFI 実装、cargo + cmake 連携
- **`references/debugging.md`** - GDB/Valgrind/AddressSanitizer 活用
