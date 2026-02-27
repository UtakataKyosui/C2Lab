#!/usr/bin/env python3
import json
import pathlib
import sys

# Rustプロジェクト以外ではスキップ
if not pathlib.Path("Cargo.toml").exists():
    sys.exit(0)

try:
    import mistune
except ImportError:
    sys.exit(0)


# ---------------------------------------
# Markdown 判定関数（mistune で AST を生成 → エラーが出なければ Markdown とみなす）
# ---------------------------------------
def is_markdown(text: str) -> bool:
    try:
        markdown = mistune.create_markdown(renderer="ast")
        ast = markdown(text)
        # AST が空でも Markdown とみなす（Markdown 仕様では空文書も有効）
        return isinstance(ast, list)
    except Exception:
        return False


# ---------------------------------------
# Hook 入口
# ---------------------------------------
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": f"入力がJSONとして読み取れませんでした: {e}",
            }
        )
    )
    sys.exit(0)

prompt = input_data.get("prompt", "")

# ---------------------------------------
# Markdown チェック
# ---------------------------------------
if not is_markdown(prompt):
    # Markdown ではない → block
    output = {
        "decision": "block",
        "reason": "入力がMarkdown形式ではありませんでした。Markdownで記述してください。",
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)

# ---------------------------------------
# 通常進行（Markdown と判断）
# additionalContext を付与して allow
# ---------------------------------------
output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "Markdown 形式を確認しました。続行します。",
    }
}

print(json.dumps(output, ensure_ascii=False))
sys.exit(0)
