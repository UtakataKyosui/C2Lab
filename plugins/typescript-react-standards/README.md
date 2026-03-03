# typescript-react-standards

TypeScript・React コーディング標準ガイドを提供するプラグイン。

## 概要

型定義・コンポーネント設計・DRY・null 安全性・フォームバリデーション・セキュリティ・アクセシビリティ・Figma 準拠ルールを skill として提供する。`.ts` / `.tsx` ファイルを開いているときに自動ロードされる。

## 提供コンポーネント

### Skills

| スキル名 | 説明 |
|----------|------|
| `typescript-react-standards` | TypeScript・React コーディング標準の総合ガイド |

**スキルが自動ロードされるファイルパターン**:
- `**/*.ts`
- `**/*.tsx`

## カバーする領域

| 領域 | 内容 |
|------|------|
| 型定義 | API クライアント型からの導出・共通ラッパー・null ガード |
| コンポーネント設計 | `use client`・`asChild`・Server/Client 境界・`useMemo`・モーダル state 管理 |
| URL パラメータ | `new URL()` パース・nuqs の `history` 設定 |
| DRY・共通化 | Zod スキーマ共通化・マッピングヘルパー抽出 |
| Null 安全性 | nullable フィールドの null ガード |
| フォームバリデーション | ヘルプテキスト一致・`superRefine` クロスフィールド検証 |
| エラーハンドリング | `console.error` 保持 |
| セキュリティ | `e.target` ガード・CSP への環境変数埋め込み |
| アクセシビリティ | キーボード操作・WCAG 基準・alt フォールバック |
| Figma 準拠 | セマンティックカラー・CSS 変数名・ハードコード色の許容判断 |

## フック

なし
