# TDD パターンとアンチパターン

## TDD の基本パターン

### 1. Obvious Implementation（明白な実装）

テストが明白な場合、直接正しい実装を書く。

```
Red:   test_add(2, 3) → expected 5
Green: fn add(a, b) { a + b }  // 明白なので直接実装
```

### 2. Fake It（偽装実装）

まずハードコードで通し、徐々に一般化する。

```
Red:   test_add(2, 3) → expected 5
Green: fn add(a, b) { 5 }      // まずハードコード
Red:   test_add(1, 1) → expected 2
Green: fn add(a, b) { a + b }  // 一般化
```

### 3. Triangulation（三角測量）

複数のテストケースで実装を強制する。

```
test_add(2, 3) → 5
test_add(0, 0) → 0
test_add(-1, 1) → 0
// 3つのテストで add の正しい実装が決まる
```

### 4. One to Many（1つから多数へ）

単一要素のテストから始め、コレクションへ拡張する。

```
Red:   test_sum([5]) → 5
Green: fn sum(list) { list[0] }
Red:   test_sum([1, 2, 3]) → 6
Green: fn sum(list) { list.iter().sum() }
```

## テスト作成の原則

### FIRST 原則

- **F**ast: テストは高速に実行される
- **I**ndependent: テスト間に依存関係がない
- **R**epeatable: 何度実行しても同じ結果
- **S**elf-validating: テスト自体が合否を判定する
- **T**imely: 実装の前にテストを書く（TDD）

### テストの命名規則

**何をテストしているかが名前から分かること。**

```
// Good
test_parse_valid_json_returns_object()
test_parse_invalid_json_returns_error()
test_empty_input_returns_none()

// Bad
test1()
test_parse()
test_it_works()
```

**パターン**: `test_{対象}_{条件}_{期待結果}`

### テストのサイズ

- **1テスト = 1アサーション**（原則）
- 複数アサーションは関連する場合のみ許可
- テスト関数は10-15行以内を目安
- Arrange が大きい場合はフィクスチャやヘルパーに抽出

## TDD サイクルの実践

### ステップ 1: Red（失敗するテストを書く）

```rust
#[test]
fn test_parse_number() {
    let result = parse("42");
    assert_eq!(result, Token::Number(42));
}
```

この時点で `parse` 関数も `Token` 型も存在しない → コンパイルエラー = Red。

### ステップ 2: Green（最小限の実装）

```rust
enum Token {
    Number(i32),
}

fn parse(input: &str) -> Token {
    Token::Number(input.parse().unwrap())
}
```

テストがパスする最小限のコード。エラーハンドリングは後回し。

### ステップ 3: Refactor

```rust
fn parse(input: &str) -> Result<Token, ParseError> {
    let n = input.parse::<i32>().map_err(|_| ParseError::InvalidNumber)?;
    Ok(Token::Number(n))
}
```

テストを更新しながらリファクタリング。

### ステップ 4: 次のテスト

```rust
#[test]
fn test_parse_invalid_input() {
    let result = parse("abc");
    assert!(result.is_err());
}
```

新しいテストケースで次の Red を作る。

## アンチパターン

### 1. Test After（後付けテスト）

```
// BAD: 実装してからテストを書く
fn complex_function() { ... }  // 先に実装
#[test] fn test_complex() { ... }  // 後からテスト

// GOOD: テストを先に書く
#[test] fn test_complex() { ... }  // 先にテスト（Red）
fn complex_function() { ... }      // テストを通す実装（Green）
```

**問題**: テスト可能な設計にならない。テストが実装に引きずられる。

### 2. Testing Implementation（実装の詳細テスト）

```
// BAD: 内部実装をテスト
assert_eq!(cache.internal_map.len(), 3);

// GOOD: 振る舞いをテスト
assert_eq!(cache.get("key"), Some("value"));
```

### 3. Fragile Tests（壊れやすいテスト）

```
// BAD: 出力の全文一致
assert_eq!(output, "Error at line 5: unexpected token ';'");

// GOOD: 重要な部分のみ検証
assert!(output.contains("unexpected token"));
assert!(output.contains("line 5"));
```

### 4. God Test（巨大テスト）

```
// BAD: 1テストで複数の振る舞いを検証
#[test]
fn test_everything() {
    // 20行のセットアップ
    // パース、変換、保存、通知を全部テスト
}

// GOOD: 1テスト1振る舞い
#[test] fn test_parse() { ... }
#[test] fn test_transform() { ... }
#[test] fn test_save() { ... }
```

### 5. Slow Tests（遅いテスト）

```
// BAD: テスト内でネットワーク通信
fn test_fetch_data() {
    let data = http_client.get("https://api.example.com");
}

// GOOD: モックを使用
fn test_fetch_data() {
    let mock_client = MockHttpClient::new();
    mock_client.expect_get().returning(|_| Ok(sample_data()));
}
```

## テストピラミッド

```
        /  E2E  \        少量（遅い、高コスト）
       /----------\
      / Integration \    中程度
     /----------------\
    /   Unit Tests     \  大量（速い、低コスト）
   /--------------------\
```

- **Unit Tests**: 70-80%。個々の関数・メソッド。高速。
- **Integration Tests**: 15-20%。モジュール間連携。
- **E2E Tests**: 5-10%。ユーザーシナリオ。最も遅い。

## TDD で書くべきでないテスト

- 外部ライブラリの機能テスト（信頼する）
- 単純な getter/setter
- フレームワークが生成したボイラープレート
- 設定ファイルのバリデーション（CI/lint に任せる）
