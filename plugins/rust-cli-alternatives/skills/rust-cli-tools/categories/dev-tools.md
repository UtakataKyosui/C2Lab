# Development Tools

## tokei — line of code counter

**cloc / sloccount の代替。200+ 言語対応、非常に高速。**

```bash
# インストール
cargo install tokei
brew install tokei

# 基本使用
tokei                          # カレントディレクトリの統計
tokei src/                     # src/ 以下の統計
tokei --files                  # ファイル別の詳細
tokei -l Rust TypeScript       # 特定言語のみ
tokei --exclude target         # ディレクトリを除外

# 出力形式
tokei --output json            # JSON出力
tokei --output toml            # TOML出力
tokei --output yaml            # YAML出力

# 設定: .tokeignore ファイルで除外パターン（.gitignore形式）
```

**出力例**:
```
─────────────────────────────────────────────────────────
 Language            Files        Lines         Code     Comments       Blanks
─────────────────────────────────────────────────────────
 Rust                   42         4521         3891          198          432
 TypeScript             18         2103         1756          147          200
 JSON                    5          234          234            0            0
─────────────────────────────────────────────────────────
 Total                  65         6858         5881          345          632
```

---

## hyperfine — benchmarking

**time の代替。統計的ベンチマーク、複数コマンド比較、エクスポート機能。**

```bash
# インストール
cargo install hyperfine
brew install hyperfine

# 基本使用
hyperfine 'sleep 0.3'                     # 単一コマンドのベンチマーク
hyperfine 'fd -e rs' 'find . -name "*.rs"'  # コマンドを比較

# オプション
hyperfine --warmup 3 'cmd'               # ウォームアップ3回後にベンチマーク
hyperfine --runs 20 'cmd'               # 20回実行
hyperfine --min-runs 5 'cmd'            # 最低5回実行
hyperfine --prepare 'sync' 'cmd'        # 各実行前にコマンドを実行（キャッシュクリア等）
hyperfine --cleanup 'rm /tmp/output'    # 各実行後にクリーンアップ

# パラメータベンチマーク
hyperfine --parameter-scan n 1 10 'sleep {n}'
hyperfine --parameter-list lang rust,go,python './compile {lang}'

# 出力
hyperfine --export-markdown results.md 'cmd1' 'cmd2'
hyperfine --export-json results.json 'cmd'
hyperfine --export-csv results.csv 'cmd'

# シェル
hyperfine --shell=none 'cmd'             # シェルオーバーヘッドを除外
hyperfine --shell bash 'cmd'             # 指定シェルを使用
```

**統計情報**: mean, standard deviation, median, min, max を自動表示。

---

## just — make replacement

**make の代替。シンプルな構文、引数サポート、ドットエンブファイル読み込み。**

```bash
# インストール
cargo install just
brew install just

# 基本使用
just                           # デフォルトレシピを実行
just build                     # build レシピを実行
just test --release            # 引数付きで実行
just --list                    # レシピ一覧
just --dry-run build           # 実行内容を表示（実行しない）
```

**justfile の例**:
```make
# コメント
default: build test

# 変数
version := "1.0.0"
target := "debug"

# 基本レシピ
build:
    cargo build

# 引数付きレシピ
test filter="":
    cargo test {{filter}}

# 条件分岐
build-release:
    cargo build --release
    @echo "Built version {{version}}"

# 依存関係
deploy: build-release
    ./scripts/deploy.sh

# OS別実行
install:
    #!/usr/bin/env bash
    if command -v apt-get; then
        apt-get install myapp
    fi

# プライベートレシピ（just --list に表示されない）
_setup:
    pip install -r requirements.txt
```

**make との比較**:
- タブ不要（インデントは任意）
- 変数の構文が直感的（`:=` または `=`）
- 引数をレシピに渡せる
- `.env` ファイルを自動読み込み（`set dotenv-load`）

---

## watchexec — file watcher

**watch / entr の代替。.gitignore 認識、シグナルハンドリング、クロスプラットフォーム。**

```bash
# インストール
cargo install watchexec-cli    # コマンド名は watchexec
brew install watchexec

# 基本使用
watchexec cargo build          # ファイル変更時に cargo build を実行
watchexec -e rs cargo build    # .rs ファイルの変更時のみ
watchexec -w src/ cargo build  # src/ 以下を監視
watchexec --no-gitignore 'cmd' # .gitignore を無視

# ファイルフィルタ
watchexec -e rs,toml -- cargo test   # .rs または .toml の変更時
watchexec --ignore "*.log" -- cmd    # .log ファイルの変更を無視

# プロセス制御
watchexec --restart -- server        # 変更時にサーバーを再起動
watchexec --signal SIGTERM -- server # 指定シグナルを送信

# デバウンス
watchexec --debounce 500 -- cmd      # 500ms のデバウンス（デフォルト100ms）

# 環境変数
# WATCHEXEC_WRITTEN_PATH  — 変更されたファイルのパス
# WATCHEXEC_COMMON_PATH   — 共通のパスプレフィックス
watchexec -- bash -c 'echo "Changed: $WATCHEXEC_WRITTEN_PATH" && cargo build'
```
