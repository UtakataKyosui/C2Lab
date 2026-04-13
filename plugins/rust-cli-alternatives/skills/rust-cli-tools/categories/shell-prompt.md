# Shell & Prompt Tools

## starship — cross-shell prompt

**カスタムシェルプロンプトの代替。クロスシェル対応、言語バージョン自動検出、高速。**

```bash
# インストール
cargo install starship
brew install starship

# シェル統合（末尾に追加）
eval "$(starship init zsh)"    # ~/.zshrc
eval "$(starship init bash)"   # ~/.bashrc
starship init fish | source    # ~/.config/fish/config.fish
```

**設定ファイル**: `~/.config/starship.toml`
```toml
# プリセットを使う（starship preset <name> --output ~/.config/starship.toml）
# 利用可能: nerd-font-symbols, plain-text-symbols, no-runtime-versions 等

[character]
success_symbol = "[➜](bold green)"
error_symbol = "[➜](bold red)"

[git_branch]
symbol = " "
style = "bold purple"

[rust]
symbol = "🦀 "

[nodejs]
symbol = " "

[python]
symbol = " "
```

**プリセット一覧**:
```bash
starship preset --list             # 利用可能なプリセット一覧
starship preset nerd-font-symbols  # プリセット内容を確認
starship preset nerd-font-symbols --output ~/.config/starship.toml  # 適用
```

---

## nushell (nu) — modern shell

**bash/zsh/fish の代替。構造化データパイプライン、型システム。**

```bash
# インストール
cargo install nu
brew install nushell

# 起動
nu                             # nushell を起動
```

**Nushell の特徴**:
```nu
# すべての出力が構造化データ（テーブル）
ls | where size > 1kb | sort-by size -r

# パイプラインで SQL的な操作
ps | where cpu > 5 | select name cpu mem

# JSON/YAML/CSV を直接操作
open data.json | get users | where age > 18

# 型システム
def greet [name: string] { $"Hello, ($name)!" }

# 条件分岐
if ($env.HOME | path exists) { echo "home exists" }

# リスト操作
[1 2 3 4 5] | each { |it| $it * 2 } | math sum
```

**設定ファイル**: `~/.config/nushell/config.nu`

---

## tealdeer (tldr) — man page alternative

**man ページの代替。実用的なコマンド例に特化。**

```bash
# インストール
cargo install tealdeer          # コマンド名は tldr
brew install tealdeer

# 初回キャッシュ更新
tldr --update

# 基本使用
tldr tar                       # tar のチートシートを表示
tldr git commit                # git commit のチートシート
tldr -l                        # 利用可能なコマンド一覧
tldr -u                        # キャッシュを更新

# プラットフォーム指定
tldr --platform linux tar      # Linux 向け
tldr --platform osx brew       # macOS 向け

# 言語指定（利用可能な場合）
tldr --language ja tar         # 日本語ページ
```

---

## atuin — shell history replacement

**シェル履歴の代替。暗号化同期、ファジー検索、統計。**

```bash
# インストール
cargo install atuin
brew install atuin

# シェル統合（末尾に追加）
eval "$(atuin init zsh)"       # ~/.zshrc（Ctrl+R を atuin に置き換え）
eval "$(atuin init bash)"      # ~/.bashrc
atuin init fish | source       # ~/.config/fish/config.fish

# 基本使用（Ctrl+R で対話的検索）
atuin search cargo             # "cargo" を含む履歴を検索
atuin history list             # 全履歴を表示
atuin stats                    # 使用統計

# 同期（オプション）
atuin register                 # アカウント作成
atuin login                    # ログイン
atuin sync                     # 同期

# インポート
atuin import auto              # 既存の履歴を自動インポート
```

**設定ファイル**: `~/.config/atuin/config.toml`
```toml
auto_sync = true
sync_frequency = "10m"
search_mode = "fuzzy"
filter_mode = "global"     # global / host / session / directory
```

---

## yazi — terminal file manager

**ranger/nnn の代替。非同期 I/O、画像プレビュー、プラグインシステム。**

```bash
# インストール
cargo install yazi-fm          # コマンド名は yazi
brew install yazi

# 起動
yazi                           # カレントディレクトリで起動
yazi /path/to/dir              # 指定ディレクトリで起動

# 終了時にディレクトリを変更するシェル統合
function y() {
  local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
  yazi "$@" --cwd-file="$tmp"
  if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
    cd -- "$cwd"
  fi
  rm -f -- "$tmp"
}
```

**主なキーバインド**:
| キー | 動作 |
|------|------|
| `hjkl` / 矢印キー | ナビゲーション |
| `Enter` | ファイルを開く |
| `Space` | 選択/選択解除 |
| `y` | コピー |
| `x` | カット |
| `p` | ペースト |
| `d` | 削除（ゴミ箱） |
| `r` | リネーム |
| `/` | 検索 |
| `q` | 終了 |

---

## jaq — jq alternative

**jq の代替。高速、より正確な JSON 処理。jq 互換の構文。**

```bash
# インストール
cargo install jaq
brew install jaq

# 基本使用（jq と互換性あり）
echo '{"name":"Alice","age":30}' | jaq '.name'
cat data.json | jaq '.users[] | select(.age > 18)'
cat data.json | jaq '.items | length'
cat data.json | jaq '[.users[] | {name: .name, email: .email}]'

# ファイルから直接
jaq '.name' data.json
jaq -r '.name' data.json       # 文字列の引用符を除去 (raw output)
jaq -c '.[]' data.json         # コンパクト出力（改行なし）
jaq -n '[1,2,3] | add'        # 入力なし (-n)
```

---

## ouch — universal compression

**tar/gzip/zip 等の代替。フォーマット自動検出。**

```bash
# インストール
cargo install ouch
brew install ouch

# 圧縮（ファイル名から形式を自動判定）
ouch compress files/ archive.tar.gz
ouch compress *.rs code.zip
ouch compress data.json data.json.zst  # Zstandard 圧縮

# 展開（形式自動検出）
ouch decompress archive.tar.gz
ouch decompress file.zip -d /output    # 展開先指定

# 一覧表示
ouch list archive.tar.gz

# 対応形式: .tar, .tar.gz, .tar.bz2, .tar.xz, .tar.zst,
#           .zip, .gz, .bz2, .xz, .zst, .lz4, .sz, .7z, .rar
```
