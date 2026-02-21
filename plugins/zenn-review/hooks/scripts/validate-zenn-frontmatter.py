# ruff: noqa: E501, SIM102, SIM114
#!/usr/bin/env python3
"""
PostToolUse hook: Zenn フロントマター / config.yaml バリデーション(Advisory のみ)

Write/Edit ツール使用後に実行され、以下を検証する:
- articles/*.md: フロントマターの必須フィールドと値の妥当性
- books/*/config.yaml: 書籍設定の必須フィールドと値の妥当性

- 対象外のファイルはスキップ
- stdlib のみ使用(外部依存なし)
- 常に exit 0(advisory のみ、ブロックしない)
"""

import json
import os
import re
import sys

MAX_FILE_SIZE = 512 * 1024  # 512KB


def read_input():
    """stdin から PostToolUse の JSON データを読み取る"""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError, OSError, UnicodeDecodeError):
        return None


def extract_file_path(data):
    """ツール実行データからファイルパスを抽出する"""
    if not data:
        return None
    tool_input = data.get("tool_input", {})
    return tool_input.get("file_path")


def is_target_file(file_path):
    """Zenn コンテンツファイルかどうか判定する"""
    normalized = file_path.replace("\\", "/")
    # 先頭の "./" を許容しつつ、ルート直下の articles/ / books/ に限定
    if normalized.startswith("./"):
        normalized = normalized[2:]

    # articles/*.md
    if normalized.startswith("articles/"):
        return normalized.endswith(".md")

    # books/*/config.yaml および books/*/*.md
    if normalized.startswith("books/"):
        parts = normalized.split("/")
        # ["books", "<book-slug>", "<file>"] 以上を要求
        if len(parts) >= 3:
            filename = parts[-1]
            if filename == "config.yaml":
                return True
            if filename.endswith(".md"):
                return True
    return False


def get_file_type(file_path):
    """ファイルの種別を判定する"""
    normalized = file_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]

    if normalized.startswith("articles/"):
        if normalized.endswith(".md"):
            return "article"
        return None

    if normalized.startswith("books/"):
        parts = normalized.split("/")
        if len(parts) >= 3:
            filename = parts[-1]
            if filename == "config.yaml":
                return "book_config"
            if filename.endswith(".md"):
                return "book_chapter"
    return None


def check_file_safety(file_path):
    """ファイルのサイズとパスを検証する"""
    normalized = os.path.normpath(file_path)
    if ".." in normalized.split(os.sep):
        return False, "パストラバーサルが検出されました"

    real_path = os.path.realpath(file_path)
    project_root = os.path.realpath(os.getcwd())
    if not real_path.startswith(project_root):
        return False, "プロジェクト外のパスが検出されました"

    if not os.path.isfile(real_path):
        return False, f"ファイルが存在しません: {file_path}"

    file_size = os.path.getsize(real_path)
    if file_size > MAX_FILE_SIZE:
        return False, f"ファイルサイズが上限(512KB)を超えています: {file_size} bytes"

    return True, None


def parse_frontmatter(content):
    """Markdown ファイルからフロントマターを正規表現で解析する"""
    # 改行を正規化してからフロントマターを解析する(\r\n / \r -> \n)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    # 末尾が EOF の場合もマッチするように、終了 --- の後は改行または文字列終端を許可する
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", normalized, re.DOTALL)
    if not match:
        return None
    fm_text = match.group(1)
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kv_match = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if " #" in value and not (
                (value.startswith('"') and value.endswith('"') and value.count('"') <= 2) or
                (value.startswith("'") and value.endswith("'") and value.count("'") <= 2)
            ):
                value = value.split(" #", 1)[0].strip()
            # 配列の簡易パース
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                if inner:
                    items = [
                        item.strip().strip("\"'")
                        for item in inner.split(",")
                    ]
                    result[key] = items
                else:
                    result[key] = []
            elif value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            elif value.startswith('"') and value.endswith('"'):
                result[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                result[key] = value[1:-1]
            else:
                result[key] = value
    return result


def parse_yaml_simple(content):
    """config.yaml を正規表現で簡易パースする(PyYAML 不要)"""
    result = {}
    current_list_key = None
    current_list = []
    for line in content.split("\n"):
        # リスト項目
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_list_key:
            current_list.append(list_match.group(1).strip().strip("\"'"))
            continue
        # 前のリストを保存
        if current_list_key and current_list:
            result[current_list_key] = current_list
            current_list_key = None
            current_list = []
        # キー: 値
        kv_match = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if " #" in value and not (
                (value.startswith('"') and value.endswith('"') and value.count('"') <= 2) or
                (value.startswith("'") and value.endswith("'") and value.count("'") <= 2)
            ):
                value = value.split(" #", 1)[0].strip()
            if not value:
                # 次の行がリスト項目かもしれない
                current_list_key = key
                current_list = []
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                if inner:
                    items = [
                        item.strip().strip("\"'")
                        for item in inner.split(",")
                    ]
                    result[key] = items
                else:
                    result[key] = []
            elif value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            elif re.match(r"^\d+$", value):
                result[key] = int(value)
            elif value.startswith('"') and value.endswith('"'):
                result[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                result[key] = value[1:-1]
            else:
                result[key] = value
    # 最後のリストを保存
    if current_list_key and current_list:
        result[current_list_key] = current_list
    return result


def validate_article_frontmatter(file_path, content):
    """記事フロントマターを検証する"""
    errors = []
    warnings = []

    fm = parse_frontmatter(content)
    if fm is None:
        errors.append("フロントマターが見つかりません(--- で囲まれた YAML ブロックが必要)")
        return errors, warnings

    # 必須フィールドチェック
    required = ["title", "emoji", "type", "topics", "published"]
    for field in required:
        if field not in fm:
            errors.append(f"必須フィールド `{field}` がありません")

    # title チェック
    if "title" in fm:
        title = str(fm["title"])
        if not title:
            errors.append("`title` が空です")
        elif len(title) > 70:
            warnings.append(f"`title` が {len(title)} 文字です(70文字以内推奨)")

    # emoji チェック(必須: 絵文字)
    if "emoji" in fm:
        emoji_value = fm["emoji"]
        if not isinstance(emoji_value, str):
            errors.append("`emoji` が文字列ではありません(絵文字を指定してください)")
        elif not emoji_value.strip():
            errors.append("`emoji` が空です(絵文字を指定してください)")

    # published チェック(必須: boolean)
    if "published" in fm:
        if not isinstance(fm["published"], bool):
            errors.append("`published` が boolean ではありません(true / false を指定してください)")

    # type チェック
    if "type" in fm:
        if fm["type"] not in ("tech", "idea"):
            errors.append(f"`type` が不正です: \"{fm['type']}\"(\"tech\" または \"idea\" のみ)")

    # topics チェック
    if "topics" in fm:
        topics = fm["topics"]
        if not isinstance(topics, list):
            errors.append("`topics` が配列ではありません")
        elif len(topics) == 0:
            errors.append("`topics` が空です(1〜5個必要)")
        elif len(topics) > 5:
            errors.append(f"`topics` が {len(topics)} 個あります(最大5個)")
        else:
            for topic in topics:
                if not re.match(r"^[a-z0-9][a-z0-9-]*$", str(topic)):
                    errors.append(
                        f"`topics` の値 \"{topic}\" が不正です(小文字英数字・ハイフンのみ)"
                    )

    # スラッグチェック
    slug = os.path.splitext(os.path.basename(file_path))[0]
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", slug):
        warnings.append(f"スラッグ \"{slug}\" に使用不可の文字が含まれています")
    elif len(slug) < 12 or len(slug) > 50:
        warnings.append(
            f"スラッグ \"{slug}\" の長さが {len(slug)} 文字です(12〜50文字推奨)"
        )

    return errors, warnings


def validate_book_config(content):
    """書籍 config.yaml を検証する"""
    errors = []
    warnings = []

    config = parse_yaml_simple(content)
    if not config:
        errors.append("config.yaml のパースに失敗しました")
        return errors, warnings

    # 必須フィールドチェック
    required = ["title", "summary", "topics", "published", "price"]
    for field in required:
        if field not in config:
            errors.append(f"必須フィールド `{field}` がありません")

    # title チェック
    if "title" in config and not str(config["title"]):
        errors.append("`title` が空です")

    # summary チェック
    if "summary" in config:
        summary = str(config["summary"])
        if len(summary) > 200:
            warnings.append(
                f"`summary` が {len(summary)} 文字です(200文字以内推奨)"
            )

    # published チェック(必須: boolean)
    if "published" in config:
        if not isinstance(config["published"], bool):
            errors.append("`published` が boolean ではありません(true / false を指定してください)")

    # topics チェック
    if "topics" in config:
        topics = config["topics"]
        if not isinstance(topics, list):
            errors.append("`topics` が配列ではありません")
        elif len(topics) == 0:
            errors.append("`topics` が空です(1〜5個必要)")
        elif len(topics) > 5:
            errors.append(f"`topics` が {len(topics)} 個あります(最大5個)")
        else:
            for topic in topics:
                if not re.match(r"^[a-z0-9][a-z0-9-]*$", str(topic)):
                    errors.append(
                        f"`topics` の値 \"{topic}\" が不正です(小文字英数字・ハイフンのみ)"
                    )

    # price チェック
    if "price" in config:
        price = config["price"]
        if not isinstance(price, int):
            errors.append("`price` が整数ではありません")
        elif price != 0 and (price < 200 or price > 5000 or price % 100 != 0):
            errors.append(
                f"`price` が不正です: {price}(0 または 200〜5000 の100円単位)"
            )

    return errors, warnings


def validate_chapter_frontmatter(content):
    """チャプターファイルのフロントマターを検証する"""
    errors = []
    fm = parse_frontmatter(content)
    if fm is None:
        errors.append("フロントマターが見つかりません")
        return errors
    if "title" not in fm or not str(fm.get("title", "")):
        errors.append("チャプターの `title` がありません")
    return errors


def main():
    try:
        data = read_input()
        file_path = extract_file_path(data)

        if not file_path:
            sys.exit(0)

        # 対象外のファイルはスキップ
        if not is_target_file(file_path):
            sys.exit(0)

        # ファイル安全性チェック
        is_safe, error_msg = check_file_safety(file_path)
        if not is_safe:
            print(f"[Zenn validate] スキップ: {error_msg}", file=sys.stderr)
            sys.exit(0)

        file_type = get_file_type(file_path)
        if not file_type:
            sys.exit(0)

        # ファイル読み込み
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"[Zenn validate] ファイル読み込みエラー: {e}", file=sys.stderr)
            sys.exit(0)

        errors = []
        warnings = []
        basename = os.path.basename(file_path)

        if file_type == "article":
            errors, warnings = validate_article_frontmatter(file_path, content)
        elif file_type == "book_config":
            errors, warnings = validate_book_config(content)
        elif file_type == "book_chapter":
            errors = validate_chapter_frontmatter(content)

        # 結果出力
        if errors:
            msg_parts = [f"[Zenn validate] ⚠ {basename} にエラーがあります:"]
            for err in errors:
                msg_parts.append(f"  ERROR: {err}")
            for warn in warnings:
                msg_parts.append(f"  WARNING: {warn}")
            msg_parts.append(
                "\n  詳細な検証は `/zenn-review:frontmatter-check` コマンドを使用してください。"
            )
            print("\n".join(msg_parts), file=sys.stderr)
        elif warnings:
            msg_parts = [f"[Zenn validate] {basename} に警告があります:"]
            for warn in warnings:
                msg_parts.append(f"  WARNING: {warn}")
            print("\n".join(msg_parts), file=sys.stderr)
        else:
            print(f"[Zenn validate] ✓ {basename} のフロントマター検証に問題はありません。")

        sys.exit(0)
    except Exception as e:
        print(f"[Zenn validate] 予期しないエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
