# Conflict Resolution and Collaboration

Jujutsu (jj) はコンフリクトを「エラー」ではなく「状態」として扱います。
コンフリクトが発生しても作業を中断する必要はなく、都合の良いタイミングで解消できます。

## コンフリクトの解決 (`jj resolve`)

コンフリクトが発生したファイルは、標準的なコンフリクトマーカー（`<<<<<<<`, `=======`, `>>>>>>>`）が挿入された状態で保存されます。

### 外部ツールで解決

設定されたマージツール（VSCodeなど）を起動して解決します。

```bash
# 全てのコンフリクトを順番に解決
jj resolve

# 特定のファイルを解決
jj resolve <path>
```

### 手動で解決

エディタでファイルを開き、マーカーを修正した後、その状態を記録します。
Jujutsuでは、ファイルの内容が修正されれば自動的にコンフリクト解消とみなされます（`git add` は不要です）。

## Gitとの連携

JujutsuはGit互換のバックエンドを使用しているため、GitHubやGitLabとシームレスに連携できます。

### Push

現在のChangeをリモートにプッシュします。

```bash
# 特定のBookmarkをプッシュ（推奨：意図しないBookmarkのpushを防ぐ）
jj git push -b <bookmark-name>

# 全てのBookmarkをプッシュ（注意：意図しないBookmarkも含まれる場合がある）
jj git push --all
```

### Fetch

リモートの変更を取り込みます。

```bash
jj git fetch
```

### Pull (Rebase)

リモートの変更を取り込み、自分の作業（Change）をその上に移動（Rebase）します。
Jujutsuには `git pull` コマンドはありませんが、以下のように行うのが一般的です。

```bash
# 1. Fetch
jj git fetch

# 2. Rebase (自動的に行われる場合もありますが、手動で行う場合)
jj rebase -d main
```

> [!NOTE]
> `jj` は working copy が clean である必要はありません。
> 変更中のファイルがあっても安全に fetch や rebase が可能です。
