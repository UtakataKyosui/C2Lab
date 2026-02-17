# Colocation Patterns

## コアパターン

### 1. コンポーネント・コロケーション

最も基本的なパターン。UIコンポーネントとその関連ファイルをグループ化する。

```
src/components/Button/
├── index.ts              # バレルエクスポート
├── Button.tsx            # コンポーネント本体
├── Button.test.tsx       # テスト
├── Button.module.css     # スタイル
└── Button.types.ts       # 型定義
```

**原則**:
- `index.ts` は必須。外部からのインポートパスを短くする
- コンポーネント名とディレクトリ名は一致させる（PascalCase）
- 内部実装の詳細は `index.ts` で隠蔽する

### 2. フィーチャー・コロケーション

機能（feature）単位で関連ファイルを配置する。

```
src/features/authentication/
├── index.ts
├── components/
│   ├── LoginForm/
│   │   ├── index.ts
│   │   ├── LoginForm.tsx
│   │   ├── LoginForm.test.tsx
│   │   └── LoginForm.types.ts
│   └── SignupForm/
│       ├── index.ts
│       ├── SignupForm.tsx
│       └── SignupForm.types.ts
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts
├── utils/
│   ├── validators.ts
│   └── validators.test.ts
├── types/
│   └── auth.types.ts
└── constants/
    └── auth.constants.ts
```

**原則**:
- フィーチャーディレクトリのルートに `index.ts` を置き、公開APIを定義
- フィーチャー内のコンポーネントもコンポーネント・コロケーションに従う
- フィーチャー間の直接参照は避け、共有モジュール経由にする

### 3. ページ・コロケーション

ページ（ルート）ごとに関連ファイルを配置する。

```
src/pages/dashboard/
├── index.ts
├── DashboardPage.tsx
├── DashboardPage.test.tsx
├── components/
│   ├── DashboardHeader/
│   └── DashboardStats/
├── hooks/
│   └── useDashboardData.ts
└── utils/
    └── dashboard.utils.ts
```

## 拡張パターン

### ネストされたコロケーション

大きなコンポーネントの内部に、プライベートなサブコンポーネントを配置する。

```
src/components/DataTable/
├── index.ts
├── DataTable.tsx
├── DataTable.types.ts
├── components/                # プライベート・サブコンポーネント
│   ├── TableHeader/
│   │   ├── TableHeader.tsx
│   │   └── TableHeader.types.ts
│   ├── TableRow/
│   └── TablePagination/
└── hooks/
    └── useTableSort.ts
```

**ルール**:
- サブコンポーネントは親の `index.ts` からエクスポートしない
- サブコンポーネントは親コンポーネント内でのみ使用する
- 再利用が必要になったら、`src/components/` に昇格させる

### 共有モジュール

複数のフィーチャーで共有するコードを配置する。

```
src/shared/
├── components/        # 共有UIコンポーネント
├── hooks/             # 共有フック
├── utils/             # 共有ユーティリティ
├── types/             # 共有型定義
└── constants/         # 共有定数
```

## アンチパターン

### 1. ファイルタイプ別フォルダ（避けるべき）

```
# BAD: ファイルタイプでグループ化
src/
├── components/
│   ├── Button.tsx
│   └── Input.tsx
├── tests/
│   ├── Button.test.tsx    # Button.tsx と距離がある
│   └── Input.test.tsx
├── styles/
│   ├── Button.module.css  # さらに距離がある
│   └── Input.module.css
└── types/
    ├── Button.types.ts
    └── Input.types.ts
```

**問題点**: 関連ファイルが散在し、変更時に複数のディレクトリを行き来する必要がある。

### 2. バレルファイルの欠如

```
# BAD: index.ts がない
import { Button } from '../components/Button/Button';  # 冗長

# GOOD: index.ts あり
import { Button } from '../components/Button';  # クリーン
```

### 3. 深すぎるネスト

```
# BAD: 4階層以上
src/features/auth/components/forms/fields/inputs/TextInput/

# GOOD: 3階層以内
src/features/auth/components/TextInput/
```

**ガイドライン**: ネストは最大3階層まで。それ以上は構造を見直す。

### 4. 循環依存

```
# BAD: フィーチャー間の直接参照
src/features/auth/ → src/features/user/
src/features/user/ → src/features/auth/  # 循環!

# GOOD: 共有モジュール経由
src/features/auth/ → src/shared/types/
src/features/user/ → src/shared/types/
```

## バレルファイル（index.ts）のベストプラクティス

```typescript
// src/components/Button/index.ts

// 名前付きエクスポート（推奨）
export { Button } from './Button';
export type { ButtonProps, ButtonVariant } from './Button.types';

// デフォルトエクスポートの再エクスポート（必要な場合）
export { default } from './Button';
```

**注意事項**:
- バレルファイルから内部実装の詳細をエクスポートしない
- 型は `export type` を使ってエクスポートする（tree-shaking 対応）
- 巨大なバレルファイルはバンドルサイズに影響するため、必要最小限に
