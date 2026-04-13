# Git Tools

## delta — diff pager

**git diff / log / blame の出力をシンタックスハイライト付きで表示するページャー。**

```bash
# インストール
cargo install git-delta        # コマンド名は delta
brew install git-delta

# git と統合（~/.gitconfig に追加）
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true            # n/N でファイル間ナビゲーション
    light = false              # ダークターミナル向け
    side-by-side = true        # サイドバイサイド表示
    line-numbers = true        # 行番号表示

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
```

**コマンドライン直接使用**:
```bash
git diff | delta
git show HEAD | delta
delta file1.txt file2.txt      # 2ファイルの差分

# サイドバイサイド表示
git diff | delta --side-by-side

# テーマ一覧
delta --list-syntax-themes
delta --list-styles
```

**主なオプション**:
```bash
delta --theme="Dracula"        # テーマ指定
delta --syntax-theme="ansi"    # シンタックステーマ指定
delta --diff-so-fancy          # diff-so-fancy スタイルを模倣
delta --hyperlinks             # ファイルパスをハイパーリンク化
delta --word-diff-regex="\S+"  # 単語レベルの差分表示
```

**設定ファイル**: `~/.gitconfig` の `[delta]` セクション

---

## gitui — Git TUI

**キーボード駆動のGit TUI。ステージング、コミット、プッシュ、ログ、blame をターミナルから操作。**

```bash
# インストール
cargo install gitui
brew install gitui

# 起動
gitui                          # カレントリポジトリで起動
gitui -d /path/to/repo         # 指定リポジトリで起動
gitui log                      # ログ表示で起動
```

**主なキーバインド**:
| キー | 動作 |
|------|------|
| `Tab` / `Shift+Tab` | タブ切り替え（Status/Log/Files/Stash/Branch） |
| `Space` / `Enter` | ファイルをステージ/アンステージ |
| `c` | コミット |
| `P` | プッシュ |
| `f` | フェッチ |
| `p` | プル |
| `B` | ブランチ作成/切り替え |
| `t` | タグ作成 |
| `?` | キーバインド一覧 |
| `q` / `Esc` | 閉じる / 終了 |

**ハンクレベル操作**:
- diff ビューで `1`, `2`, `3` キーでハンク選択
- `Space` でハンク単位でステージ

**設定ファイル**: `~/.config/gitui/key_config.ron`（キーバインドカスタマイズ）

**lazygit との比較**:
| 特性 | gitui | lazygit |
|------|-------|---------|
| 言語 | Rust | Go |
| 大規模リポジトリ | 高速 | やや遅い |
| UI スタイル | シンプル | 高機能 |
| カスタマイズ | 限定的 | 豊富 |
