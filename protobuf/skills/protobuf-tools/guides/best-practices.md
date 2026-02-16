# ProtoBuf Best Practices

This document outlines best practices for versioning, field management, and common data patterns in Protocol Buffers.

## 1. バージョニング

Breaking Change を避けるため、パッケージ名にバージョンを含めることを強く推奨します。

```protobuf
package my.server.v1; // Good
```

## 2. フィールド番号の管理

*   フィールド番号は一度割り当てたら変更しない。
*   削除したフィールド番号は `reserved` を使って再利用を防ぐ。

```protobuf
message User {
  reserved 2, 15, 9 to 11;
  reserved "foo", "bar";
  string username = 1;
}
```

## 3. required vs optional

*   `required` は proto3 では廃止されました。すべてのフィールドは optional と見なすべきです。

## 共通パターン

### Timestamp

時刻を扱う場合は `google.protobuf.Timestamp` を使用します。

```protobuf
import "google/protobuf/timestamp.proto";

message Log {
  google.protobuf.Timestamp created_at = 1;
}
```

### Empty

空のメッセージが必要な場合は `google.protobuf.Empty` を使用します。

```protobuf
import "google/protobuf/empty.proto";

service Health {
  rpc Check(google.protobuf.Empty) returns (HealthCheckResponse);
}
```
