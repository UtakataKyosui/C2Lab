---
name: rust-cli-tools
description: "Modern Rust-based CLI tools that replace or enhance classic Unix commands. Covers 30+ tools across file management (eza, fd, broot, zoxide), text processing (ripgrep, bat, sd), system monitoring (bottom, dust, procs), git (delta, gitui), development (hyperfine, just, tokei), networking (xh, miniserve), and shell (starship, atuin, nushell). Use when: (1) looking for a modern alternative to ls/find/grep/cat/sed/du/top/ps/curl/make (2) setting up a modern CLI/terminal environment (3) comparing or installing Rust CLI tools (4) configuring eza, bat, delta, starship, ripgrep, fd, or other tools (5) migrating shell scripts to use modern tools"
---

# Modern Rust CLI Tools

Rust製CLIツールはクラシックなUnixコマンドを速度・UX・機能の面で大幅に向上させる。クロスプラットフォーム対応・シングルバイナリ配布・.gitignore認識・カラー出力がデフォルトで有効。

## クイックリファレンス

| Classic Command | Rust Alternative | Key Advantage |
|----------------|------------------|---------------|
| `ls` | **eza** / **lsd** | Git status, icons, tree view built-in |
| `find` | **fd** | Intuitive syntax, .gitignore-aware, 5-10x faster |
| `grep` / `ag` | **ripgrep (rg)** | Fastest code search, PCRE2, Unicode |
| `cat` / `less` | **bat** | Syntax highlighting, Git diff integration |
| `sed` | **sd** | Simple regex syntax, no escaping hell |
| `tree` | **tre-command** / **broot** | Numbered entries, fuzzy search |
| `cd` + autojump | **zoxide** | Frecency-based, fzf integration |
| `du` | **dust** | Visual bar charts, sorted by size |
| `top` / `htop` | **bottom (btm)** | Customizable TUI widgets |
| `ps` | **procs** | Colors, tree view, port display |
| `diff` pager | **delta** | Syntax highlighting, side-by-side |
| `hexdump` | **hexyl** | Colorized with semantic highlighting |
| `time` | **hyperfine** | Statistical analysis, multiple runs |
| `make` | **just** | Simple syntax, no tab/space issues |
| `watch` / `entr` | **watchexec** | .gitignore-aware, signal handling |
| `curl` / httpie | **xh** | HTTPie syntax, HTTP/2 by default |
| `python -m http.server` | **miniserve** | Upload, auth, TLS, QR code |
| shell prompt | **starship** | Cross-shell, language detection |
| shell history | **atuin** | Encrypted sync, fuzzy search |
| `man` / `tldr` | **tealdeer** | Fast, offline, practical examples |
| `jq` | **jaq** | Faster, more correct jq-compatible |
| `tar` / `gzip` | **ouch** | Universal, auto-detect format |
| cloc / sloccount | **tokei** | 200+ languages, very fast |

## インストール方法（概要）

```bash
# cargo でインストール（最新版）
cargo install <package-name>

# Homebrew（macOS/Linux）
brew install <tool-name>

# cargo-binstall（プリビルドバイナリ、高速）
cargo install cargo-binstall
cargo binstall <package-name>
```

おすすめスターターパック:
```bash
brew install eza fd ripgrep bat delta bottom dust starship atuin zoxide
```

## カテゴリ別詳細ドキュメント

- **[file-management.md](./categories/file-management.md)** — eza, lsd, fd, broot, tre-command, zoxide
- **[text-processing.md](./categories/text-processing.md)** — ripgrep, bat, sd, grex, hexyl
- **[system-monitoring.md](./categories/system-monitoring.md)** — bottom, procs, dust, bandwhich
- **[git-tools.md](./categories/git-tools.md)** — delta, gitui
- **[dev-tools.md](./categories/dev-tools.md)** — tokei, hyperfine, just, watchexec
- **[networking.md](./categories/networking.md)** — xh, miniserve
- **[shell-prompt.md](./categories/shell-prompt.md)** — starship, nushell, tealdeer, atuin, yazi, jaq, ouch

## ガイド

- **[installation.md](./guides/installation.md)** — プラットフォーム別インストール、スターターパック
- **[shell-integration.md](./guides/shell-integration.md)** — エイリアス設定、シェル統合、`.zshrc`スニペット

## 移行チートシート

クラシックコマンドからの移行はこちら: **[migration-cheatsheet.md](./migration-cheatsheet.md)**
