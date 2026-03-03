---
name: typescript-react-standards
description: TypeScript・React コーディング標準。型定義・コンポーネント設計・DRY・null 安全性・フォーム・セキュリティ・アクセシビリティ・Figma 準拠ルールを提供する。TypeScript/React コードを書くときや設計方針に迷ったときに参照する。
globs:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript・React コーディング標準

## 型定義

- コンポーネント固有の型をローカルで再定義しない。API クライアントの型から導出する（例: `TenantListItem['status']`）
- 型キャストのボイラープレートが複数箇所に現れる場合は、共通ラッパーに切り出す
- hooks の引数がコール元で `null` になりうる場合、`string | null` を受け入れて `enabled` でガードする。呼び出し側に `?? ''` 等の変換を強いない

## コンポーネント設計

- `'use client'` ディレクティブは hooks やブラウザ API を使用するコンポーネントにのみ付与する
- `asChild` を使用する場合、Button の `onClick` は子要素に伝播しない。Link に直接配置するか、Button を使わずに Link をスタイリングする
- 同じ機能の既存コンポーネントがある場合は設定を統一する（例: `shallow: true` を同種の hooks で統一）
- 共通コンポーネント（Pagination 等）を変更する場合は影響範囲を考慮し、既存の実装を活用する
- コールバック props は、全ての呼び出し元が必ず渡す場合は必須（`onX: () => void`）にする。オプショナル（`onX?`）は本当に省略されるケースがあるときだけ使う
- Server → Client 境界で非シリアライズ可能な props（関数、コンポーネント参照）を渡さない。variant props や文字列キーで Client Component 内部からマッピングする
- `useMemo` の依存配列が空で同期的な派生値を計算している場合は不要。レンダリング時に直接計算する
- ユーティリティ関数を無関係なモジュールから import しない。`utils/` に切り出して共有する
- Radix Dialog のモーダルでは `open` state をデータ取得用の ID state から分離する。ID で `open` を導出すると、閉じアニメーション中にデータが消えてチラつく
- 同一画面に詳細モーダルと編集モーダルがある場合、タイトルで区別する（例: 「テナント詳細」「テナント編集」）

## URL パラメータ

- URL のパースには文字列操作ではなく `new URL()` を使用する
- nuqs の `useQueryStates` で検索パラメータを管理する場合、`history: 'push'` は検索ごとにブラウザ履歴が増えるため、特別な理由がない限り使用しない

## DRY・共通化

- 同じフィールド群を複数の Zod スキーマで定義する場合、共通部分を `const` に切り出してスプレッドする
- 同じマッピングロジック（例: フォーム値 → API リクエストの変換）が複数関数に現れる場合はヘルパー関数に抽出する
- 特定コンテキスト固有の条件分岐（例: モック環境のみのスキップ処理）は、意図が伝わる名前の関数に切り出す

## Null 安全性

- API レスポンスの nullable フィールド（Zod スキーマで `.nullable()`）はプロパティアクセス前に必ず null ガードする（例: `agency?.agencyCode ?? null`）

## フォームバリデーション

- フォームのヘルプテキスト・説明文は実際のバリデーション正規表現と一致させる
- 相互依存フィールド（例: メール・パスワードのペア）は `superRefine` でクロスフィールドバリデーションを実装する

## エラーハンドリング

- catch ブロックで `console.error` を削除しない。エラーを握りつぶすとデバッグが困難になる

## セキュリティ

- `e.target` は Text ノード等 `Element` 以外の場合がある。`closest()` を呼ぶ前に `target instanceof Element` ガードまたは `(e.target as Element | null)?.closest?.(...)` で安全に判定する
- 環境変数を CSP やヘッダーに埋め込む場合、`new URL().origin` でパースしてインジェクションを防ぐ。空値の場合はヘッダーに追記しない

## アクセシビリティ

- クリック可能な行（`onRowClick`）にはキーボード操作も対応する: `tabIndex={0}` + `onKeyDown` で Enter/Space をハンドリング
- `onClick` と `onKeyDown` が同じアクションを実行する場合、両方に同じガードロジック（例: インタラクティブ要素の除外判定）を適用する
- インタラクティブ要素の除外セレクタには `label`, `[role="button"]`, `[role="link"]`, `[role="checkbox"]`, `[role="switch"]` も含める
- 画像の alt 属性にはエラー・未ロード時のフォールバック値を設定する（例: `userName || 'ユーザー'`）
- WCAG 基準を引用する場合、正確なレベルとサイズを記載する（例: タッチターゲットは WCAG 2.5.8 AA = 24x24px、WCAG 2.5.5 AAA = 44x44px。混同しない）

## Figma・デザイン準拠

- UI のラベル・用語は Figma デザインの定義に準拠する（例: 技術的に tenantCode でも Figma で「テナントID」ならそのまま使用）
- セマンティックカラー（`bg-muted`, `text-foreground`）を使用する。Figma で明示的に固定色が指定されている場合のみハードコード可
- Figma 上にはデザイントークンに定義されていない色が多数ある。ハードコード色を一律 NG にせず、Figma 指定でトークンにない色はハードコードを許容する
- Tailwind クラス名はプロジェクトの `globals.css` の CSS 変数定義と正確に一致させる（`text-primary` ではなく `text-text-primary` など）
- アバター画像には `object-cover object-center` を付与して縦横比の崩れを防ぐ

## パス・定数

- パスの定数がある場合はハードコードせず、定数（例: `ROUTES`）を使用する
