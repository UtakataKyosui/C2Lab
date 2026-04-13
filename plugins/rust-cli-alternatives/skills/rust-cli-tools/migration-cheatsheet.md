# Migration Cheatsheet: Classic → Rust CLI

詳細なコマンド対応表は [skills/rust-cli-migration/SKILL.md](../../rust-cli-migration/SKILL.md) を参照。

## 一覧（ツール名と置き換え対象）

| Classic | Rust Tool | Install (brew) |
|---------|-----------|----------------|
| `ls` | `eza` | `brew install eza` |
| `ls` | `lsd` | `brew install lsd` |
| `find` | `fd` | `brew install fd` |
| `tree` | `tre` | `brew install tre-command` |
| `tree`/nav | `broot` | `brew install broot` |
| `cd` | `z` (zoxide) | `brew install zoxide` |
| `grep` | `rg` | `brew install ripgrep` |
| `cat` | `bat` | `brew install bat` |
| `sed` | `sd` | `brew install sd` |
| `hexdump` | `hexyl` | `brew install hexyl` |
| `du` | `dust` | `brew install dust` |
| `top` | `btm` | `brew install bottom` |
| `ps` | `procs` | `brew install procs` |
| `iftop` | `bandwhich` | `brew install bandwhich` |
| git diff | `delta` | `brew install git-delta` |
| git TUI | `gitui` | `brew install gitui` |
| `cloc` | `tokei` | `brew install tokei` |
| `time` | `hyperfine` | `brew install hyperfine` |
| `make` | `just` | `brew install just` |
| `watch` | `watchexec` | `brew install watchexec` |
| `curl` | `xh` | `brew install xh` |
| `http.server` | `miniserve` | `brew install miniserve` |
| prompt | `starship` | `brew install starship` |
| `history` | `atuin` | `brew install atuin` |
| `man` | `tldr` | `brew install tealdeer` |
| ranger | `yazi` | `brew install yazi` |
| `jq` | `jaq` | `brew install jaq` |
| tar/zip | `ouch` | `brew install ouch` |
