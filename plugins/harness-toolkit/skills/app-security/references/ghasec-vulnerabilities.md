# GitHub Actions の典型的な脆弱性パターン

## CRITICAL: pwn request（最も危険）

### pull_request_target でのコードチェックアウト

```yaml
# 危険な設定
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  build:
    steps:
      - uses: actions/checkout@v4  # ← PR のコードをチェックアウト（危険！）
      - run: npm ci && npm build   # ← 悪意あるコードが実行される
```

**問題**: `pull_request_target` は base ブランチのコンテキストで実行されるが、`actions/checkout` はデフォルトで PR のコードをチェックアウトするため、攻撃者がシークレットにアクセスできる。

**修正**:
```yaml
# 安全な設定（ビルドを分離する）
on:
  pull_request_target:

jobs:
  # シークレットが必要な処理（信頼できるコードのみ実行）
  trusted-job:
    steps:
      - uses: actions/checkout@v4  # base ブランチのコードのみ
        with:
          ref: ${{ github.base_ref }}  # PR のコードを使わない
```

### workflow_run での信頼されないコードの実行

```yaml
# 危険な設定
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_sha }}  # ← PR のコード
      - run: ./deploy.sh  # ← 危険
```

## HIGH: アクションバージョンの未固定

```yaml
# 危険（タグは書き換えられる可能性がある）
- uses: actions/checkout@v4
- uses: actions/setup-node@main

# 安全（SHA で固定）
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
- uses: actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af  # v4.1.0
```

**SHA の取得方法**:
```bash
# GitHub API でタグの SHA を取得
gh api repos/actions/checkout/git/ref/tags/v4 | jq -r '.object.sha'
```

## HIGH: GITHUB_TOKEN の過剰な権限

```yaml
# 危険（デフォルト全権限）
jobs:
  build:
    steps:
      - run: echo "building..."

# 安全（最小権限）
permissions:
  contents: read
  pull-requests: write  # PR コメントが必要な場合のみ

jobs:
  build:
    permissions:
      contents: read
    steps:
      - run: echo "building..."
```

## MEDIUM: 環境変数でのシークレット漏洩

```yaml
# 危険
- run: ./script.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}  # 環境変数経由で渡すと logs に出やすい

# 安全
- run: |
    echo "${{ secrets.API_KEY }}" | ./script.sh  # stdin 経由
  # または
- run: ./script.sh --api-key "$API_KEY"
  env:
    API_KEY: ${{ secrets.API_KEY }}  # スクリプト側でマスクする
```

## MEDIUM: 信頼されないデータの script インジェクション

```yaml
# 危険
- name: Comment PR
  run: |
    echo "PR title: ${{ github.event.pull_request.title }}"  # ← インジェクション可能
    # タイトルが "test"; rm -rf / だと危険

# 安全
- name: Comment PR
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}  # 環境変数経由
  run: |
    echo "PR title: $PR_TITLE"  # 環境変数として展開
```

## チェックリスト

- [ ] `pull_request_target` を使う場合、信頼されたコードのみを実行している
- [ ] 全アクションを SHA で固定している
- [ ] `permissions` ブロックで最小権限を設定している
- [ ] ユーザー入力（PR タイトル、ブランチ名等）を直接 `run:` に使っていない
- [ ] `GITHUB_TOKEN` のシークレットは必要最小限の権限で使用している
- [ ] `workflow_run` で PR のコードを実行していない

## ghasec の実行方法

```bash
# 全ワークフローをスキャン
ghasec .github/workflows/

# 特定ファイルのみ
ghasec .github/workflows/ci.yml

# 重要度でフィルタ（high 以上）
ghasec --severity high .github/workflows/

# JSON 出力
ghasec --format json . > ghasec-results.json
```
