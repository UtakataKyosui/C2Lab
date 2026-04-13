---
name: rust-cli-migration
description: "Quick migration cheatsheet from classic Unix commands to modern Rust CLI alternatives. Use when: (1) you know the classic command and want the Rust equivalent syntax (2) migrating shell scripts to use modern tools (3) need a quick side-by-side comparison — ls vs eza, find vs fd, grep vs rg, cat vs bat, sed vs sd, du vs dust, top vs btm, ps vs procs, curl vs xh, make vs just, hexdump vs hexyl, diff vs delta, time vs hyperfine, cloc vs tokei, watch vs watchexec"
---

# Rust CLI Migration Cheatsheet

クラシックUnixコマンドとRust代替ツールのコマンド対応表。

---

## ls → eza

```bash
ls                    →  eza
ls -la                →  eza -la
ls -la --color=auto   →  eza --icons --git           # アイコン + Git status
ls -R                 →  eza --tree                  # ツリー表示
tree -L 2             →  eza --tree --level=2
ls -lh                →  eza -lh                     # 人間可読サイズ
ls -lt                →  eza -la --sort=modified
```

**注意**: eza は .gitignore を認識。`--git-ignore` でgit除外ファイルを非表示。

---

## find → fd

```bash
find . -name "*.rs"           →  fd "\.rs$"          # または fd -e rs
find . -name "foo"            →  fd foo
find . -type f -name "*.txt"  →  fd -t f -e txt
find . -not -path "./.git/*"  →  fd --exclude .git   # .git を明示的に除外（fd はデフォルトで隠しディレクトリを除外）
find . -mtime -7              →  fd --changed-within 7d
find . -size +1M              →  fd --size +1M
find . -exec grep -l "foo" {} \;  →  rg -l "foo"     # ファイル検索にはrg使用
```

**注意**: fd は .gitignore・.fdignore を自動認識。隠しファイルは `-H`、無視ファイルは `-I` で表示。

---

## grep → ripgrep (rg)

```bash
grep -r "pattern" .              →  rg "pattern"
grep -rn "pattern" src/          →  rg -n "pattern" src/
grep -ri "pattern" .             →  rg -i "pattern"
grep -rl "pattern" .             →  rg -l "pattern"     # ファイル名のみ
grep -rL "pattern" .             →  rg --files-without-match "pattern"
grep -v "pattern"                →  rg -v "pattern"
grep -A 2 -B 2 "pattern"         →  rg -C 2 "pattern"
grep -E "foo|bar"                →  rg "foo|bar"         # デフォルトは Rust regex
grep -P "(?<=foo)bar"            →  rg -P "(?<=foo)bar"  # PCRE2 構文が必要な場合
grep --include="*.ts" -r "foo"   →  rg "foo" -g "*.ts"
```

**注意**: rg は .gitignore を自動認識、バイナリファイルを自動スキップ。`--no-ignore` で無効化。

---

## cat → bat

```bash
cat file.rs           →  bat file.rs           # シンタックスハイライト付き
cat -n file.rs        →  bat -n file.rs        # 行番号
cat file1 file2       →  bat file1 file2       # 複数ファイル連結
cat file | less       →  bat file              # bat は自動でページャー起動
```

**注意**: `bat` をマンページのページャーとして使う: `export MANPAGER="sh -c 'col -bx | bat -l man -p'"`

---

## sed → sd

```bash
sed 's/foo/bar/g' file        →  sd 'foo' 'bar' file
sed -i 's/foo/bar/g' file     →  sd 'foo' 'bar' file  # インプレース編集（デフォルト）
sed 's/foo/bar/' file         →  sd -n 1 'foo' 'bar' file  # 最初の1件のみ
# 正規表現
sed 's/[0-9]+/NUM/g' file     →  sd '\d+' 'NUM' file   # stdライクな正規表現
```

**注意**: sd はデフォルトでファイルを直接変更。プレビューは `--preview` / `-p` フラグ。

---

## du → dust

```bash
du -sh .              →  dust              # カレントディレクトリの使用量
du -sh *              →  dust -d 1         # 深さ1でサブディレクトリ一覧
du -sh /path          →  dust /path
du -ah --max-depth=2  →  dust -d 2 -f      # すべてのファイルを表示
du -s * | sort -rh    →  dust              # dust はデフォルトでサイズ順ソート
```

---

## top / htop → bottom (btm)

```bash
top                   →  btm              # インタラクティブTUI
htop                  →  btm              # カスタマイズ可能なウィジェット
```

**主なキーバインド**: `q` 終了、`?` ヘルプ、`/` 検索、`dd` プロセス終了  
**設定**: `~/.config/bottom/bottom.toml`

---

## ps → procs

```bash
ps aux                →  procs            # カラー付きプロセス一覧
ps aux | grep nginx   →  procs nginx      # キーワード検索
ps -ef --forest       →  procs --tree     # ツリー表示
```

**注意**: procs は TCP/UDPポート表示、Dockerコンテナ名表示をサポート。

---

## curl / httpie → xh

```bash
curl https://api.example.com/users           →  xh GET https://api.example.com/users
curl -X POST -H "Content-Type: application/json" -d '{"key":"val"}' URL
                                             →  xh POST URL key=val
curl -X DELETE URL                           →  xh DELETE URL
curl -H "Authorization: Bearer TOKEN" URL    →  xh URL Authorization:"Bearer TOKEN"
curl -o output.file URL                      →  xh --output output.file URL
curl -s URL | jq .                           →  xh URL                # JSON自動整形
```

---

## make → just

```bash
make build            →  just build
make test             →  just test
make clean install    →  just clean install
make VAR=value target →  just --set VAR value target
```

**justfile 記法**: `just --list` でレシピ一覧表示。

---

## watch / entr → watchexec

```bash
watch -n 2 'ls -la'                       →  watchexec -w . 'ls -la'
echo file | entr make                     →  watchexec -w file make
find . -name "*.rs" | entr cargo build    →  watchexec -e rs cargo build
```

---

## hexdump / xxd → hexyl

```bash
hexdump -C file.bin   →  hexyl file.bin   # カラー付き16進ダンプ
xxd file.bin          →  hexyl file.bin
```

---

## time → hyperfine

```bash
time ./myscript.sh            →  hyperfine './myscript.sh'
# 複数コマンドの比較
time cmd1 && time cmd2        →  hyperfine 'cmd1' 'cmd2'
# ウォームアップ付き
                              →  hyperfine --warmup 3 'cmd'
# 統計情報をMarkdownで出力
                              →  hyperfine --export-markdown results.md 'cmd1' 'cmd2'
```

---

## cloc / sloccount → tokei

```bash
cloc .                →  tokei
cloc src/             →  tokei src/
cloc --by-file src/   →  tokei --files src/
```

---

## tree → tre / broot

```bash
tree                  →  tre               # または broot
tree -L 2             →  tre -d 2          # 深さ指定
tree -I "node_modules"→  tre               # .gitignore を自動認識
```
