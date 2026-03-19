# Workspace Configuration

## ディレクトリ構造

Moonrepo ワークスペースは `.moon/` ディレクトリで管理します。

```
my-monorepo/
├── .moon/
│   ├── workspace.yml      # ワークスペース設定（必須）
│   ├── toolchain.yml      # ツールチェーン設定（proto 連携）
│   ├── tasks.yml          # ワークスペース共通タスク
│   └── tasks/             # 言語・タグ別タスク
│       ├── node.yml
│       └── rust.yml
├── .prototools            # proto バージョン定義
├── apps/
│   └── web/
│       ├── moon.yml
│       └── package.json
└── packages/
    └── ui/
        ├── moon.yml
        └── package.json
```

## 初期化

```bash
# 新規ワークスペースの初期化
moon init

# 既存モノレポに追加（package.json を検出して自動設定）
moon init --minimal
```

## .moon/workspace.yml

```yaml
$schema: 'https://moonrepo.dev/schemas/workspace.json'

# VCS 設定
vcs:
  manager: 'git'
  defaultBranch: 'main'
  remoteCandidates: ['origin', 'upstream']

# プロジェクト検出
projects:
  - 'apps/*'
  - 'packages/*'
  # 明示的に指定することも可能
  # web: 'apps/web'
  # ui: 'packages/ui'

# ファイルグループ（タスクの inputs/outputs で @group() 参照）
fileGroups:
  sources:
    - 'src/**/*.{ts,tsx}'
  tests:
    - 'tests/**/*.test.{ts,tsx}'
    - '**/__tests__/**/*'
  configs:
    - '*.config.*'
    - '.eslintrc.*'
    - 'tsconfig*.json'

# タスクランナー設定
runner:
  cacheLifetime: '7 days'
  inheritColorsForPipedTasks: true
  logRunningCommand: false
  archivableTargets:           # リモートキャッシュ対象タスク
    - ':build'
    - ':test'

# 制約（プロジェクト間の依存ルール）
constraints:
  enforceProjectTypeRelationships: true
```

## .moon/toolchain.yml

proto と連携してツールのバージョンを管理します。

```yaml
$schema: 'https://moonrepo.dev/schemas/toolchain.json'

# Node.js
node:
  version: '22'
  packageManager: 'pnpm'  # npm | pnpm | yarn | bun
  pnpm:
    version: '9'
  # yarn:
  #   version: '4'
  #   plugins: ['@yarnpkg/plugin-workspace-tools']
  addEnginesConstraint: true    # package.json engines に書き込む
  inferTasksFromScripts: true   # package.json scripts からタスクを自動生成

# TypeScript（型チェック連携）
typescript:
  version: '5.4'
  createMissingConfig: true     # tsconfig.json がなければ自動生成
  syncProjectReferences: true   # プロジェクト参照を自動同期
  routeOutDirToCache: true      # outDir を .moon/cache に向ける

# Rust
rust:
  edition: '2021'
  targets: ['wasm32-unknown-unknown']
  syncToolchainConfig: true

# Python
python:
  version: '3.12'
  packageManager: 'uv'
```

## リモートキャッシュ

```yaml
# .moon/workspace.yml
unstable_remote:
  host: 'grpcs://your-bazel-cache.example.com'  # Bazel Remote Execution API
  # または moonrepo.app のクラウドサービス
  auth:
    token: '$MOON_AUTH_TOKEN'
```

## CI/CD 統合

### GitHub Actions

```yaml
# .github/workflows/ci.yml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0         # --affected の比較に必要

      - uses: moonrepo/setup-toolchain@v0
        with:
          auto-install: true     # .moon/toolchain.yml のツールを自動インストール

      - run: moon ci             # 変更されたプロジェクトのタスクを実行
```

### 変更検出の仕組み

```bash
# デフォルト: HEAD と main の差分
moon ci

# ベースブランチを指定
moon ci --base origin/main

# 特定コミット範囲を指定
moon ci --base <sha1> --head <sha2>
```

## プロジェクト制約

```yaml
# .moon/workspace.yml
constraints:
  enforceProjectTypeRelationships: true
  # application は library にのみ依存可能
  # library は library にのみ依存可能
  # tool はどちらにも依存可能
```

## moon.yml のスキーマ継承

```yaml
# packages/ui/moon.yml
$schema: 'https://moonrepo.dev/schemas/project.json'

# workspace.yml の fileGroups を継承
# .moon/tasks.yml のタスクを自動継承

tasks:
  build:
    command: 'tsc'
    # workspace レベルのタスクを上書き可能
```

## よく使うコマンド

```bash
# ワークスペース情報の確認
moon info                      # ワークスペース全体の情報

# プロジェクト情報
moon project ui                # ui プロジェクトの詳細
moon project-graph             # プロジェクト依存グラフ

# タスク情報
moon task ui:build             # ui:build タスクの詳細

# 同期（設定の自動適用）
moon sync                      # tsconfig.json・package.json を自動同期
moon sync projects             # プロジェクト設定のみ同期

# キャッシュ管理
moon clean                     # 古いキャッシュを削除
```
