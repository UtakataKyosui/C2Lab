# Advanced Locator Patterns

## Role-Based Locators

ARIA roles provide the most resilient locators. Prefer these over CSS/XPath.

```typescript
// Headings by level
page.getByRole('heading', { name: 'Title', level: 1 })
page.getByRole('heading', { level: 2 })  // any h2

// Navigation and lists
page.getByRole('navigation')
page.getByRole('list')
page.getByRole('listitem')

// Tables
page.getByRole('table')
page.getByRole('row', { name: 'Row title' })
page.getByRole('cell', { name: 'Cell value' })

// Dialogs
page.getByRole('dialog')
page.getByRole('alertdialog')

// Status regions
page.getByRole('status')  // live regions for status messages
page.getByRole('alert')   // error/warning messages
```

## Scoped Locators (chaining)

Scope locators to avoid ambiguity when the same text appears multiple times:

```typescript
// Scope to a specific section
const loginForm = page.getByRole('form', { name: 'Login' });
await loginForm.getByLabel('Email').fill('user@example.com');
await loginForm.getByRole('button', { name: 'Submit' }).click();

// Scope to a list item
const firstItem = page.getByRole('listitem').first();
await firstItem.getByRole('button', { name: 'Delete' }).click();

// Scope to a table row
const row = page.getByRole('row', { name: 'Alice' });
await row.getByRole('button', { name: 'Edit' }).click();
```

## Filtering Locators

```typescript
// Filter by text content
page.getByRole('listitem').filter({ hasText: 'Apple' })
page.getByRole('listitem').filter({ hasText: /price: \$\d+/ })

// Filter by contained element
page.getByRole('listitem').filter({ has: page.getByRole('checkbox', { checked: true }) })

// Filter by NOT containing
page.getByRole('listitem').filter({ hasNot: page.getByText('Sold out') })

// nth element
page.getByRole('button', { name: 'Edit' }).nth(2)  // 0-indexed, third button
page.getByRole('button', { name: 'Edit' }).first()
page.getByRole('button', { name: 'Edit' }).last()
```

## data-testid Locators

Use `data-testid` attributes for elements that are hard to describe semantically:

```typescript
// HTML: <div data-testid="product-card">...</div>
page.getByTestId('product-card')

// Custom attribute name (if project uses different attribute)
page.locator('[data-cy="submit-btn"]')
page.locator('[data-qa="user-menu"]')
```

## XPath and CSS (Last Resort)

```typescript
// CSS selector
page.locator('.submit-button')  // by class
page.locator('#main-content')   // by id
page.locator('input[type="email"]')  // by attribute

// XPath (avoid if possible)
page.locator('xpath=//button[contains(text(), "Submit")]')
page.locator('//table//tr[2]')  // shorthand without xpath= prefix
```

## Handling Dynamic Content

```typescript
// Wait for element to appear (auto-retry built in)
await expect(page.getByText('Loading complete')).toBeVisible({ timeout: 10000 });

// Wait for element to disappear
await expect(page.getByRole('progressbar')).toBeHidden();

// Wait for count to change
await expect(page.getByRole('listitem')).toHaveCount(5);

// Polling for custom condition
await page.waitForFunction(() => document.querySelectorAll('.item').length > 3);
```

## Accessibility Queries

Verify accessibility attributes:

```typescript
// Check aria-label
await expect(page.locator('[aria-label="Close dialog"]')).toBeVisible();

// Check aria-expanded
await expect(page.getByRole('button', { name: 'Menu' })).toHaveAttribute('aria-expanded', 'false');

// Check aria-selected
await expect(page.getByRole('tab', { name: 'Profile' })).toHaveAttribute('aria-selected', 'true');
```
