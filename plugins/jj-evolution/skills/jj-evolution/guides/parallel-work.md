# Parallel Workflows with Jujutsu

Jujutsu (jj) の最大の特徴は、**Working Copy (@) 自体が常にコミット可能（Amendable）なChangeである** という点です。
これにより、Gitの「ブランチを切る」という重い操作なしに、息をするように並行作業を行えます。

## 新しい作業の開始 (`jj new`)

現在の作業内容を確定し、その上に新しいChangeを作成します。

```bash
# 現在の変更(@)を親として、新しいChangeを作成
jj new

# 特定のRevision(mainなど)を親として、新しいChangeを作成
jj new main
```

### 活用例: 複数のアイデアを試す

1.  A案の実装を開始
    ```bash
    jj new main -m "feat: Idea A"
    # ... A案のコーディング ...
    ```
2.  B案も試したい（A案は保留）
    ```bash
    jj new main -m "feat: Idea B"
    # (@) が main の子である新しいChangeに移動します。A案は別のChangeとして残ります。
    # ... B案のコーディング ...
    ```

## 作業の切り替え (`jj edit`)

既存のChangeを編集（Working Copyにチェックアウト）するには `jj edit` を使用します。

```bash
# A案に戻る
jj edit <Change ID of A>

# B案に戻る
jj edit <Change ID of B>
```

### Tips: Change IDの確認

`jj log` でChange ID（ハッシュ）を確認できます。

```bash
jj log -r "all()"
```

## コンテキストスイッチの高速化

`jj` はWorking Copyの変更を自動的に記録しているため、`git stash` のような「退避」操作は不要です。
ただ `jj new` や `jj edit` で移動するだけで、前の状態は安全に保存されます。

---

> [!NOTE]
> `jj new` 直後のChangeは空ですが、ファイルを編集すると自動的にそのコンテンツが含まれます。
> Description（コミットメッセージ）は `jj describe` でいつでも変更可能です。
