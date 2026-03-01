# Rust OBS プラグインのテスト戦略

## 基本方針：ロジック層と FFI 層の分離

OBS に依存しない純粋なロジックを `logic/` モジュールに分離し、
`cargo test` で OBS 環境なしにテストする。

```
src/
├── lib.rs             # FFI エントリ（obs_module_load/unload）
├── source.rs          # FFI ラッパー（unsafe extern "C" fn）
├── filter.rs          # フィルター FFI ラッパー
└── logic/
    ├── mod.rs
    ├── processor.rs   # テスト可能なビジネスロジック
    └── config.rs      # 設定値の検証・変換
```

## ロジック層のテスト（OBS 非依存）

```rust
// src/logic/processor.rs

/// フレーム処理ロジック（OBS API 非依存）
pub struct VideoProcessor {
    pub width: u32,
    pub height: u32,
    pub brightness: f32,
    pub contrast: f32,
}

impl VideoProcessor {
    pub fn new(width: u32, height: u32) -> Result<Self, String> {
        if width == 0 || height == 0 {
            return Err("Width and height must be non-zero".to_string());
        }
        Ok(Self {
            width,
            height,
            brightness: 0.0,
            contrast: 1.0,
        })
    }

    pub fn set_brightness(&mut self, value: f32) {
        // -1.0 〜 1.0 にクランプ
        self.brightness = value.clamp(-1.0, 1.0);
    }

    pub fn set_contrast(&mut self, value: f32) {
        // 0.0 〜 4.0 にクランプ
        self.contrast = value.clamp(0.0, 4.0);
    }

    /// ピクセルに輝度・コントラスト補正を適用
    pub fn process_pixel(&self, rgba: [u8; 4]) -> [u8; 4] {
        let apply = |channel: u8| -> u8 {
            let f = channel as f32 / 255.0;
            let brightened = f + self.brightness;
            let contrasted = (brightened - 0.5) * self.contrast + 0.5;
            (contrasted.clamp(0.0, 1.0) * 255.0) as u8
        };

        [apply(rgba[0]), apply(rgba[1]), apply(rgba[2]), rgba[3]]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_valid() {
        let proc = VideoProcessor::new(1920, 1080).unwrap();
        assert_eq!(proc.width, 1920);
        assert_eq!(proc.height, 1080);
        assert_eq!(proc.brightness, 0.0);
        assert_eq!(proc.contrast, 1.0);
    }

    #[test]
    fn test_new_zero_width_fails() {
        let result = VideoProcessor::new(0, 1080);
        assert!(result.is_err());
    }

    #[test]
    fn test_brightness_clamped() {
        let mut proc = VideoProcessor::new(100, 100).unwrap();

        proc.set_brightness(2.0); // 範囲外
        assert_eq!(proc.brightness, 1.0);

        proc.set_brightness(-2.0); // 範囲外
        assert_eq!(proc.brightness, -1.0);
    }

    #[test]
    fn test_neutral_process_pixel() {
        let proc = VideoProcessor::new(100, 100).unwrap();
        // brightness=0, contrast=1 では変化なし
        let pixel = [128u8, 64, 200, 255];
        let result = proc.process_pixel(pixel);
        assert_eq!(result[3], 255); // アルファは変化しない
        // 近似値チェック（浮動小数点丸め誤差を許容）
        assert!((result[0] as i32 - 128).abs() <= 1);
    }

    #[test]
    fn test_brightness_increases_value() {
        let mut proc = VideoProcessor::new(100, 100).unwrap();
        proc.set_brightness(0.5);

        let pixel = [100u8, 100, 100, 255];
        let result = proc.process_pixel(pixel);
        assert!(result[0] > pixel[0]);
    }
}
```

## FFI 層のモック戦略

FFI 関数をテスト用にモックするには `cfg(test)` を使って差し替える:

```rust
// src/source.rs

/// OBS FFI（本番）
#[cfg(not(test))]
mod obs_api {
    use std::ffi::{c_char, c_void};

    extern "C" {
        pub fn obs_data_get_int(data: *mut c_void, name: *const c_char) -> i64;
        pub fn obs_data_set_default_int(data: *mut c_void, name: *const c_char, val: i64);
    }
}

/// OBS FFI（テスト用モック）
#[cfg(test)]
mod obs_api {
    use std::collections::HashMap;
    use std::ffi::{c_char, c_void, CStr};
    use std::cell::RefCell;

    thread_local! {
        static MOCK_DATA: RefCell<HashMap<String, i64>> = RefCell::new(HashMap::new());
    }

    pub fn set_mock_int(key: &str, val: i64) {
        MOCK_DATA.with(|m| m.borrow_mut().insert(key.to_string(), val));
    }

    pub unsafe fn obs_data_get_int(data: *mut c_void, name: *const c_char) -> i64 {
        let key = CStr::from_ptr(name).to_str().unwrap_or("");
        MOCK_DATA.with(|m| *m.borrow().get(key).unwrap_or(&0))
    }

    pub unsafe fn obs_data_set_default_int(_data: *mut c_void, _name: *const c_char, _val: i64) {
        // テストでは無視
    }
}

/// ソースの設定を安全に読み込む
pub fn read_source_config(settings: *mut std::ffi::c_void) -> (u32, u32) {
    unsafe {
        let width  = obs_api::obs_data_get_int(settings, b"width\0".as_ptr() as _) as u32;
        let height = obs_api::obs_data_get_int(settings, b"height\0".as_ptr() as _) as u32;
        (width, height)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_read_config() {
        obs_api::set_mock_int("width",  1920);
        obs_api::set_mock_int("height", 1080);

        let (w, h) = read_source_config(std::ptr::null_mut());
        assert_eq!(w, 1920);
        assert_eq!(h, 1080);
    }
}
```

## 統合テスト（tests/ ディレクトリ）

```rust
// tests/integration_test.rs
use my_obs_plugin::logic::processor::VideoProcessor;

#[test]
fn test_full_frame_processing() {
    let mut proc = VideoProcessor::new(4, 4).unwrap();
    proc.set_brightness(0.1);
    proc.set_contrast(1.2);

    // 4x4 フレームを処理
    let frame: Vec<[u8; 4]> = (0..16)
        .map(|i| [(i * 16) as u8, (i * 8) as u8, 100u8, 255u8])
        .collect();

    let result: Vec<[u8; 4]> = frame.iter()
        .map(|&pixel| proc.process_pixel(pixel))
        .collect();

    // アルファチャンネルは変化しない
    for pixel in &result {
        assert_eq!(pixel[3], 255);
    }

    // すべてのピクセルが有効な範囲内
    for pixel in &result {
        for &channel in &pixel[0..3] {
            assert!(channel <= 255);
        }
    }
}
```

## テスト実行コマンド

```bash
# 全テスト実行
cargo test

# 特定のテストモジュール
cargo test logic::processor

# 詳細出力（println! を表示）
cargo test -- --nocapture

# 失敗時に停止
cargo test -- --test-threads=1

# 統合テストのみ
cargo test --test integration_test

# ドキュメントテスト
cargo test --doc

# カバレッジ計測（cargo-tarpaulin が必要）
cargo tarpaulin --out Html
```

## メモリ安全性のチェック（Miri）

```bash
# Miri のインストール
rustup component add miri

# unsafe コードの実行チェック
cargo miri test

# 特定テスト
cargo miri test test_create_destroy
```

## Rust での AddressSanitizer

```bash
# nightly が必要
RUSTFLAGS="-Z sanitizer=address" \
    cargo +nightly test \
    --target x86_64-unknown-linux-gnu

# または
cargo +nightly test -Z build-std \
    --target x86_64-unknown-linux-gnu \
    -- ASAN_OPTIONS=detect_leaks=1
```
