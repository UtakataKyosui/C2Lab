# dependency-cruiser ルール集

## 基本的なルールセット

### 禁止ルール（forbidden）

```json
{
  "forbidden": [
    {
      "name": "no-circular",
      "comment": "循環依存を禁止する",
      "severity": "error",
      "from": {},
      "to": {
        "circular": true
      }
    },
    {
      "name": "no-orphans",
      "comment": "孤立したファイルを警告する",
      "severity": "warn",
      "from": {
        "orphan": true,
        "pathNot": "\\.d\\.ts$"
      },
      "to": {}
    },
    {
      "name": "no-deprecated-core",
      "comment": "非推奨のNode.js組み込みモジュールを禁止",
      "severity": "warn",
      "from": {},
      "to": {
        "dependencyTypes": ["core"],
        "path": "^(punycode|domain)$"
      }
    },
    {
      "name": "no-reach-into-node_modules",
      "comment": "node_modules の内部パスへの直接参照を禁止",
      "severity": "error",
      "from": {},
      "to": {
        "path": "node_modules/.+/node_modules"
      }
    },
    {
      "name": "no-cross-package-imports",
      "comment": "packages/ 間の直接 import を禁止（公開 API 経由のみ許可）",
      "severity": "error",
      "from": {
        "path": "^packages/([^/]+)/"
      },
      "to": {
        "path": "^packages/(?!\\1)([^/]+)/src/"
      }
    }
  ]
}
```

### アーキテクチャ制約

```json
{
  "forbidden": [
    {
      "name": "ui-not-import-infra",
      "comment": "UI 層はインフラ層を直接 import しない",
      "severity": "error",
      "from": {
        "path": "^src/(components|pages|app)/"
      },
      "to": {
        "path": "^src/(db|cache|queue)/"
      }
    },
    {
      "name": "domain-not-import-external",
      "comment": "ドメイン層は外部パッケージに依存しない（純粋なビジネスロジック）",
      "severity": "warn",
      "from": {
        "path": "^src/domain/"
      },
      "to": {
        "dependencyTypes": ["npm"]
      }
    }
  ]
}
```

## 可視化

```bash
# SVG グラフ生成（Graphviz が必要）
depcruise --output-type dot src | dot -T svg > dependency-graph.svg

# 特定モジュールを起点にしたグラフ
depcruise --output-type dot --focus src/index.ts src | dot -T svg > focused.svg

# 循環依存のみ表示
depcruise --output-type dot --include-only "circular" src | dot -T svg > circular.svg

# アーカイブ形式（HTML）
depcruise --output-type archi src > architecture.html
```

## .dependency-cruiser.js（JavaScript 設定）

```javascript
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      from: {},
      to: { circular: true }
    }
  ],
  options: {
    doNotFollow: {
      path: 'node_modules',
      dependencyTypes: ['npm', 'npm-dev', 'npm-optional', 'npm-peer', 'npm-bundled', 'npm-no-pkg']
    },
    tsConfig: {
      fileName: './tsconfig.json'
    },
    reporterOptions: {
      dot: {
        theme: {
          graph: { rankdir: 'LR' },
          modules: [
            {
              criteria: { source: '^src/components' },
              attributes: { fillcolor: '#ddf5ff' }
            }
          ]
        }
      }
    }
  }
}
```

## CI 統合

```yaml
# .github/workflows/dep-check.yml
- name: Check dependencies
  run: |
    npx depcruise \
      --validate .dependency-cruiser.json \
      --output-type err \
      src
```
