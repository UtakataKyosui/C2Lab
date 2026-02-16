#!/usr/bin/env python3
"""
PostToolUse hook: WASM 最適化候補の軽量検出（Advisory のみ）

Edit/Write ツール使用後に実行され、JS/TS ファイルに含まれる
重い処理パターンを regex で検出し、WASM ライブラリへの置き換えを提案する。

- 常に exit 0（advisory のみ、ブロックしない）
- 外部依存なし（stdlib のみ）
- JS/TS ファイル以外はスキップ
"""

import json
import os
import re
import sys

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB


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
    tool_input = data.get("tool_input", {})
    if "file_path" in tool_input:
        return tool_input["file_path"]
    return None


def is_js_ts_file(file_path):
    """JS/TS ファイルかどうか判定する"""
    js_ts_extensions = (".js", ".ts", ".tsx", ".jsx", ".mjs")
    return any(file_path.endswith(ext) for ext in js_ts_extensions)


def is_excluded_file(file_path):
    """スキャン不要なファイルかどうか判定する"""
    basename = os.path.basename(file_path)

    # テストファイル
    if re.match(r".*\.(test|spec)\.(ts|tsx|js|jsx)$", basename):
        return True

    # 設定ファイル
    if re.match(r".*\.config\.(ts|js|mjs)$", basename):
        return True

    # 型定義
    if basename.endswith((".d.ts", ".types.ts")):
        return True

    # node_modules, dist 等
    excluded_dirs = ("node_modules", "dist", "build", ".next", ".nuxt")
    for d in excluded_dirs:
        if f"/{d}/" in file_path:
            return True

    return False


# 検出パターン定義
PATTERNS = [
    {
        "name": "CryptoJS / crypto-js",
        "regex": r"""(?:import|require)\s*\(?.*(?:crypto-js|CryptoJS)""",
        "suggestion": "@noble/hashes または libsodium-wrappers",
        "detail": "CryptoJS はメンテナンス停止しており、セキュリティ面でも移行推奨",
    },
    {
        "name": "Canvas ピクセル操作",
        "regex": r"""(?:getImageData|putImageData|imageData\.data\[)""",
        "suggestion": "wasm-vips または @squoosh/lib",
        "detail": "ピクセル単位の操作は WASM で 5-20x 高速化可能",
    },
    {
        "name": "pako / zlib 圧縮",
        "regex": r"""(?:import|require)\s*\(?.*(?:pako|zlib)""",
        "suggestion": "fflate または brotli-wasm",
        "detail": "fflate は pako より 3-5x 高速で軽量",
    },
    {
        "name": "ループ内 JSON.parse",
        "regex": r"""(?:for|while|\.(?:map|forEach|reduce))\s*\(.*?(?:\{|=>).*?JSON\.parse""",
        "suggestion": "simd_json_wasm",
        "detail": "大量データの JSON パースは SIMD WASM で 2-5x 高速化可能",
    },
    {
        "name": "手動文字列距離関数",
        "regex": r"""(?:function\s+|(?:const|let|var)\s+)(?:levenshtein|editDistance|hammingDistance|jaroWinkler|damerauLevenshtein)\s*[=(]""",
        "suggestion": "wasm-pack カスタム Rust ビルド",
        "detail": "文字列距離計算は Rust/WASM で 10-50x 高速化可能",
    },
    {
        "name": "3重ネストループ (行列演算候補)",
        "regex": r"""for\s*\([^)]{0,200}\)\s*\{.*?for\s*\([^)]{0,200}\)\s*\{.*?for\s*\([^)]{0,200}\)""",
        "suggestion": "@stdlib/stdlib WASM または wasm-pack Rust ビルド",
        "detail": "行列演算パターンは WASM で 5-20x 高速化可能",
    },
    {
        "name": "DOMParser XML パース",
        "regex": r"""new\s+DOMParser\s*\(\s*\)""",
        "suggestion": "fast-xml-parser",
        "detail": "fast-xml-parser は DOMParser より 10x 以上高速",
    },
]


def detect_patterns(file_path):
    """ファイル内容からパターンを検出する"""
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, UnicodeDecodeError):
        return []

    detected = []
    for pattern in PATTERNS:
        if re.search(pattern["regex"], content, re.DOTALL):
            detected.append(pattern)

    return detected


def main():
    data = read_input()
    file_path = extract_file_path(data)

    if not file_path:
        sys.exit(0)

    # JS/TS ファイル以外はスキップ
    if not is_js_ts_file(file_path):
        sys.exit(0)

    # 除外ファイルはスキップ
    if is_excluded_file(file_path):
        sys.exit(0)

    # パターン検出
    detected = detect_patterns(file_path)

    if detected:
        basename = os.path.basename(file_path)
        messages = [f"[WASM] {basename} に最適化候補を検出:"]
        for p in detected:
            messages.append(f"  - {p['name']}: {p['suggestion']} ({p['detail']})")
        messages.append(
            "[WASM] `/wasm-optimizer:suggest` で詳細な分析と before/after コードを確認できます"
        )
        print("\n".join(messages), file=sys.stderr)

    # 常に exit 0（advisory のみ）
    sys.exit(0)


if __name__ == "__main__":
    main()
