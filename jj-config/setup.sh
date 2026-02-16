#!/usr/bin/env bash
# .jj/repo/config.toml → jj-config/config.toml のシンボリックリンクを作成する
# クローン直後や .jj を作り直した後に一度だけ実行する
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$REPO_ROOT/jj-config/config.toml"
TARGET_DIR="$REPO_ROOT/.jj/repo"
TARGET="$TARGET_DIR/config.toml"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR が見つかりません。jj リポジトリのルートから実行してください。"
    exit 1
fi

if [ -L "$TARGET" ]; then
    echo "シンボリックリンクはすでに存在します: $TARGET"
    echo "  -> $(readlink "$TARGET")"
    exit 0
fi

if [ -f "$TARGET" ]; then
    BACKUP="${TARGET}.bak"
    echo "既存の config.toml をバックアップします: $BACKUP"
    mv "$TARGET" "$BACKUP"
fi

ln -s "$SOURCE" "$TARGET"
echo "シンボリックリンクを作成しました: $TARGET -> $SOURCE"
