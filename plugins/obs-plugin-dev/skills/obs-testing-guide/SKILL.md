---
name: obs-testing-guide
description: "OBS Studioプラグインのテスト・デバッグガイド。C/C++ユニットテスト、Rustのcargo test、gdb/lldbデバッグ、Valgrindメモリチェック、blog()ログ出力、AddressSanitizerの使い方に関する質問時に使用する。"
version: 0.1.0
globs:
  - "**/test/**/*.c"
  - "**/tests/**/*.c"
  - "**/*_test.c"
  - "**/test_*.c"
  - "**/*.rs"
  - "**/*.supp"
---

# OBS プラグインのテスト・デバッグガイド

## テスト環境のセットアップ

### 必要なツール

```bash
# Linux（Ubuntu/Debian）
sudo apt install \
    obs-studio \
    gdb \
    valgrind \
    libasan8 \
    cmake \
    ninja-build

# macOS
brew install obs lldb cmake ninja

# Rust プロジェクトの場合
rustup component add rust-src
cargo install cargo-expand  # マクロ展開確認
```

### デバッグビルドの作成

```bash
# C/C++ プロジェクト
cmake -B build-debug \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build-debug

# Rust プロジェクト
cargo build  # debug ビルド（デフォルト）
```

---

## `blog()` でのログ出力

OBS のログシステムを使った基本的なデバッグ手法:

```c
// C/C++: obs-module.h をインクルード
blog(LOG_INFO,    "width=%d, height=%d", width, height);
blog(LOG_WARNING, "設定ファイルが見つかりません");
blog(LOG_ERROR,   "テクスチャ生成失敗");
blog(LOG_DEBUG,   "コールバック呼び出し: %s", __func__);
```

```rust
// Rust: FFI 経由でログ出力
extern "C" {
    fn blog(level: i32, format: *const u8, ...);
}

macro_rules! obs_log {
    ($level:expr, $msg:literal) => {
        unsafe { blog($level, concat!($msg, "\0").as_ptr()) }
    };
}

obs_log!(300, "プラグインが初期化されました");
```

ログの確認:
```bash
# Linux
tail -f ~/.config/obs-studio/logs/*.txt

# OBS 起動時の詳細ログ
obs --verbose 2>&1 | grep "my-plugin"
```

---

## C/C++ テストパターン

OBS 依存部分をモックしてユニットテストを実施する。

### カスタムテストハーネス

```c
// test/test_utils.h
#pragma once
#include <stdio.h>
#include <stdlib.h>

static int test_pass_count = 0;
static int test_fail_count = 0;

#define ASSERT_EQ(a, b) do { \
    if ((a) == (b)) { \
        test_pass_count++; \
        printf("  PASS: " #a " == " #b "\n"); \
    } else { \
        test_fail_count++; \
        printf("  FAIL: " #a " == " #b " (got %d vs %d)\n", (int)(a), (int)(b)); \
    } \
} while(0)

#define ASSERT_NOT_NULL(p) do { \
    if ((p) != NULL) { \
        test_pass_count++; \
    } else { \
        test_fail_count++; \
        printf("  FAIL: " #p " should not be NULL\n"); \
    } \
} while(0)

#define RUN_TEST(fn) do { \
    printf("Running: " #fn "\n"); \
    fn(); \
} while(0)

#define PRINT_RESULTS() do { \
    printf("\n結果: %d passed, %d failed\n", test_pass_count, test_fail_count); \
    exit(test_fail_count > 0 ? 1 : 0); \
} while(0)
```

詳細: `references/test-patterns.md`

---

## Rust テストパターン

Rust の `#[cfg(test)]` を使ってビジネスロジックをテスト。

### ロジック層と FFI 層の分離

```
src/
├── lib.rs          # FFI エントリポイント（obs_module_load等）
├── source.rs       # FFI ラッパー（unsafe extern "C" fn）
└── logic/
    ├── mod.rs      # ロジック層（OBS非依存・テスト可能）
    └── processing.rs
```

```rust
// src/logic/processing.rs - OBS 非依存のビジネスロジック
pub struct FrameProcessor {
    pub width: u32,
    pub height: u32,
    pub intensity: f32,
}

impl FrameProcessor {
    pub fn new(width: u32, height: u32) -> Self {
        Self { width, height, intensity: 1.0 }
    }

    pub fn apply_grayscale(&self, pixel: [u8; 4]) -> [u8; 4] {
        let gray = (pixel[0] as f32 * 0.299
                  + pixel[1] as f32 * 0.587
                  + pixel[2] as f32 * 0.114) as u8;
        [gray, gray, gray, pixel[3]]
    }

    pub fn pixel_count(&self) -> u64 {
        self.width as u64 * self.height as u64
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_processor() {
        let proc = FrameProcessor::new(1920, 1080);
        assert_eq!(proc.width, 1920);
        assert_eq!(proc.height, 1080);
        assert_eq!(proc.intensity, 1.0);
    }

    #[test]
    fn test_grayscale_red_pixel() {
        let proc = FrameProcessor::new(100, 100);
        let red = [255, 0, 0, 255];
        let result = proc.apply_grayscale(red);
        // R=255 の場合: gray = 255 * 0.299 ≈ 76
        assert_eq!(result[0], result[1]);
        assert_eq!(result[1], result[2]);
        assert_eq!(result[3], 255); // アルファは保持
    }

    #[test]
    fn test_pixel_count() {
        let proc = FrameProcessor::new(1920, 1080);
        assert_eq!(proc.pixel_count(), 1920 * 1080);
    }
}
```

```bash
# テスト実行
cargo test

# 特定のテストのみ
cargo test test_grayscale

# 詳細出力
cargo test -- --nocapture
```

詳細: `references/rust-testing.md`

---

## GDB/LLDB デバッグセッション

```bash
# GDB（Linux）
gdb --args obs --scene test-scene
(gdb) break my_source_create
(gdb) run
# ブレークポイントで停止したら
(gdb) info locals  # ローカル変数表示
(gdb) bt           # バックトレース
(gdb) p data->width  # 変数の値確認

# LLDB（macOS）
lldb -- obs
(lldb) breakpoint set --name my_source_create
(lldb) run
(lldb) frame variable
```

---

## Valgrind / AddressSanitizer

### Valgrind（メモリリーク）

```bash
valgrind --leak-check=full \
         --track-origins=yes \
         obs 2>&1 | grep "my-plugin"
```

### AddressSanitizer（ASan）

```bash
# CMake
cmake -B build-asan \
    -DCMAKE_C_FLAGS="-fsanitize=address -g" \
    -DCMAKE_BUILD_TYPE=Debug

# Rust
RUSTFLAGS="-Z sanitizer=address" cargo +nightly test \
    --target x86_64-unknown-linux-gnu
```

---

## OBS 内統合テスト

```bash
# OBS にテスト用シーンを用意して起動
obs --scene obs-plugin-test.json --verbose

# プラグインのロード確認
grep "my-plugin" ~/.config/obs-studio/logs/*.txt

# 特定シーンで動作確認後、OBS を終了
obs --scene test.json --minimize-to-tray
```

---

## 参考ファイル

- **`references/test-patterns.md`** - C 言語テストの実装例（モックOBS API）
- **`references/rust-testing.md`** - Rust テスト戦略（cargo test、FFIモック、ロジック分離）
