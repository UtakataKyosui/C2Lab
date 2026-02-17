# ProtoBuf CLI Tools

This guide covers the usage of standard tools for Protocol Buffer compilation and management.

## protoc (Protocol Buffer Compiler)

`.proto` ファイルから各言語のコードを生成します。

**基本コマンド:**

```bash
protoc --proto_path=src --go_out=build/gen src/foo.proto src/bar/baz.proto
```

## buf (Buf CLI)

現代的な Protobuf ツールチェーン。`protoc` の代替として推奨されます。
Linting, Breaking Change Detection, Formatting などの機能があります。

**Lint:**
```bash
buf lint
```

**Generate:**
```bash
buf generate
```
