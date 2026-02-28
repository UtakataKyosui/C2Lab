# Tauri v2 ビルド・デプロイ

## 開発ビルド

```bash
# 開発サーバー起動（ホットリロード有効）
npm run tauri dev
cargo tauri dev

# 特定のウィンドウラベルを指定
cargo tauri dev -- --no-watch

# リリースモードで開発（最適化あり、デバッグシンボルなし）
cargo tauri dev --release
```

## プロダクションビルド

```bash
# デスクトップ向けビルド（インストーラー生成）
npm run tauri build
cargo tauri build

# デバッグビルド（サイズ大・速度遅いがデバッグ可能）
cargo tauri build --debug

# 特定のターゲット向けビルド
cargo tauri build --target x86_64-unknown-linux-gnu
cargo tauri build --target x86_64-pc-windows-msvc
cargo tauri build --target universal-apple-darwin  # macOS Universal Binary
```

## ビルド出力

```
src-tauri/target/release/bundle/
├── deb/              # Linux: .deb パッケージ
│   └── my-app_0.1.0_amd64.deb
├── appimage/         # Linux: AppImage
│   └── my-app_0.1.0_amd64.AppImage
├── rpm/              # Linux: RPM パッケージ（設定時）
├── dmg/              # macOS: ディスクイメージ
│   └── my-app_0.1.0_x64.dmg
├── macos/            # macOS: .app バンドル
│   └── my-app.app
├── nsis/             # Windows: NSIS インストーラー
│   └── my-app_0.1.0_x64-setup.exe
└── msi/              # Windows: MSI パッケージ
    └── my-app_0.1.0_x64_en-US.msi
```

## Cargo.lock のコミット（重要）

```bash
# Cargo.lock は必ずコミットすること
git add src-tauri/Cargo.lock
git commit -m "chore: add Cargo.lock"
```

**理由**: `Cargo.lock` がないと依存関係のバージョンが変わり、ビルドが再現できなくなる。アプリケーションは常に `Cargo.lock` をコミットすべき。

## ビルドターゲット設定

`tauri.conf.json` でビルドするインストーラー形式を指定:

全プラットフォーム対応の例:

```json
{
  "bundle": {
    "active": true,
    "targets": "all"
  }
}
```

Linux のみの例:

```json
{
  "bundle": {
    "active": true,
    "targets": ["deb", "appimage"]
  }
}
```

macOS のみの例:

```json
{
  "bundle": {
    "active": true,
    "targets": ["dmg"]
  }
}
```

Windows のみの例:

```json
{
  "bundle": {
    "active": true,
    "targets": ["nsis", "msi"]
  }
}
```

利用可能なターゲット:
- `"all"` - プラットフォームのデフォルト全て
- `"deb"` - Linux Debian パッケージ
- `"appimage"` - Linux AppImage
- `"rpm"` - Linux RPM（要追加設定）
- `"dmg"` - macOS ディスクイメージ
- `"app"` - macOS .app バンドル
- `"nsis"` - Windows NSIS インストーラー
- `"msi"` - Windows MSI パッケージ

## バージョン管理

### `tauri.conf.json` のバージョン

```json
{
  "version": "1.2.3"
}
```

### package.json と同期する場合

`version` フィールドに `"version": "package.json"` と指定すると `package.json` のバージョンを参照する（Tauri v2 では `tauri.conf.json` が正）。

## コード署名

### macOS

```bash
# 環境変数で署名情報を設定
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
export APPLE_CERTIFICATE_PASSWORD="cert-password"
export APPLE_ID="your@apple.com"
export APPLE_TEAM_ID="ABCDE12345"
export APPLE_PASSWORD="app-specific-password"  # App Store Connect で生成

cargo tauri build
```

`tauri.conf.json`:
```json
{
  "bundle": {
    "macOS": {
      "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
      "providerShortName": "ABCDE12345",
      "entitlements": "entitlements.plist"
    }
  }
}
```

### Windows

```bash
# PFX 証明書による署名
export TAURI_SIGNING_PRIVATE_KEY="path/to/cert.pfx"
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="cert-password"

cargo tauri build
```

`tauri.conf.json`:
```json
{
  "bundle": {
    "windows": {
      "certificateThumbprint": "certificate-thumbprint",
      "digestAlgorithm": "sha256",
      "timestampUrl": "http://timestamp.comodoca.com"
    }
  }
}
```

## クロスコンパイル

Tauri のクロスコンパイルはネイティブでは限定的。GitHub Actions を使うことを推奨。

### GitHub Actions（推奨）

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    permissions:
      contents: write
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: 'macos-latest'
            args: '--target aarch64-apple-darwin'
          - platform: 'macos-latest'
            args: '--target x86_64-apple-darwin'
          - platform: 'ubuntu-22.04'
            args: ''
          - platform: 'windows-latest'
            args: ''

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: lts/*

      - name: Install Rust
        uses: dtolnay/rust-toolchain@1.75.0
        with:
          targets: ${{ matrix.platform == 'macos-latest' && 'aarch64-apple-darwin,x86_64-apple-darwin' || '' }}

      - name: Install Linux dependencies
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Install npm dependencies
        run: npm ci

      - name: Build
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'App v__VERSION__'
          releaseBody: 'See the assets to download this version and install.'
          releaseDraft: true
          prerelease: false
          args: ${{ matrix.args }}
```

## 自動アップデーター（updater プラグイン）

### 署名キーの生成

```bash
npm run tauri signer generate -- -w ~/.tauri/myapp.key
```

### アップデートサーバーの設定

`tauri.conf.json`:
```json
{
  "plugins": {
    "updater": {
      "endpoints": ["https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"],
      "dialog": true,
      "pubkey": "YOUR_PUBLIC_KEY_HERE"
    }
  }
}
```

### アップデートサーバーレスポンス形式

```json
{
  "version": "1.1.0",
  "notes": "Bug fixes and improvements",
  "pub_date": "2024-01-15T00:00:00Z",
  "platforms": {
    "linux-x86_64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v1.1.0/app_1.1.0_amd64.AppImage"
    },
    "darwin-x86_64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v1.1.0/app_1.1.0_x64.dmg"
    },
    "darwin-aarch64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v1.1.0/app_1.1.0_aarch64.dmg"
    },
    "windows-x86_64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v1.1.0/app_1.1.0_x64-setup.exe"
    }
  }
}
```

## Linux の依存関係（ビルド環境）

```bash
# Ubuntu/Debian
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev \
  libappindicator3-dev \
  librsvg2-dev \
  patchelf \
  libssl-dev \
  libgtk-3-dev

# Fedora/RHEL
sudo dnf install -y \
  webkit2gtk4.1-devel \
  openssl-devel \
  gtk3-devel \
  librsvg2-devel
```

## ビルド最適化

### リリースビルドのサイズ削減

`src-tauri/Cargo.toml`:
```toml
[profile.release]
panic = "abort"
codegen-units = 1
lto = true
opt-level = "s"   # サイズ優先（"z" でさらに小さく）
strip = true      # デバッグシンボル除去
```

### UPX による圧縮（Linux/Windows）

```bash
# UPX インストール後
upx --best src-tauri/target/release/my-app
```

`tauri.conf.json`:
```json
{
  "bundle": {
    "linux": {
      "deb": {
        "depends": ["libwebkit2gtk-4.1-0"]
      }
    }
  }
}
```
