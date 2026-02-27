---
description: プロジェクトの言語・フレームワークに基づいてテストフレームワークを提案する。
---

# tdd-enforce: suggest-framework

プロジェクトに最適なテストフレームワークを提案します。

## 手順

### 1. プロジェクト分析

以下の情報を収集する:

- **言語**: `Cargo.toml`, `package.json`, `go.mod`, `pyproject.toml` 等から検出
- **フレームワーク**: React, Vue, Next.js, FastAPI, Actix-web 等
- **既存のテスト設定**: 設定ファイル、テストディレクトリ、devDependencies

### 2. 言語別テストフレームワーク提案

#### Rust

```
テストフレームワーク提案:

✅ 推奨: cargo test (built-in)
  - 追加インストール不要
  - #[test] アトリビュートでユニットテスト
  - tests/ ディレクトリで統合テスト

オプション:
  - cargo-nextest: 高速並列テストランナー (cargo install cargo-nextest)
  - proptest: プロパティベーステスト (cargo add --dev proptest)
  - mockall: モックライブラリ (cargo add --dev mockall)
  - rstest: パラメータ化テスト (cargo add --dev rstest)
```

#### TypeScript / JavaScript

```
テストフレームワーク提案:

✅ 推奨: Vitest
  - Vite ベースで高速
  - ESM ネイティブ対応
  - Jest 互換 API

代替:
  - Jest: 最も広く使われている。既存プロジェクトに多い
  - Bun test: Bun ランタイム使用時

UI コンポーネントテスト:
  - @testing-library/react (React)
  - @testing-library/vue (Vue)
  - @testing-library/svelte (Svelte)

E2E テスト:
  - Playwright (推奨)
  - Cypress
```

#### Python

```
テストフレームワーク提案:

✅ 推奨: pytest
  - 最も広く使われている
  - 豊富なプラグインエコシステム
  - フィクスチャ機能が強力

代替:
  - unittest: 標準ライブラリ（追加インストール不要）

関連ツール:
  - pytest-cov: カバレッジ
  - pytest-mock: モック
  - pytest-asyncio: 非同期テスト
  - pytest-django: Django プロジェクト
  - httpx: FastAPI テスト
```

#### Go

```
テストフレームワーク提案:

✅ 推奨: testing (built-in)
  - 追加インストール不要
  - テーブル駆動テストが Go の慣習

オプション:
  - testify: アサーション + モック (go get github.com/stretchr/testify)
  - gomock: インターフェースモック生成
  - ginkgo: BDD スタイル
```

#### C# / .NET

```
テストフレームワーク提案:

✅ 推奨: xUnit
  - .NET 公式推奨
  - [Fact] と [Theory] アトリビュート

代替:
  - NUnit: 歴史が長い、豊富な機能
  - MSTest: Microsoft 公式

モック:
  - Moq: 最も人気
  - NSubstitute: 直感的 API
```

#### Java

```
テストフレームワーク提案:

✅ 推奨: JUnit 5
  - 最新版、豊富な機能
  - @ParameterizedTest サポート

代替:
  - TestNG: 高度なテスト設定

モック:
  - Mockito: デファクトスタンダード
```

#### Kotlin

```
テストフレームワーク提案:

✅ 推奨: Kotest (KotlinTest)
  - Kotlin ネイティブ設計、表現力の高い DSL
  - StringSpec, FunSpec, BehaviorSpec など多様なスタイル
  - Coroutines ネイティブサポート

代替:
  - JUnit 5 + Kotlin: 既存 JUnit 環境との互換性
  - JUnit 4: Android プロジェクト向け

モック:
  - MockK: Kotlin 専用、suspend 関数対応
  - Mockito-Kotlin: Mockito の Kotlin ラッパー
```

**build.gradle.kts 設定例:**
```kotlin
plugins {
    kotlin("jvm") version "1.9.0"
}

dependencies {
    // Kotest
    testImplementation("io.kotest:kotest-runner-junit5:5.8.0")
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")

    // MockK
    testImplementation("io.mockk:mockk:1.13.8")

    // Coroutines テスト
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
}

tasks.test {
    useJUnitPlatform()
}
```

### 3. インストールガイド

ユーザーが選択したフレームワークのインストール手順を表示する。

パッケージマネージャーを検出して適切なコマンドを提示:

```
インストール手順:

pnpm add -D vitest @testing-library/react

package.json の scripts に追加:
  "test": "vitest",
  "test:run": "vitest run"
```

### 4. 設定ファイル生成

必要に応じてテスト設定ファイルを生成する:

- `vitest.config.ts`
- `jest.config.ts`
- `pytest.ini` / `pyproject.toml` の `[tool.pytest]` セクション

ユーザーの了承を得てから生成する。
