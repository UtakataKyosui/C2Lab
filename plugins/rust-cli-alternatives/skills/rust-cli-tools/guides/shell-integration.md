# Shell Integration Guide

## 推奨 .zshrc / .bashrc 設定

以下のスニペットを `~/.zshrc`（または `~/.bashrc`）に追加する。

### 基本エイリアス

```bash
# eza（ls の代替）
if command -v eza &>/dev/null; then
  alias ls='eza --icons --git'
  alias ll='eza -la --icons --git'
  alias lt='eza --tree --icons --level=2'
  alias la='eza -la --icons --git --group-directories-first'
fi

# bat（cat の代替）
if command -v bat &>/dev/null; then
  alias cat='bat --paging=never'      # ページャーなしで cat に近い動作
  alias less='bat --paging=always'    # ページャーあり
fi

# fd（find の代替）
# 注意: find を fd で上書きすると、オプションの違いで既存スクリプトが壊れることがある
# 代わりにそのまま fd コマンドを使用するか、別名（例: fdfind）を設定する

# ripgrep（grep の代替）
# 注意: grep を rg で上書きすると、オプションの違いで既存スクリプトが壊れることがある
# 代わりにそのまま rg コマンドを使用するか、別名（例: rggrep）を設定する

# dust（du の代替）
if command -v dust &>/dev/null; then
  alias du='dust'
fi

# procs（ps の代替）
if command -v procs &>/dev/null; then
  alias ps='procs'
fi

# bottom（top の代替）
if command -v btm &>/dev/null; then
  alias top='btm'
  alias htop='btm'
fi
```

### ツール初期化

```bash
# zoxide（cd の代替）
if command -v zoxide &>/dev/null; then
  eval "$(zoxide init zsh)"   # bash の場合は zsh → bash
fi

# atuin（シェル履歴の強化）
if command -v atuin &>/dev/null; then
  eval "$(atuin init zsh)"    # Ctrl+R を atuin に置き換え
fi

# starship（プロンプト）
if command -v starship &>/dev/null; then
  eval "$(starship init zsh)"
fi
```

### 環境変数

```bash
# bat のデフォルトテーマ
export BAT_THEME="TwoDark"

# bat を man ページのページャーとして使用
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export MANREDIR=bat

# ripgrep の設定ファイル
export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/ripgreprc"

# fzf との統合（ripgrep + bat）
export FZF_DEFAULT_COMMAND='rg --files --hidden --follow --glob "!.git"'
export FZF_DEFAULT_OPTS='--height 40% --reverse --preview "bat --color=always {}"'
```

### delta（git pager）の設定

`~/.gitconfig` に追加:
```ini
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true
    light = false
    side-by-side = true
    line-numbers = true
    syntax-theme = TwoDark

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
```

---

## 完全な .zshrc テンプレート

```bash
# ============================
# Rust CLI Tools Integration
# ============================

# Helper: check if command exists
_has() { command -v "$1" &>/dev/null; }

# --- eza (ls replacement) ---
if _has eza; then
  alias ls='eza --icons --git'
  alias ll='eza -la --icons --git'
  alias lt='eza --tree --icons --level=2'
  alias la='eza -la --icons --git --group-directories-first'
  alias tree='eza --tree --icons'
fi

# --- bat (cat replacement) ---
if _has bat; then
  alias cat='bat --paging=never'
  export MANPAGER="sh -c 'col -bx | bat -l man -p'"
  export BAT_THEME="TwoDark"
fi

# --- ripgrep ---
if _has rg; then
  export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/ripgreprc"
fi

# --- fd (find replacement) ---
# fd is already fast enough; no alias needed to avoid breaking scripts

# --- dust (du replacement) ---
if _has dust; then
  alias du='dust'
fi

# --- zoxide (smart cd) ---
if _has zoxide; then
  eval "$(zoxide init zsh)"
  # zi for interactive selection with fzf
fi

# --- atuin (shell history) ---
if _has atuin; then
  eval "$(atuin init zsh --disable-up-arrow)"
fi

# --- starship (prompt) ---
if _has starship; then
  eval "$(starship init zsh)"
fi

# --- fzf integration ---
if _has fzf && _has rg; then
  export FZF_DEFAULT_COMMAND='rg --files --hidden --follow --glob "!.git"'
fi
if _has fzf && _has bat; then
  export FZF_DEFAULT_OPTS='--height 40% --reverse --preview "bat --color=always --style=numbers {}"'
fi
```

---

## シェル補完の設定

多くのツールはシェル補完スクリプトを生成できる:

```bash
# eza
eza --generate-completion zsh > ~/.zsh/completions/_eza

# fd
fd --gen-completions zsh > ~/.zsh/completions/_fd

# ripgrep
rg --generate complete-zsh > ~/.zsh/completions/_rg

# just
just --completions zsh > ~/.zsh/completions/_just

# starship
starship completions zsh > ~/.zsh/completions/_starship

# ~/.zshrc に以下を追加（補完ディレクトリを読み込む）
fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit
```

---

## fish シェル設定

```fish
# ~/.config/fish/config.fish

# zoxide
zoxide init fish | source

# atuin
atuin init fish | source

# starship
starship init fish | source

# eza エイリアス
alias ls 'eza --icons --git'
alias ll 'eza -la --icons --git'
alias tree 'eza --tree --icons'

# bat
alias cat 'bat --paging=never'
set -x BAT_THEME "TwoDark"
set -x MANPAGER "sh -c 'col -bx | bat -l man -p'"
```
