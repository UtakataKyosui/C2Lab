# Supply Chain 攻撃の詳細と対策

## 主要な攻撃パターン

### 1. Typosquatting

人気パッケージに似た名前の悪意あるパッケージを公開する。

**例:**
- `lodash` → `lodahs`, `l0dash`, `1odash`
- `react` → `reacts`, `reaact`
- `express` → `expres`, `expressjs` (公式と異なる)

**対策:**
- パッケージ名をコピー&ペーストではなく、公式ドキュメントから参照する
- Takumi Guard でインストール前にチェック
- `npm pack <package>` で内容を事前確認

### 2. Dependency Confusion

プライベートパッケージと同名のパブリックパッケージを公開し、優先度を高くする。

**仕組み:**
1. 企業が内部パッケージ `@mycompany/utils` を使用
2. 攻撃者が同名のパッケージを npm に公開（バージョンを高くする）
3. npm がパブリックのより高いバージョンをダウンロード

**対策:**
- `@scope` 付きパッケージ名を使い、スコープを npm に登録する
- `.npmrc` でスコープを内部レジストリに向ける: `@mycompany:registry=https://registry.internal/`
- Takumi Guard で外部レジストリへのアクセスを制御

### 3. Malicious Maintainer Takeover

正規のパッケージメンテナーのアカウントを乗っ取り、悪意あるコードを注入する。

**事例:**
- `event-stream` (2018): バックドア入りバージョンがリリース
- `ua-parser-js` (2021): クリプトマイナー・バックドアを含むバージョン

**対策:**
- `package-lock.json` / `pnpm-lock.yaml` をコミットしてバージョンを固定
- `npm audit` / `pnpm audit` を CI で実行
- Renovate/Dependabot でアップデートの差分を確認
- Takumi Guard でリアルタイムチェック

### 4. Malicious postinstall Scripts

`package.json` の `scripts.postinstall` に悪意あるコードを仕込む。

**対策:**
```bash
# postinstall スクリプトを無効化（慎重に）
npm install --ignore-scripts

# スクリプトの内容を事前確認
npm pack <package>
tar -tzf <package>.tgz  # ファイル一覧確認
```

## npm audit の活用

```bash
# 脆弱性チェック
npm audit

# JSON 出力（CI 向け）
npm audit --json

# 修正可能な問題のみ表示
npm audit --audit-level moderate

# 自動修正（慎重に）
npm audit fix

# 破壊的変更も含めて修正（慎重に）
npm audit fix --force
```

## lockfile の重要性

```bash
# lockfile がコミットされているか確認（git 環境）
git ls-files package-lock.json pnpm-lock.yaml yarn.lock

# git が利用できない環境（jj 専用リポジトリ等）での代替:
test -f package-lock.json && echo "package-lock.json found"
test -f pnpm-lock.yaml    && echo "pnpm-lock.yaml found"
test -f yarn.lock          && echo "yarn.lock found"

# lockfile からインストール（package.json ではなく lockfile を使う）
npm ci               # npm
pnpm install --frozen-lockfile  # pnpm
yarn install --frozen-lockfile  # yarn
```

## SBOM (Software Bill of Materials)

```bash
# npm SBOM を生成（npm 7+）
npm sbom --sbom-format spdx --sbom-type lockfile > sbom.json

# CycloneDX 形式
npx @cyclonedx/cyclonedx-npm --output-file sbom.cyclonedx.json
```

## 参考リソース

- [OWASP Top 10 for Supply Chain](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [Flatt Security Blog: npm supply chain attacks](https://flatt.tech/)
- [GitHub: Dependabot alerts](https://docs.github.com/en/code-security/dependabot)
