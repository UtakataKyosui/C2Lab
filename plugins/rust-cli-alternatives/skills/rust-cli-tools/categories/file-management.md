# File Management & Navigation Tools

## eza — ls replacement

**ls の代替。Git integration, icons, tree view 内蔵。**

```bash
# インストール
cargo install eza
brew install eza

# 基本使用
eza                          # ls
eza -la                      # ls -la (long format + hidden files)
eza --icons --git            # アイコン + Git status 表示
eza --tree                   # ツリー表示
eza --tree --level=2         # 深さ2のツリー
eza -la --sort=modified      # 更新日時でソート
eza -la --sort=size          # サイズでソート
eza --git-ignore             # .gitignore のファイルを非表示
eza -la --group-directories-first  # ディレクトリを先頭に
```

**設定ファイル**: 設定ファイルなし。環境変数 `EZA_COLORS` でカラー設定。

**推奨エイリアス**:
```bash
alias ls='eza --icons --git'
alias ll='eza -la --icons --git'
alias lt='eza --tree --icons --level=2'
alias la='eza -la --icons --git --group-directories-first'
```

**注意**: `exa` は 2023年頃から unmaintained。`eza` が community-maintained fork。

---

## lsd — ls replacement (Nerd Font特化)

**ls の代替。Nerd Font のアイコンが特徴。**

```bash
# インストール
cargo install lsd
brew install lsd

# 基本使用
lsd                          # ls
lsd -la                      # ls -la
lsd --tree                   # ツリー表示
lsd --tree --depth 2         # 深さ2のツリー
lsd -la --sort time          # 更新日時でソート
lsd --blocks permission,user,size,date,name  # 表示カラム選択
```

**設定ファイル**: `~/.config/lsd/config.yaml`
```yaml
blocks:
  - permission
  - user
  - group
  - size
  - date
  - name
date: "+%Y-%m-%d %H:%M"
icons:
  when: auto
```

---

## fd — find replacement

**find の代替。直感的な構文、.gitignore 認識、高速。**

```bash
# インストール
cargo install fd-find        # コマンド名は fd
brew install fd

# 基本使用
fd foo                       # "foo" を含むファイル名を検索（現在ディレクトリ以下）
fd "\.rs$"                   # .rs で終わるファイル
fd -e rs                     # 拡張子 rs のファイル（fd -e rs と同等）
fd -t f foo                  # ファイルのみ (-t f)
fd -t d foo                  # ディレクトリのみ (-t d)
fd -H foo                    # 隠しファイルも含む
fd -I foo                    # .gitignore を無視
fd foo src/                  # src/ 以下を検索
fd -x cat                    # 結果に cat コマンドを実行
fd -e rs -x wc -l            # .rs ファイルの行数をカウント
fd --changed-within 7d       # 7日以内に変更されたファイル
```

**設定ファイル**: `~/.config/fd/ignore` (.gitignore 形式でグローバル除外パターン)

**便利なパターン**:
```bash
# 古いファイルを削除
fd --changed-before 30d -e log -x rm

# 見つかったファイルをエディタで開く
fd "config" --type f | fzf | xargs $EDITOR
```

---

## broot — tree / file navigator

**ディレクトリナビゲーター。ファジー検索、プレビュー、ファイル操作。**

```bash
# インストール
cargo install broot
brew install broot

# セットアップ（初回実行でシェル統合を設定）
broot --install

# 基本使用
broot                        # カレントディレクトリを開く
broot /path/to/dir           # 指定ディレクトリを開く
```

**broot 内の操作**:
- `/pattern` — ファジー検索
- `Enter` — ファイルを開く / ディレクトリに移動
- `:e` — エディタで開く
- `:cp`, `:mv`, `:rm` — ファイル操作
- `?` — ヘルプ

**設定ファイル**: `~/.config/broot/conf.hjson`

---

## tre-command — tree replacement

**tree の代替。ナンバリング付きエントリ、.gitignore 認識。**

```bash
# インストール
cargo install tre-command    # コマンド名は tre
brew install tre-command

# 基本使用
tre                          # カレントディレクトリのツリー
tre -d 2                     # 深さ2まで
tre -a                       # 隠しファイルも表示
tre -e rs,toml               # 指定拡張子のみ
```

**シェル統合**（番号でファイルを開く）:
```bash
# ~/.zshrc に追加
tre() { command tre "$@" -e && source /tmp/tre_aliases_$USER 2>/dev/null; }
```
→ `e1` で番号1のファイルをエディタで開ける。

---

## zoxide — cd with frecency

**cd の代替。よく使うディレクトリにすばやくジャンプ。**

```bash
# インストール
cargo install zoxide
brew install zoxide

# シェル統合（.zshrc に追加）
eval "$(zoxide init zsh)"    # zsh
eval "$(zoxide init bash)"   # bash
zoxide init fish | source    # fish

# 基本使用
z foo                        # "foo" を含む最も頻繁に使うディレクトリへ移動
z foo bar                    # "foo" と "bar" を含むディレクトリへ移動
zi                           # fzf で対話的に選択（fzf が必要）
z -                          # 直前のディレクトリへ戻る

# データベース操作
zoxide query foo             # マッチするパスを表示
zoxide add /path             # パスを手動追加
zoxide remove /path          # パスを削除
```

**設定**: `_ZO_DATA_DIR` でデータベース保存先を変更可能。
