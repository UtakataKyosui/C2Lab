# obs-plugin-dev

OBS Studio プラグイン（C/C++ / Rust）の開発を支援する Claude Code プラグイン。

## 機能

### Skills

| スキル | 説明 | トリガー例 |
|--------|------|-----------|
| `obs-plugin-guide` | OBS プラグイン開発ガイド（構造・API・CMake・Rust FFI） | "OBSプラグインを作りたい" |
| `obs-testing-guide` | テスト・デバッグガイド（cargo test・GDB・Valgrind・ASan） | "OBSプラグインのテスト方法は？" |

### Agent

| エージェント | 説明 |
|-------------|------|
| `obs-plugin-validator` | プラグインコードを静的解析し、必須API・メモリ管理の問題をレポート |

### Hooks

CMakeLists.txt・C/C++ ソース・Rust ソースの Write/Edit 時に自動でバリデーションを実施:

- **CMakeLists.txt**: `find_package(libobs)` と `MODULE` ライブラリタイプを確認
- **C/C++ ソース**: `obs_module_load`/`unload` のペア、`bzalloc`/`bfree` のペアを確認
- **Rust ソース**: `#[no_mangle]` エントリポイント、`Box::into_raw`/`from_raw` のペアを確認

## サポート範囲

- ソースプラグイン（映像・音声入力）
- フィルタープラグイン（エフェクト処理）
- 出力プラグイン（配信・録画先）
- エンコーダープラグイン
- C/C++ および Rust での実装

## インストール

### マーケットプレイスからのインストール

Claude Code のプラグイン設定画面からマーケットプレイスを開き、`obs-plugin-dev` を検索してインストールします。

```bash
# または CLI 経由でインストール（Claude Code マーケットプレイス統合時）
# プラグインマネージャーで以下の URL を登録:
# https://github.com/UtakataKyosui/C2Lab/tree/main/plugins/obs-plugin-dev
```

インストール後、以下が利用可能になります：
- **Skills**: `obs-plugin-guide`, `obs-testing-guide`
- **Agent**: `obs-plugin-validator`
- **Hooks**: CMakeLists.txt / C/C++ / Rust ソースの自動バリデーション

## 参考資料

- [OBS Studio Plugin Development](https://obsproject.com/docs/plugins.html)
- [obs-plugintemplate](https://github.com/obsproject/obs-plugintemplate)
- [OBS Studio Source](https://github.com/obsproject/obs-studio)
