---
name: testing-and-mocking
description: TypeScript・React プロジェクトのテストと MSW モックのベストプラクティス。テスト設計・アサーション方針・MSW ハンドラーパターン・モックデータ規約を提供する。テストを書くとき、MSW ハンドラーを追加するときに参照する。
globs:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/msw/**"
  - "**/mocks/**"
  - "**/__mocks__/**"
---

# テストと MSW モックのベストプラクティス

## テスト設計

- ロジックが存在するコンポーネントにはテストを書く
- テスト可能なロジック関数はコンポーネントから `export` して単体テストを書く
- ソースコードのパターンを変更した場合は、関連するテストも同時に更新する
- 複数ファイルにまたがる変更をした場合、Push 前にテストファイルが新しいインターフェース・プロパティに追従しているか必ず確認する

## アサーション方針

- アサーションは意図に合った厳密さで選ぶ
  - 完全一致を期待する場合は `toEqual` を使う
  - `toMatchObject`（部分一致）は意図的にサブセットだけ検証したい場合に限定する
- テストコードでも non-null assertion（`!`）は避ける
  - `querySelector() as HTMLElement` や `getAllByText()[0] as HTMLElement` を使う
  - `@typescript-eslint/no-non-null-assertion` の lint warning を出さない

## MSW モック

- API を呼び出すコンポーネントを追加する場合、対応する MSW モックハンドラーも必ず用意する
- モックのフィルター・検索対象は、UI のプレースホルダーや検索対象と一致させる
- モックデータのメールアドレスや URL には RFC 2606 で予約された `example.com` を使用する
- 環境判定にはユーティリティ関数（例: `isMockEnvironment()`）を使い、`process.env` を直接参照しない。同じ判定ロジックが複数箇所に散在するのを防ぐ
- `withAuth` ラッパーのハンドラーシグネチャを正確に合わせる。引数を使わない場合も `async (_request) => {` のように明示する

## よくあるパターン

### MSW ハンドラー例

```typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/users', async ({ request }) => {
    const url = new URL(request.url)
    const query = url.searchParams.get('q') ?? ''
    const filtered = users.filter(u =>
      u.name.includes(query) || u.email.includes(query)
    )
    return HttpResponse.json({ users: filtered })
  }),
]
```

### withAuth ラッパー例

```typescript
// 引数を使わない場合も明示的に宣言する
const handler = withAuth(async (_request) => {
  return HttpResponse.json({ data: mockData })
})
```

### テストのモックデータ

```typescript
// RFC 2606 準拠のドメインを使用する
const mockUser = {
  email: 'user@example.com',
  avatarUrl: 'https://example.com/avatar.png',
}
```
