# Complex Test Patterns

## Authentication State Sharing

Avoid logging in before every test by saving authentication state:

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.playwright/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  await expect(page).toHaveURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

```typescript
// playwright.config.ts — reference the setup project
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'authenticated',
      use: { storageState: '.playwright/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

For quick verification scripts (no persistent config), authenticate inline:

```typescript
test.beforeAll(async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  // Save state for other tests if needed
  await context.storageState({ path: '/tmp/auth.json' });
  await context.close();
});
```

## API Request Interception (Mocking)

Mock slow or flaky APIs during E2E tests:

```typescript
test('エラー状態を表示すること', async ({ page }) => {
  // Intercept API call before navigating
  await page.route('**/api/users', route => route.fulfill({
    status: 500,
    body: JSON.stringify({ error: 'Internal Server Error' }),
  }));

  await page.goto('/users');
  await expect(page.getByRole('alert')).toContainText('エラーが発生しました');
});

test('空のリストを表示すること', async ({ page }) => {
  await page.route('**/api/items', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([]),
  }));

  await page.goto('/items');
  await expect(page.getByText('アイテムがありません')).toBeVisible();
});
```

## Wait for API Response

Confirm that an action triggered a specific API call:

```typescript
test('保存ボタンがAPIを呼び出すこと', async ({ page }) => {
  const saveResponsePromise = page.waitForResponse(
    resp => resp.url().includes('/api/save') && resp.request().method() === 'POST'
  );

  await page.getByRole('button', { name: '保存' }).click();

  const response = await saveResponsePromise;
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.success).toBe(true);
});
```

## File Upload

```typescript
test('ファイルをアップロードできること', async ({ page }) => {
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('/path/to/test-file.pdf');
  await expect(page.getByText('test-file.pdf')).toBeVisible();
  await page.getByRole('button', { name: 'アップロード' }).click();
  await expect(page.getByText('アップロード完了')).toBeVisible();
});
```

## Screenshots on Failure

Take screenshots for debugging when tests fail:

```typescript
test('重要な処理のテスト', async ({ page }) => {
  try {
    await page.goto('/checkout');
    // ... test steps
  } catch (error) {
    await page.screenshot({ path: 'test-results/checkout-failure.png', fullPage: true });
    throw error;
  }
});
```

Or configure globally in `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

## Keyboard Interactions

```typescript
// Tab navigation
await page.keyboard.press('Tab');
await page.keyboard.press('Tab');
await page.keyboard.press('Enter');

// Text input with keyboard
await page.keyboard.type('Hello World');

// Shortcuts
await page.keyboard.press('Control+a');  // Select all
await page.keyboard.press('Control+c');  // Copy

// Arrow navigation in menus/selects
await page.keyboard.press('ArrowDown');
await page.keyboard.press('ArrowUp');
await page.keyboard.press('Escape');
```

## Drag and Drop

```typescript
test('ドラッグ&ドロップが機能すること', async ({ page }) => {
  const source = page.getByTestId('drag-item');
  const target = page.getByTestId('drop-zone');

  await source.dragTo(target);
  await expect(target).toContainText('dropped');
});
```

## Multiple Browser Contexts (Isolation)

```typescript
test('2ユーザー同時操作のテスト', async ({ browser }) => {
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();
  const pageA = await contextA.newPage();
  const pageB = await contextB.newPage();

  await pageA.goto('/chat');
  await pageB.goto('/chat');

  await pageA.getByRole('textbox').fill('Hello from A');
  await pageA.keyboard.press('Enter');
  await expect(pageB.getByText('Hello from A')).toBeVisible({ timeout: 5000 });

  await contextA.close();
  await contextB.close();
});
```

## Testing Responsive Layouts

```typescript
test('モバイルレイアウトが正しいこと', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');

  // Mobile menu should be visible
  await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
  // Desktop nav should be hidden
  await expect(page.getByRole('navigation', { name: 'Main nav' })).toBeHidden();
});
```
