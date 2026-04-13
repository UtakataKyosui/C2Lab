# Text Processing & Search Tools

## ripgrep (rg) — grep replacement

**grep の代替。最速のコード検索ツール、.gitignore 認識、PCRE2対応。**

```bash
# インストール
cargo install ripgrep        # コマンド名は rg
brew install ripgrep

# 基本使用
rg "pattern"                 # 現在ディレクトリ以下を検索
rg "pattern" src/            # src/ 以下を検索
rg -i "pattern"              # 大文字小文字を無視
rg -n "pattern"              # 行番号表示
rg -l "pattern"              # マッチするファイル名のみ
rg -c "pattern"              # マッチ数のみ
rg -v "pattern"              # マッチしない行
rg -w "word"                 # 単語境界マッチ
rg -C 3 "pattern"            # 前後3行のコンテキスト
rg -A 2 -B 1 "pattern"       # 後2行・前1行のコンテキスト

# フィルタリング
rg "pattern" -g "*.ts"       # TypeScriptファイルのみ
rg "pattern" -g "!*.test.ts" # テストファイルを除外
rg "pattern" --type rust     # Rustファイルのみ
rg "pattern" --type-not json # JSONを除外

# 高度な使い方
rg "pattern" --no-ignore     # .gitignore を無視
rg "pattern" -H              # 隠しファイルも含む
rg "foo" -r "bar"            # foo を bar に置換（出力のみ）
rg -U "foo\nbar"             # 複数行マッチ（-U: multiline）
rg --json "pattern"          # JSON出力（パイプ処理に便利）
```

**設定ファイル**: `~/.config/ripgrep/ripgreprc` または `RIPGREP_CONFIG_PATH` で指定
```
--smart-case
--follow
--glob=!.git
```

---

## bat — cat replacement

**cat の代替。シンタックスハイライト、Git diff、自動ページャー。**

```bash
# インストール
cargo install bat
brew install bat

# 基本使用
bat file.rs                  # シンタックスハイライト付きで表示
bat -n file.rs               # 行番号のみ（シンタックスハイライトなし）
bat -A file                  # 表示できない文字も表示
bat file1.rs file2.rs        # 複数ファイルを連結
bat *.md                     # グロブ展開
bat --plain file             # プレーンテキスト出力（パイプ処理用）

# 言語指定
bat --language rust file     # 言語を明示指定
bat -l json                  # JSON として表示

# テーマ
bat --list-themes            # 利用可能テーマ一覧
bat --theme="Dracula" file   # テーマを指定
```

**環境変数**:
```bash
export BAT_THEME="TwoDark"         # デフォルトテーマ
export BAT_STYLE="numbers,changes" # 表示スタイル
```

**便利な統合**:
```bash
# man ページのシンタックスハイライト
export MANPAGER="sh -c 'col -bx | bat -l man -p'"

# git diff のシンタックスハイライト（delta と組み合わせる場合は不要）
git diff | bat --language diff

# fzf でプレビュー
fzf --preview 'bat --color=always {}'
```

---

## sd — sed replacement

**sed の代替。直感的な正規表現構文、エスケープ地獄なし。**

```bash
# インストール
cargo install sd
brew install sd

# 基本使用（ファイルを直接変更）
sd 'foo' 'bar' file.txt          # foo → bar に置換
sd 'foo' 'bar' file1 file2       # 複数ファイル
sd '\bfoo\b' 'bar' file          # 単語境界マッチ

# パイプ処理
echo "hello world" | sd 'world' 'rust'   # 標準入力から

# 正規表現
sd 'v(\d+\.\d+)' 'v[$1]' file   # キャプチャグループ
sd '(?P<y>\d{4})-(?P<m>\d{2})' '$m/$y' file  # 名前付きキャプチャ

# プレビュー
sd --preview 'foo' 'bar' file    # 変更内容を表示（変更しない）

# フラグ
sd -f i 'foo' 'bar' file         # 大文字小文字を無視
```

**sed との比較**:
```bash
# sed（エスケープが必要）
sed 's/foo\/bar/baz\/qux/g' file

# sd（エスケープ不要）
sd 'foo/bar' 'baz/qux' file
```

---

## grex — regex generator

**テスト文字列からの正規表現自動生成。**

```bash
# インストール
cargo install grex
brew install grex

# 基本使用
grex "abc" "def" "ghi"           # 共通パターンを生成
grex "foo@example.com" "bar@test.org"  # メールアドレスパターン
grex "2024-01-15" "2023-12-01"   # 日付パターン

# オプション
grex --digits-only "abc123"      # 数字を \d に変換
grex --non-digits-only "abc123"  # 非数字を \D に変換
grex --spaces-only "a b c"       # スペースを \s に変換
grex --repetitions "aaa" "bb"    # 繰り返しを {n} / + / * に変換
grex --with-anchors "foo" "bar"  # ^ と $ を追加
grex --escape "foo.bar"          # メタ文字をエスケープ
```

---

## hexyl — hexdump replacement

**hexdump / xxd の代替。色分けで視認性抜群。**

```bash
# インストール
cargo install hexyl
brew install hexyl

# 基本使用
hexyl file.bin                   # 16進ダンプ
hexyl --length 256 file.bin      # 最初の256バイトのみ
hexyl --skip 128 file.bin        # 128バイト目からダンプ
hexyl --block-size 8 file.bin    # 1行あたり8バイト（デフォルト16）

# カラー表意:
# ■ NULL bytes (黒)
# ■ ASCII printable (緑)
# ■ ASCII whitespace (緑)
# ■ ASCII other (黄)
# ■ Non-ASCII (水色)
```
