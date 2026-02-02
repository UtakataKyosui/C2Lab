# JJ 開発ワークフロー

実際の開発シナリオにおけるJJの使い方を詳細に解説します。

## 新規機能開発

### フェーズ1: 準備

```bash
# 1. リモートの最新状態を取得
jj git fetch

# 2. 現在の状態を確認
jj log

# 3. main（またはdevelop）から新しいチェンジを作成
jj new main@origin

# 4. 作業内容を記述（WIPでも書いておく）
jj describe -m "feat: ユーザー認証機能の実装

- ログイン/ログアウト機能
- セッション管理
- パスワードリセット"
```

### フェーズ2: 開発

```bash
# 開発を進める（自動的にスナップショットされる）
# ... コードを書く ...

# 進捗を確認
jj status
jj diff

# 必要に応じて説明を更新
jj describe -m "feat: ユーザー認証機能の実装

- [x] ログイン/ログアウト機能
- [ ] セッション管理
- [ ] パスワードリセット"
```

#### 開発中に別の作業が必要になった場合

```bash
# 現在の作業を確認（チェンジIDをメモ）
jj log -r @

# 別の作業を開始（現在の作業は自動保存）
jj new main@origin
jj describe -m "別の緊急作業"
# ... 作業 ...

# 元の作業に戻る
jj edit <元のチェンジID>
```

#### 開発を複数のチェンジに分割

```bash
# 大きな機能を段階的に開発

# チェンジ1: データモデル
jj new main@origin
jj describe -m "feat: User モデルを追加"
# ... 作業 ...

# チェンジ2: チェンジ1の上にAPI層を追加
jj new
jj describe -m "feat: 認証APIエンドポイントを追加"
# ... 作業 ...

# チェンジ3: チェンジ2の上にUI層を追加
jj new
jj describe -m "feat: ログイン画面を追加"
# ... 作業 ...
```

### フェーズ3: レビュー準備

```bash
# 1. 作業内容を確認
jj log
jj diff -r <最初のチェンジ>::@  # 全チェンジの差分

# 2. ブックマークを作成
jj bookmark create feature/user-auth -r @

# 3. リモートにプッシュ
jj git push -b feature/user-auth

# 4. プルリクエストを作成（GitHub CLI等で）
gh pr create --title "feat: ユーザー認証機能" --body "..."
```

### フェーズ4: レビュー対応

```bash
# 1. レビュー指摘を受けたチェンジを編集
jj log  # 該当チェンジを確認
jj edit <該当チェンジID>

# 2. 修正を加える
# ... 修正 ...

# 3. 確認（子孫チェンジは自動的にリベースされる）
jj log
jj status

# 4. 再プッシュ（force pushが自動的に行われる）
jj git push -b feature/user-auth
```

#### 複数のチェンジにまたがる修正

```bash
# チェンジ1を修正
jj edit <チェンジ1のID>
# ... 修正 ...

# チェンジ2を修正（チェンジ1の修正は自動的に反映）
jj edit <チェンジ2のID>
# ... 修正 ...

# 最新のチェンジに戻る
jj new  # または jj edit <最新のチェンジID>
```

### フェーズ5: マージ

```bash
# プルリクエストがマージされたら

# 1. リモートの状態を取得
jj git fetch

# 2. ローカルのブックマークを更新
jj bookmark delete feature/user-auth  # ローカルブックマークを削除

# 3. 次の作業へ
jj new main@origin
```

---

## 不具合修正

### 通常の不具合修正

```bash
# 1. 最新を取得
jj git fetch

# 2. mainから新しいチェンジを作成
jj new main@origin

# 3. 不具合の説明と修正内容を記述
jj describe -m "fix: ログイン時にセッションが保存されない問題を修正

原因: セッションの有効期限が0に設定されていた
対策: デフォルト値を24時間に変更

Fixes #123"

# 4. 修正を実装
# ... 修正 ...

# 5. テストを実行
# ... テスト ...

# 6. ブックマーク作成とプッシュ
jj bookmark create fix/session-not-saved
jj git push -b fix/session-not-saved
```

### 緊急修正（Hotfix）

```bash
# 1. 本番ブランチ（main/production）から直接修正
jj git fetch
jj new main@origin

# 2. 緊急修正を実装
jj describe -m "hotfix: 本番環境でのクラッシュを修正

Critical: ユーザーがログインできない状態
原因: NullPointerException in AuthService
対策: null チェックを追加"

# ... 修正 ...

# 3. 即座にプッシュ
jj bookmark create hotfix/auth-crash
jj git push -b hotfix/auth-crash

# 4. プルリクエスト作成（緊急レビュー）
gh pr create --title "HOTFIX: 本番クラッシュ修正" --label "urgent"
```

### 過去のバージョンの不具合修正

```bash
# 1. 特定のリリースタグから修正
jj git fetch
jj new v1.2.0  # リリースタグから開始

# 2. 修正を実装
jj describe -m "fix: v1.2.x向けセキュリティ修正"
# ... 修正 ...

# 3. バックポート用ブックマーク
jj bookmark create fix/security-v1.2
jj git push -b fix/security-v1.2
```

---

## チーム開発のプラクティス

### 他の人の変更を取り込む

```bash
# 1. リモートの変更を取得
jj git fetch

# 2. 現在の作業を最新のmainにリベース
jj rebase -d main@origin

# コンフリクトがある場合
jj status  # コンフリクトを確認
# ... ファイルを編集してコンフリクト解決 ...
jj status  # 解決を確認
```

### 他の人のブランチをレビュー

```bash
# 1. リモートを取得
jj git fetch

# 2. レビュー対象のブックマークをチェックアウト
jj new feature/someone-else@origin

# 3. コードを確認
jj diff -r main@origin..@  # mainからの差分
jj log -r main@origin..@   # コミット履歴

# 4. ローカルで修正提案を試す
jj new
jj describe -m "suggestion: リファクタリング提案"
# ... 修正 ...
# これはプッシュせずローカルで確認するだけ

# 5. 元の作業に戻る
jj edit <元のチェンジ>
```

### チェンジの整理（プッシュ前）

```bash
# 複数のチェンジを1つにまとめる
jj squash --from <まとめたいチェンジ> --into <統合先>

# チェンジを分割
jj split -r <分割したいチェンジ>

# チェンジの順序を変更
jj rebase -r <移動したいチェンジ> -d <新しい親>

# 不要なチェンジを削除
jj abandon <不要なチェンジ>
```

---

## 高度なテクニック

### 複数の機能を並行開発

```bash
# 機能Aと機能Bを同時に開発

# 機能A
jj new main@origin
jj describe -m "feat: 機能A"
jj bookmark create feature/a

# 機能B（mainから独立）
jj new main@origin
jj describe -m "feat: 機能B"
jj bookmark create feature/b

# 切り替え
jj edit feature/a  # 機能Aの作業
jj edit feature/b  # 機能Bの作業

# 両方の状態を確認
jj log -r 'bookmarks()'
```

### 実験的な変更を試す

```bash
# 現在の状態を確認
jj log -r @

# 実験用チェンジを作成
jj new
jj describe -m "experiment: 新しいアルゴリズムを試す"

# ... 実験 ...

# 実験が成功したら、そのまま続行
# 実験が失敗したら
jj abandon  # 実験チェンジを破棄
# または
jj undo  # 直前の状態に戻る
```

### bisectで問題のチェンジを特定

```bash
# 問題が発生したチェンジを二分探索で特定

# 1. 問題のある範囲を確認
jj log -r 'v1.0.0::main@origin'

# 2. 中間点をチェック
jj new <中間のチェンジ>
# ... テスト ...

# 3. 問題があれば前半を、なければ後半を調査
# 繰り返して問題のチェンジを特定
```

### 依存関係のあるプルリクエスト（スタックPR）

```bash
# PR1: 基盤となる変更
jj new main@origin
jj describe -m "refactor: 認証基盤のリファクタリング"
jj bookmark create stack/1-auth-refactor
# ... 作業 ...

# PR2: PR1に依存する変更
jj new  # PR1の上に作成
jj describe -m "feat: OAuth2対応"
jj bookmark create stack/2-oauth

# PR3: PR2に依存する変更
jj new
jj describe -m "feat: Google認証"
jj bookmark create stack/3-google-auth

# 各PRを個別にプッシュ
jj git push -b stack/1-auth-refactor
jj git push -b stack/2-oauth
jj git push -b stack/3-google-auth

# PR1が修正された場合、PR2, PR3は自動的にリベースされる
jj edit stack/1-auth-refactor
# ... 修正 ...
# PR2, PR3は自動更新

# 再プッシュ
jj git push -b stack/1-auth-refactor
jj git push -b stack/2-oauth
jj git push -b stack/3-google-auth
```

---

## コミットメッセージの規約

JJでも一般的なコミットメッセージ規約を使用することを推奨します：

```
<type>: <subject>

<body>

<footer>
```

### Type

| Type | 説明 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | コードの意味に影響しない変更（空白、フォーマット等） |
| `refactor` | バグ修正でも機能追加でもないコード変更 |
| `perf` | パフォーマンス改善 |
| `test` | テストの追加・修正 |
| `chore` | ビルドプロセスやツールの変更 |
| `hotfix` | 緊急修正 |

### 例

```bash
jj describe -m "feat: ユーザープロフィール画像のアップロード機能を追加

- 画像サイズは最大5MBまで
- 対応フォーマット: JPG, PNG, GIF
- 自動リサイズ機能付き

Closes #456"
```

---

## チェックリスト

### プッシュ前の確認

- [ ] `jj status` でコンフリクトがないか確認
- [ ] `jj diff` で意図しない変更が含まれていないか確認
- [ ] `jj log` でチェンジの説明が適切か確認
- [ ] テストが通るか確認
- [ ] ブックマーク名が規約に従っているか確認

### レビュー後の確認

- [ ] すべての指摘に対応したか確認
- [ ] 子孫チェンジに問題が発生していないか確認
- [ ] 再度テストが通るか確認
