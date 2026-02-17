# History Maintenance: Rewriting the Past

Jujutsu では、コミット（Change）はイミュータブル（不変）ではありません。
歴史は常に書き換え可能であり、整理整頓された状態を保つことができます。

## 変更の統合 (`jj squash`)

現在の変更を親Changeに統合します。
「修正コミット」を作らずに、元のコミットを修正したい場合に最適です。

```bash
# 親Changeに変更を統合
jj squash

# 特定の親（先祖）まで遡って統合することも可能（インタラクティブ）
jj squash -r <Target Revision>
```

## 変更の分割 (`jj split`)

1つのChangeに複数の変更が混ざっている場合、それを論理的に分割できます。

```bash
# 現在のChangeを分割（インタラクティブモードが起動）
jj split
```

これを行うと、元のChangeが2つ（以上）の親子関係にあるChangeに分割されます。

## 変更の破棄 (`jj abandon`)

不要になった実験的な実装や、誤って作成したChangeを削除します。

```bash
# 現在のChangeを破棄（親に戻る）
jj abandon

# 特定のChangeを破棄
jj abandon <Change ID>
```

※ 子供がいるChangeをAbandonすると、子供は親にRebaseされます（孤立しません）。

## 変更の移動 (`jj rebase`)

あるChangeの親を変更します（例: `main` が進んだので、自分の作業を最新の `main` の上に乗せ直す）。

```bash
# 現在のChange (@) を main の上に移動
jj rebase -d main

# 特定のブランチ(feat-x)を main の上に移動
jj rebase -s feat-x -d main
```

---

> [!TIP]
> **`jj rebase` vs `jj new`**
> *   `jj rebase`: 既存の作業履歴を別の親に付け替える（履歴改変）
> *   `jj new`: 新しい作業場所を作る（履歴追加）
