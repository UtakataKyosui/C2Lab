# Installation Guide

## インストール方法

### cargo（Rust パッケージマネージャ）

```bash
# 最新版をソースからビルド
cargo install <package-name>

# locked（Cargo.lock を尊重）
cargo install --locked <package-name>
```

### cargo-binstall（プリビルドバイナリ、高速推奨）

```bash
# まず cargo-binstall をインストール
cargo install cargo-binstall

# 以降はプリビルドバイナリを自動取得（ソースビルド不要）
cargo binstall eza
cargo binstall fd-find
cargo binstall ripgrep
# ...
```

### Homebrew（macOS / Linux）

```bash
brew install <tool-name>
```

### システムパッケージマネージャ

```bash
# Ubuntu / Debian (apt)
apt-get install ripgrep fd-find bat

# Fedora / RHEL (dnf)
dnf install ripgrep fd-find bat

# Arch Linux (pacman)
pacman -S ripgrep fd bat eza bottom dust procs

# Windows (winget)
winget install BurntSushi.ripgrep.MSVC
winget install sharkdp.fd
winget install sharkdp.bat

# Windows (scoop)
scoop install ripgrep fd bat eza
```

---

## おすすめスターターパック

### 最小構成（すぐに使える7つ）

```bash
brew install eza fd ripgrep bat delta bottom dust
```

### 開発者向け完全構成

```bash
brew install \
  eza fd ripgrep bat sd \
  delta gitui \
  bottom dust procs \
  tokei hyperfine just watchexec \
  xh starship atuin zoxide \
  tealdeer
```

### カーゴ一括インストール

```bash
cargo install \
  eza fd-find ripgrep bat sd \
  git-delta gitui \
  bottom du-dust procs \
  tokei hyperfine just watchexec-cli \
  xh starship atuin zoxide \
  tealdeer
```

---

## ツール別パッケージ名対応表

| ツール | コマンド名 | cargo パッケージ名 | brew パッケージ名 |
|--------|------------|-------------------|------------------|
| eza | `eza` | `eza` | `eza` |
| lsd | `lsd` | `lsd` | `lsd` |
| fd | `fd` | `fd-find` | `fd` |
| broot | `broot` | `broot` | `broot` |
| tre-command | `tre` | `tre-command` | `tre-command` |
| zoxide | `zoxide` | `zoxide` | `zoxide` |
| ripgrep | `rg` | `ripgrep` | `ripgrep` |
| bat | `bat` | `bat` | `bat` |
| sd | `sd` | `sd` | `sd` |
| grex | `grex` | `grex` | `grex` |
| hexyl | `hexyl` | `hexyl` | `hexyl` |
| bottom | `btm` | `bottom` | `bottom` |
| procs | `procs` | `procs` | `procs` |
| dust | `dust` | `du-dust` | `dust` |
| bandwhich | `bandwhich` | `bandwhich` | `bandwhich` |
| delta | `delta` | `git-delta` | `git-delta` |
| gitui | `gitui` | `gitui` | `gitui` |
| tokei | `tokei` | `tokei` | `tokei` |
| hyperfine | `hyperfine` | `hyperfine` | `hyperfine` |
| just | `just` | `just` | `just` |
| watchexec | `watchexec` | `watchexec-cli` | `watchexec` |
| xh | `xh` | `xh` | `xh` |
| miniserve | `miniserve` | `miniserve` | `miniserve` |
| starship | `starship` | `starship` | `starship` |
| nushell | `nu` | `nu` | `nushell` |
| tealdeer | `tldr` | `tealdeer` | `tealdeer` |
| atuin | `atuin` | `atuin` | `atuin` |
| yazi | `yazi` | `yazi-fm` | `yazi` |
| jaq | `jaq` | `jaq` | `jaq` |
| ouch | `ouch` | `ouch` | `ouch` |
