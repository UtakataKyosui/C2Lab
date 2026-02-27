# 言語別テストフレームワーク詳細ガイド

## Rust

### 組み込みテスト

Rust はテストフレームワークが言語に組み込まれている。追加インストール不要。

**ユニットテスト**（同一ファイル内）:
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    #[should_panic(expected = "overflow")]
    fn test_overflow() {
        add(u32::MAX, 1);
    }
}
```

**統合テスト**（`tests/` ディレクトリ）:
```rust
// tests/integration_test.rs
use my_crate::add;

#[test]
fn test_add_integration() {
    assert_eq!(add(10, 20), 30);
}
```

**実行コマンド**:
```bash
cargo test                     # 全テスト
cargo test test_name           # 名前でフィルタ
cargo test -- --nocapture      # 標準出力を表示
cargo test -- --test-threads=1 # 逐次実行
```

**推奨追加ツール**:
- `cargo-nextest` - 高速テストランナー
- `proptest` / `quickcheck` - プロパティベーステスト
- `mockall` - モック

### Rust での TDD ファイル構成

```
src/
├── lib.rs          # #[cfg(test)] mod tests { ... }
├── parser.rs       # #[cfg(test)] mod tests { ... }
└── utils.rs        # #[cfg(test)] mod tests { ... }
tests/
├── integration.rs  # 統合テスト
└── e2e.rs          # E2E テスト
```

## TypeScript / JavaScript

### Vitest（推奨）

Vite ベースの高速テストランナー。ESM ネイティブ対応。

```bash
npm install -D vitest
# or
pnpm add -D vitest
```

```typescript
// sum.test.ts
import { describe, it, expect } from 'vitest';
import { sum } from './sum';

describe('sum', () => {
  it('adds two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });

  it('handles negative numbers', () => {
    expect(sum(-1, 1)).toBe(0);
  });
});
```

**設定** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // or 'jsdom' for browser
  },
});
```

### Jest

最も広く使われているテストフレームワーク。

```bash
npm install -D jest @types/jest ts-jest
```

```typescript
// sum.test.ts
import { sum } from './sum';

describe('sum', () => {
  test('adds two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });
});
```

### Testing Library（UI コンポーネント）

```bash
npm install -D @testing-library/react @testing-library/jest-dom
```

```tsx
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button with label', () => {
  render(<Button label="Click me" />);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

### Playwright（E2E）

```bash
npm install -D @playwright/test
```

```typescript
import { test, expect } from '@playwright/test';

test('homepage has title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/My App/);
});
```

### TypeScript テスト選定ガイド

| ユースケース | 推奨 |
|---|---|
| Vite プロジェクト | Vitest |
| 既存 Jest プロジェクト | Jest |
| React/Vue コンポーネント | Vitest + Testing Library |
| E2E テスト | Playwright |
| API テスト | Vitest / Jest + supertest |

## Python

### pytest（推奨）

```bash
pip install pytest
```

```python
# test_calculator.py
from calculator import add

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

class TestCalculator:
    def test_subtract(self):
        assert subtract(5, 3) == 2
```

**フィクスチャ**:
```python
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

**実行**:
```bash
pytest                        # 全テスト
pytest test_file.py           # 特定ファイル
pytest -k "test_add"          # 名前でフィルタ
pytest -v                     # 詳細出力
pytest --cov=src              # カバレッジ
```

### unittest（標準ライブラリ）

```python
import unittest

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
```

### Python テスト選定ガイド

| ユースケース | 推奨 |
|---|---|
| 一般的な Python プロジェクト | pytest |
| 標準ライブラリのみ | unittest |
| Django プロジェクト | pytest-django |
| FastAPI プロジェクト | pytest + httpx |

## Go

### 標準 testing パッケージ

Go はテストが言語に組み込まれている。

```go
// calculator_test.go
package calculator

import "testing"

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d; want %d", got, want)
    }
}

// テーブル駆動テスト（Go の慣用パターン）
func TestAddTableDriven(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, 1, 0},
        {"zero", 0, 0, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

**実行**:
```bash
go test ./...              # 全パッケージ
go test -v ./...           # 詳細出力
go test -run TestAdd ./... # 名前でフィルタ
go test -cover ./...       # カバレッジ
```

**推奨追加ツール**:
- `testify` - アサーション、モック、スイート
- `gomock` - インターフェースモック生成
- `ginkgo` - BDD スタイルテスト

## C# / .NET

### xUnit（推奨）

```csharp
public class CalculatorTests
{
    [Fact]
    public void Add_TwoNumbers_ReturnsSum()
    {
        var calc = new Calculator();
        Assert.Equal(5, calc.Add(2, 3));
    }

    [Theory]
    [InlineData(1, 2, 3)]
    [InlineData(-1, 1, 0)]
    public void Add_Various_ReturnsCorrectSum(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.Equal(expected, calc.Add(a, b));
    }
}
```

## Java

### JUnit 5

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    @Test
    void addTwoNumbers() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }

    @ParameterizedTest
    @CsvSource({"1,2,3", "-1,1,0"})
    void addVarious(int a, int b, int expected) {
        assertEquals(expected, new Calculator().add(a, b));
    }
}
```

## Kotlin

### Kotest（旧 KotlinTest）

Kotlin ネイティブのテストフレームワーク（旧称 KotlinTest）。

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("io.kotest:kotest-runner-junit5:5.8.0")
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")
}
```

```kotlin
// CalculatorTest.kt
import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe

class CalculatorTest : StringSpec({
    "add two numbers" {
        Calculator().add(2, 3) shouldBe 5
    }

    "handle negative numbers" {
        Calculator().add(-1, 1) shouldBe 0
    }
})
```

**スタイル例（FunSpec）**:
```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.matchers.shouldBe

class CalculatorTest : FunSpec({
    test("add returns sum") {
        Calculator().add(2, 3) shouldBe 5
    }

    context("edge cases") {
        test("negative numbers") {
            Calculator().add(-1, 1) shouldBe 0
        }
    }
})
```

### JUnit 5 for Kotlin

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class CalculatorTest {
    @Test
    fun `add two numbers returns sum`() {
        assertEquals(5, Calculator().add(2, 3))
    }

    @ParameterizedTest
    @CsvSource("1, 2, 3", "-1, 1, 0")
    fun `add various`(a: Int, b: Int, expected: Int) {
        assertEquals(expected, Calculator().add(a, b))
    }
}
```

### MockK（モック）

Kotlin 専用モックライブラリ。Mockito より Kotlin フレンドリー。

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("io.mockk:mockk:1.13.8")
}
```

```kotlin
import io.mockk.*
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class OrderServiceTest {
    @Test
    fun `process order calls repository`() {
        val repository = mockk<OrderRepository>()
        every { repository.save(any()) } returns Unit

        val service = OrderService(repository)
        service.processOrder(Order(id = 1))

        verify { repository.save(any()) }
    }
}
```

**実行コマンド**:
```bash
./gradlew test              # 全テスト
./gradlew test --tests "com.example.*Test"  # フィルタ
./gradlew test --info       # 詳細出力
```

### Kotlin テスト選定ガイド

| ユースケース | 推奨 |
|---|---|
| 新規 Kotlin プロジェクト | Kotest |
| 既存 JUnit 5 プロジェクト | JUnit 5 + Kotlin |
| モック | MockK |
| Android | JUnit 4/5 + Robolectric |
| Coroutines テスト | Kotest + kotlinx-coroutines-test |

### Kotlin テストファイル構成

```
src/
├── main/
│   └── kotlin/
│       └── com/example/
│           └── Calculator.kt
└── test/
    └── kotlin/
        └── com/example/
            └── CalculatorTest.kt
```
