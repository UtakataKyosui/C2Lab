---
name: パッケージセキュリティ（Takumi Guard）
description: This skill should be used when the user asks about "パッケージセキュリティ", "Takumi Guard", "npm プロキシ", "危険な npm パッケージをブロック", "supply chain attack", "サプライチェーン攻撃の対策", "マルウェアパッケージの防止", or wants to ensure only safe npm packages are installed. Also activates when user mentions "npm レジストリのプロキシ設定", "悪意あるパッケージの除外".
version: 0.1.0
---

# パッケージセキュリティ（Takumi Guard）

Takumi Guard は Flatt Security が開発した npm パッケージセキュリティプロキシ。悪意ある依存関係を持つパッケージや、セキュリティリスクのある npm パッケージをインストール前にブロックする。

## Takumi Guard の仕組み

1. npm/pnpm/yarn のプロキシとして動作
2. パッケージのインストール要求をインターセプト
3. Flatt Security のデータベースと照合
4. 危険なパッケージはブロック、安全なパッケージのみ通過

## セットアップ

### GitHub Actions での利用（推奨）

```yaml
# .github/workflows/ci.yml
steps:
  - uses: flatt-security/setup-takumi-guard-npm@v1
    with:
      token: ${{ secrets.TAKUMI_GUARD_TOKEN }}
  
  - name: Install dependencies
    run: pnpm install
```

### ローカルでの利用

```bash
# Takumi Guard をインストール
npm install -g @flatt-security/takumi-guard

# npm プロキシとして設定
takumi-guard start

# 別ターミナルで npm コマンドを実行（自動的にプロキシ経由になる）
npm install <package>
```

### 環境変数での設定

```bash
# プロキシを環境変数で設定
export TAKUMI_GUARD_TOKEN="your-token"
takumi-guard proxy &

# npm にプロキシを指定
npm config set proxy http://localhost:4873
npm config set https-proxy http://localhost:4873
```

## ブロックされた場合の対処

```
ERROR: Package 'malicious-package' was blocked by Takumi Guard
Reason: Contains suspicious code that may be malicious
```

ブロックされた場合:
1. パッケージ名のタイポを確認（typosquatting 攻撃の可能性）
2. Flatt Security のダッシュボードでブロック理由を確認
3. 代替パッケージを検討
4. 誤検知の場合は Flatt Security に報告

## ブロックリストの確認

```bash
# ブロックされたパッケージの一覧
takumi-guard list --blocked

# 特定パッケージのリスクレポート
takumi-guard check <package-name>
```

## CI/CD での統合

```yaml
# GitHub Actions での完全な設定例
name: Secure Install

on: [push, pull_request]

jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: flatt-security/setup-takumi-guard-npm@v1
        with:
          token: ${{ secrets.TAKUMI_GUARD_TOKEN }}
          # ブロック時に CI を失敗させる
          fail-on-block: true
      
      - run: pnpm install --frozen-lockfile
```

## よくある supply chain 攻撃パターン

Takumi Guard が防ぐ主な攻撃:

| 攻撃種別 | 説明 |
|---|---|
| Typosquatting | `lodash` → `1odash` のようなタイポを狙ったパッケージ |
| Dependency confusion | プライベートパッケージ名を npm に公開して差し替える |
| Malicious update | 既存の人気パッケージのメンテナーアカウントを乗っ取り |
| Postinstall scripts | `npm install` 時に悪意あるスクリプトを実行 |

## ローカル開発時の注意

Takumi Guard をローカルで使わない場合でも:

```bash
# postinstall スクリプトを無効化（慎重に）
npm install --ignore-scripts

# パッケージの内容を事前確認
npm pack <package>  # tarball を確認
npx npm-auditor <package>  # 内容をスキャン
```

## Takumi Guard と npm audit の違い

| 機能 | npm audit | Takumi Guard |
|---|---|---|
| 既知の CVE チェック | ✅ | ✅ |
| マルウェア検出 | ❌ | ✅ |
| Typosquatting 検出 | ❌ | ✅ |
| インストール前ブロック | ❌ | ✅ |
| Flatt 独自データベース | ❌ | ✅ |

## Additional Resources

- **`references/supply-chain-attacks.md`** - supply chain 攻撃の詳細と対策
