---
name: playwright-testing
description: This skill should be used when the user asks to "write Playwright tests", "create E2E tests with Playwright", "verify web app behavior with Playwright", "run Playwright to check if this works", or when working with playwright-dev-tester or playwright-review-tester agents. Provides TypeScript Playwright test patterns, locator strategies, assertion techniques, and project setup guidance.
---

## Overview

Playwright is a Node.js library for end-to-end browser automation. Use it to verify that web application features work correctly by simulating real user interactions in a browser.

This skill covers TypeScript Playwright usage as a **library** (via `@playwright/test`), not the Playwright MCP server.

## Project Setup

### Install Playwright

```bash
npm install -D @playwright/test
npx playwright install chromium  # Install Chromium browser (minimum required)
```

### Check Existing Configuration

Use `Glob` to check for `playwright.config.ts` or `playwright.config.js` before creating tests. If a config exists, read it to understand:

- `baseURL` — the dev server URL
- `testDir` — where tests are expected
- `projects` — which browsers are configured

### Minimal playwright.config.ts (create only if missing)

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
```

## Test File Structure

### Standard Test File Layout

```typescript
// e2e/<feature-name>.spec.ts
import { test, expect } from '@playwright/test';

test.describe('<Feature or page name>', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/path/to/page');  // relative if baseURL set, absolute otherwise
  });

  test('<what this test verifies>', async ({ page }) => {
    // arrange → act → assert
  });
});
```

### File Naming Conventions

- Development verification: `e2e/verify-<feature>.spec.ts`
- PR review testing: `e2e/review-pr<NUMBER>-<feature>.spec.ts`
- Regression tests: `e2e/<feature>.spec.ts`

## Locator Strategies

### Priority Order (use top ones first)

1. `getByRole()` — matches ARIA role + accessible name
2. `getByLabel()` — matches form input via label text
3. `getByPlaceholder()` — matches input via placeholder
4. `getByText()` — matches element by visible text
5. `getByTestId()` — matches `data-testid` attribute
6. `locator('css=...')` — CSS selector (last resort)

### Common Examples

```typescript
// Buttons
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('button', { name: /save/i }).click();  // case-insensitive regex

// Form inputs
await page.getByLabel('Email').fill('user@example.com');
await page.getByPlaceholder('Enter your name').fill('John');

// Links
await page.getByRole('link', { name: 'Dashboard' }).click();

// Text content
await expect(page.getByText('Welcome back!')).toBeVisible();
await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

// Dropdowns
await page.getByRole('combobox', { name: 'Country' }).selectOption('Japan');

// Checkboxes
await page.getByRole('checkbox', { name: 'Remember me' }).check();
```

## Assertions

### Visibility and State

```typescript
await expect(locator).toBeVisible();       // element is visible
await expect(locator).toBeHidden();        // element is hidden
await expect(locator).toBeEnabled();       // input is not disabled
await expect(locator).toBeDisabled();      // input is disabled
await expect(locator).toBeChecked();       // checkbox is checked
```

### Content

```typescript
await expect(locator).toHaveText('exact text');
await expect(locator).toContainText('partial text');
await expect(locator).toHaveValue('input value');
await expect(locator).toHaveCount(3);      // number of matching elements
```

### URL and Page

```typescript
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveURL(/\/dashboard/);  // regex
await expect(page).toHaveTitle('My App');
```

### Waiting (built-in auto-wait)

Playwright automatically waits for elements to be actionable before clicks/fills. For custom waits:

```typescript
// Wait for navigation
await page.waitForURL('/new-page');

// Wait for element to appear
await page.waitForSelector('[data-testid="result"]');

// Wait for response
await page.waitForResponse(resp => resp.url().includes('/api/data') && resp.status() === 200);
```

## Common User Flow Patterns

### Login Flow

```typescript
test('ログインが成功すること', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('メールアドレス').fill('user@example.com');
  await page.getByLabel('パスワード').fill('password123');
  await page.getByRole('button', { name: 'ログイン' }).click();
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'ダッシュボード' })).toBeVisible();
});
```

### Form Submission

```typescript
test('フォームの送信が成功すること', async ({ page }) => {
  await page.getByLabel('タイトル').fill('新しい投稿');
  await page.getByLabel('本文').fill('内容をここに');
  await page.getByRole('button', { name: '投稿する' }).click();
  await expect(page.getByText('投稿しました')).toBeVisible();
});
```

### Navigation

```typescript
test('ナビゲーションが機能すること', async ({ page }) => {
  await page.getByRole('link', { name: '設定' }).click();
  await expect(page).toHaveURL('/settings');
  await page.getByRole('link', { name: 'ホーム' }).click();
  await expect(page).toHaveURL('/');
});
```

### Error State

```typescript
test('バリデーションエラーが表示されること', async ({ page }) => {
  await page.getByRole('button', { name: '送信' }).click();  // empty form
  await expect(page.getByText('メールアドレスは必須です')).toBeVisible();
});
```

## Running Tests

### Basic Execution

```bash
# Run all tests
npx playwright test

# Run specific file
npx playwright test e2e/verify-login.spec.ts

# Run with specific browser only (faster for verification)
npx playwright test --project=chromium

# Run with visible browser (for debugging)
npx playwright test --headed

# Verbose output
npx playwright test --reporter=list
```

### When No Config File Exists

```bash
# Specify all settings inline
npx playwright test e2e/verify-login.spec.ts --project=chromium --reporter=list
```

If the test needs a specific `baseURL`, set it inside the test file:

```typescript
import { test, expect } from '@playwright/test';

test.use({ baseURL: 'http://localhost:3000' });

test('...', async ({ page }) => {
  await page.goto('/');  // goes to http://localhost:3000/
});
```

## Dev Server Startup

### Detect Port

Check in this order:

```bash
# 1. package.json scripts for --port flag
grep -E "port|PORT" package.json

# 2. vite.config.ts/js
grep -E "port" vite.config.ts 2>/dev/null

# 3. next.config.ts/js (default is 3000)
cat next.config.ts 2>/dev/null

# 4. Default fallback: 3000 (Next.js, Create React App), 5173 (Vite)
```

### Start in Background and Wait

```bash
npm run dev &
DEV_PID=$!

# Poll until server responds (max 30 seconds)
for i in $(seq 1 30); do
  curl -s http://localhost:<PORT> > /dev/null && break
  sleep 1
done
```

### Check if Already Running

```bash
# lsof (macOS/多くのLinux環境で利用可能)
lsof -i :<PORT> | grep LISTEN
# lsof が使えない環境では ss (Linux) または netstat (Windows/Linux) を使用:
# ss -tlnp | grep :<PORT>
# netstat -an | grep :<PORT>
```

If already running, skip startup.

## Troubleshooting Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `browserType.launch` error | Browser not installed | Run `npx playwright install` |
| Element not found | Wrong locator or async load | Use `waitFor` or check HTML structure |
| Timeout on navigation | Dev server not ready | Add `waitForURL` or increase timeout |
| `Error: page.goto` fails | Wrong URL or server not running | Verify server is up and URL is correct |
| Test flakiness | Race conditions | Add explicit `waitFor` assertions |

## Additional Resources

For detailed patterns:
- **`references/locator-patterns.md`** — Advanced locator patterns and accessibility queries
- **`references/test-patterns.md`** — Complex flow patterns (auth state, API mocking, file upload)
