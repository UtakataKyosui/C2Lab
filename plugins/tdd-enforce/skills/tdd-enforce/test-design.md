# テスト設計の原則とベストプラクティス

## テスト設計の基本

### Arrange-Act-Assert (AAA)

テストの3段階構造。最も広く使われるパターン。

```typescript
// Arrange: テストデータとオブジェクトの準備
const calculator = new Calculator();
const input = { a: 2, b: 3 };

// Act: テスト対象の実行
const result = calculator.add(input.a, input.b);

// Assert: 結果の検証
expect(result).toBe(5);
```

### Given-When-Then (GWT)

BDD（振る舞い駆動開発）スタイル。自然言語に近い。

```python
def test_withdraw_sufficient_balance():
    # Given: 残高が十分にある口座
    account = Account(balance=1000)

    # When: 500を引き出す
    account.withdraw(500)

    # Then: 残高が500になる
    assert account.balance == 500
```

## テストダブル（モック・スタブ）

### 用語

| 種類 | 目的 | 例 |
|---|---|---|
| Stub | 固定値を返す | `stub.get_user() → User("test")` |
| Mock | 呼び出しを検証する | `mock.verify_called_once()` |
| Fake | 簡易実装 | インメモリDB |
| Spy | 実際の処理 + 記録 | 実際に送信しつつ記録 |

### モックの使い方

**Rust (mockall)**:
```rust
#[automock]
trait UserRepository {
    fn find_by_id(&self, id: u64) -> Option<User>;
}

#[test]
fn test_get_user() {
    let mut mock = MockUserRepository::new();
    mock.expect_find_by_id()
        .with(eq(1))
        .returning(|_| Some(User { id: 1, name: "Alice".into() }));

    let service = UserService::new(mock);
    let user = service.get_user(1).unwrap();
    assert_eq!(user.name, "Alice");
}
```

**TypeScript (Vitest)**:
```typescript
import { vi } from 'vitest';

const mockFetch = vi.fn().mockResolvedValue({ data: 'test' });
const service = new ApiService(mockFetch);

await service.getData();
expect(mockFetch).toHaveBeenCalledOnce();
```

**Python (unittest.mock)**:
```python
from unittest.mock import Mock, patch

@patch('module.external_api')
def test_process(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = process_data()
    assert result == "ok"
    mock_api.assert_called_once()
```

**Go (gomock)**:
```go
ctrl := gomock.NewController(t)
defer ctrl.Finish()

mockRepo := NewMockUserRepository(ctrl)
mockRepo.EXPECT().FindByID(1).Return(&User{Name: "Alice"}, nil)

service := NewUserService(mockRepo)
user, err := service.GetUser(1)
assert.NoError(t, err)
assert.Equal(t, "Alice", user.Name)
```

## テストの種類と使い分け

### ユニットテスト

- **対象**: 関数、メソッド、クラス
- **特徴**: 高速、依存関係なし
- **テスト比率**: 70-80%

```rust
#[test]
fn test_validate_email() {
    assert!(validate_email("user@example.com"));
    assert!(!validate_email("invalid"));
    assert!(!validate_email(""));
}
```

### 統合テスト

- **対象**: モジュール間の連携
- **特徴**: 実際の依存関係を使用
- **テスト比率**: 15-20%

```rust
// tests/api_integration.rs
#[tokio::test]
async fn test_create_and_fetch_user() {
    let db = setup_test_db().await;
    let repo = UserRepository::new(db);

    repo.create(User { name: "Alice".into() }).await.unwrap();
    let user = repo.find_by_name("Alice").await.unwrap();
    assert_eq!(user.name, "Alice");
}
```

### E2E テスト

- **対象**: ユーザーシナリオ全体
- **特徴**: 遅い、壊れやすい
- **テスト比率**: 5-10%

```typescript
// e2e/login.spec.ts
test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

## エッジケーステスト

テストすべきエッジケース:

1. **空入力**: `""`, `[]`, `None`, `null`
2. **境界値**: `0`, `-1`, `MAX_VALUE`, `MIN_VALUE`
3. **異常入力**: 不正な型、範囲外、特殊文字
4. **並行性**: 複数スレッドからのアクセス
5. **エラー**: ネットワーク障害、ファイル不在、権限不足

```rust
#[test]
fn test_divide_by_zero() {
    let result = divide(10, 0);
    assert!(result.is_err());
}

#[test]
fn test_empty_list_average() {
    let result = average(&[]);
    assert_eq!(result, None);
}

#[test]
fn test_max_value_overflow() {
    let result = add(i32::MAX, 1);
    assert!(result.is_err());
}
```

## テストのメンテナンス

### テストヘルパー

繰り返し使うセットアップはヘルパーに抽出:

```rust
fn create_test_user(name: &str) -> User {
    User {
        id: 0,
        name: name.to_string(),
        email: format!("{}@test.com", name.to_lowercase()),
    }
}

#[test]
fn test_user_display() {
    let user = create_test_user("Alice");
    assert_eq!(user.display_name(), "Alice");
}
```

### テストデータビルダー

複雑なオブジェクトにはビルダーパターン:

```rust
struct UserBuilder {
    name: String,
    email: String,
    active: bool,
}

impl UserBuilder {
    fn new() -> Self {
        Self {
            name: "Default".into(),
            email: "default@test.com".into(),
            active: true,
        }
    }

    fn name(mut self, name: &str) -> Self {
        self.name = name.into();
        self
    }

    fn build(self) -> User {
        User { name: self.name, email: self.email, active: self.active }
    }
}

#[test]
fn test_inactive_user() {
    let user = UserBuilder::new().name("Bob").build();
    assert_eq!(user.name, "Bob");
}
```

## TDD における CI/CD 連携

テストは CI パイプラインで自動実行する:

```yaml
# GitHub Actions 例
- name: Run tests
  run: cargo test --all

- name: Check coverage
  run: cargo tarpaulin --out Xml
```

テストが失敗した場合はマージをブロックする設定を推奨。
