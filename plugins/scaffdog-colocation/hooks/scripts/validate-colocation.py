#!/usr/bin/env python3
"""
PostToolUse hook: コロケーションパターンの簡易検証（advisory）

Edit/Write ツール使用後に実行され、作成・編集されたファイルが
コロケーションパターンに準拠しているかを簡易チェックする。

- ブロックしない（常に exit 0）
- 外部依存なし（stdlib のみ）
- 警告のみ出力
"""

import json
import os
import re
import sys

# 除外ディレクトリ（ビルド成果物・依存パッケージ等）
EXCLUDED_DIRS = ("node_modules", "dist", "build", ".next", ".nuxt")

# コンポーネント系ディレクトリ名
COMPONENT_DIR_NAMES = (
    f"{os.sep}components{os.sep}",
    f"{os.sep}features{os.sep}",
    f"{os.sep}hooks{os.sep}",
)

# barrel チェックを省略するディレクトリ名
IGNORED_BARREL_CHECK_DIRS = {
    "components",
    "features",
    "hooks",
    "utils",
    "types",
    "constants",
    "scripts",
    "styles",
    "pages",
    "app",
}

# PascalCase チェックを省略するディレクトリ名
IGNORED_PASCALCASE_DIRS = {"components", "hooks", "utils", "types", "constants"}


def read_input():
    """stdin から PostToolUse の JSON データを読み取る"""
    try:
        data = json.loads(sys.stdin.read())
        return data
    except (json.JSONDecodeError, EOFError):
        return None


def extract_file_path(data):
    """ツール実行データからファイルパスを抽出する"""
    if not data:
        return None
    return data.get("tool_input", {}).get("file_path")


def is_in_component_dir(file_path):
    """ファイルがコンポーネントディレクトリ内にあるかチェック"""
    for d in EXCLUDED_DIRS:
        if f"{os.sep}{d}{os.sep}" in file_path or file_path.startswith(f"{d}{os.sep}"):
            return False
    return any(d in file_path for d in COMPONENT_DIR_NAMES)


def get_component_dir(file_path):
    """ファイルパスからコンポーネントディレクトリを取得する"""
    dir_path = os.path.dirname(file_path)
    return dir_path


def check_barrel_exists(component_dir):
    """index.ts / index.tsx / index.js / index.jsx が存在するかチェック"""
    for ext in ["index.ts", "index.tsx", "index.js", "index.jsx"]:
        if os.path.exists(os.path.join(component_dir, ext)):
            return True
    return False


def check_naming_convention(component_dir, file_path):
    """命名規則のチェック"""
    warnings = []
    dir_name = os.path.basename(component_dir)
    file_name = os.path.basename(file_path)

    # コンポーネントディレクトリがPascalCaseかチェック
    if (
        f"{os.sep}components{os.sep}" in component_dir
        and not re.match(r"^[A-Z][a-zA-Z0-9]*$", dir_name)
        and dir_name not in IGNORED_PASCALCASE_DIRS
    ):
        warnings.append(f"ディレクトリ名 '{dir_name}' が PascalCase ではありません")

    # index ファイル以外がディレクトリ名を接頭辞に持つかチェック
    if file_name not in ("index.ts", "index.tsx", "index.js", "index.jsx"):
        base_name = file_name.split(".", 1)[0]
        # use* プレフィックスのフックファイルは除外
        if (
            not base_name.startswith("use")
            and base_name != dir_name
            and f"{os.sep}components{os.sep}" in component_dir
        ):
            # サブディレクトリ内のファイルは除外
            parent_of_dir = os.path.basename(os.path.dirname(component_dir))
            if parent_of_dir == "components":
                warnings.append(
                    f"ファイル名 '{file_name}' がディレクトリ名 '{dir_name}' と一致しません"
                )

    return warnings


def main():
    data = read_input()
    file_path = extract_file_path(data)

    if not file_path:
        sys.exit(0)

    # コンポーネントディレクトリ外のファイルはスキップ
    if not is_in_component_dir(file_path):
        sys.exit(0)

    component_dir = get_component_dir(file_path)
    warnings = []

    # barrel ファイルの存在チェック
    if not check_barrel_exists(component_dir):
        dir_name = os.path.basename(component_dir)
        # コンポーネントディレクトリ直下の場合のみ警告
        if dir_name not in IGNORED_BARREL_CHECK_DIRS:
            warnings.append(
                f"[colocation] {component_dir} に barrel file (index.ts/tsx/js/jsx) がありません"
            )

    # 命名規則チェック
    naming_warnings = check_naming_convention(component_dir, file_path)
    for w in naming_warnings:
        warnings.append(f"[colocation] {w}")

    # 警告出力
    if warnings:
        for w in warnings:
            print(w, file=sys.stderr)

    # 常に exit 0（ブロックしない）
    sys.exit(0)


if __name__ == "__main__":
    main()
