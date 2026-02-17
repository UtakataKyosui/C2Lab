# ProtoBuf Style Guide

This guide covers naming conventions and file structure for Protocol Buffer definitions, based on Google and Uber's style guides.

## ファイル構成

*   1ファイルにつき1つの `message` / `enum` / `service` を基本とする（密結合なものは除く）。
*   ファイル名は `lower_snake_case.proto`。
*   パッケージ名はディレクトリ構造と一致させる。

## Naming Conventions

*   **Message**: `PascalCase` (例: `UserProfile`, `GetBookRequest`)
*   **Field**: `lower_snake_case` (例: `user_id`, `created_at`)
*   **Enum**: `PascalCase` (例: `UserStatus`)
*   **Enum Value**: `UPPER_SNAKE_CASE` (例: `USER_STATUS_ACTIVE`)
*   **Service**: `PascalCase` (例: `UserService`)
*   **RPC Method**: `PascalCase` (例: `GetUser`)

### Example

```protobuf
syntax = "proto3";

package my.package.v1;

message UserProfile {
  string user_id = 1;
  string display_name = 2;
  string email = 3;
}
```
