#!/usr/bin/env python3
"""Claude Code プラグインバリデーションスクリプト.

plugins/ 配下の全プラグインを走査し、構造・参照・フォーマットの整合性を検証する。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"

VALID_HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "UserPromptSubmit",
    "Notification",
    "Stop",
    "SubagentStart",
    "SubagentStop",
    "SessionStart",
    "SessionEnd",
    "TeammateIdle",
    "TaskCompleted",
    "PreCompact",
}

VALID_HOOK_TYPES = {"command", "prompt", "agent"}

# plugin.json のコンポーネントパスフィールド (string|array)
COMPONENT_PATH_FIELDS = {
    "commands",
    "agents",
    "skills",
    "hooks",
    "mcpServers",
    "outputStyles",
    "lspServers",
}

KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class ValidationError:
    """単一のバリデーションエラーを表す."""

    def __init__(self, plugin: str, category: str, message: str) -> None:
        self.plugin = plugin
        self.category = category
        self.message = message

    def __str__(self) -> str:
        return f"  [{self.category}] {self.message}"


class PluginValidator:
    """プラグインのバリデーションを実行する."""

    def __init__(self) -> None:
        self.errors: list[ValidationError] = []

    def error(self, plugin: str, category: str, message: str) -> None:
        self.errors.append(ValidationError(plugin, category, message))

    def validate_all(self) -> bool:
        """全プラグインとマーケットプレイスを検証し、成功なら True を返す."""
        if not PLUGINS_DIR.is_dir():
            print(f"SKIP: {PLUGINS_DIR} が見つかりません")
            return True

        plugin_dirs = sorted(
            d
            for d in PLUGINS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )

        for plugin_dir in plugin_dirs:
            self._validate_plugin(plugin_dir)

        if MARKETPLACE_PATH.exists():
            self._validate_marketplace(plugin_dirs)

        return len(self.errors) == 0

    # ── plugin.json ──────────────────────────────────────────────

    def _validate_plugin(self, plugin_dir: Path) -> None:
        name = plugin_dir.name
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"

        if not manifest_path.exists():
            self.error(name, "plugin.json", "ファイルが存在しません")
            return

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.error(name, "plugin.json", f"JSON パースエラー: {e}")
            return

        if not isinstance(manifest, dict):
            self.error(name, "plugin.json", "トップレベルがオブジェクトではありません")
            return

        # name フィールド
        plugin_name = manifest.get("name")
        if not plugin_name:
            self.error(name, "plugin.json", "name フィールドが必須です")
        elif not isinstance(plugin_name, str):
            self.error(name, "plugin.json", "name は文字列である必要があります")
        elif not KEBAB_CASE_RE.match(plugin_name):
            self.error(
                name,
                "plugin.json",
                f"name '{plugin_name}' が kebab-case ではありません "
                f"(期待: ^[a-z][a-z0-9]*(-[a-z0-9]+)*$)",
            )

        # version フィールド
        version = manifest.get("version")
        if version is not None and (
            not isinstance(version, str) or not SEMVER_RE.match(version)
        ):
            msg = f"version '{version}' が semver (X.Y.Z) ではありません"
            self.error(name, "plugin.json", msg)

        # keywords フィールド
        keywords = manifest.get("keywords")
        if keywords is not None and (
            not isinstance(keywords, list)
            or not all(isinstance(k, str) for k in keywords)
        ):
            self.error(
                name,
                "plugin.json",
                "keywords は文字列の配列である必要があります",
            )

        # コンポーネントパスフィールドの ./ 検証
        for field in COMPONENT_PATH_FIELDS:
            value = manifest.get(field)
            if value is None:
                continue
            # object (インライン設定) は hooks/mcpServers/lspServers で許可
            if isinstance(value, dict):
                continue
            paths = value if isinstance(value, list) else [value]
            for p in paths:
                if isinstance(p, str):
                    self._validate_path_ref(name, plugin_dir, field, p)

        # hooks フィールド: デフォルトパスとの重複チェック
        hooks_field = manifest.get("hooks")
        if isinstance(hooks_field, str) and (hooks_field == "./hooks/hooks.json"):
            self.error(
                name,
                "plugin.json",
                "hooks にデフォルトパス './hooks/hooks.json' "
                "が指定されています (自動検出と重複するため不要)",
            )

        # agents の .md フロントマター検証
        agents = manifest.get("agents")
        if agents is not None:
            agent_paths = agents if isinstance(agents, list) else [agents]
            for agent_path in agent_paths:
                if not isinstance(agent_path, str):
                    continue
                resolved = plugin_dir / agent_path
                if resolved.is_dir():
                    for md in sorted(resolved.glob("*.md")):
                        self._validate_agent_md(name, md)
                elif resolved.exists() and resolved.suffix == ".md":
                    self._validate_agent_md(name, resolved)

        # hooks.json 検証
        hooks_json_path = plugin_dir / "hooks" / "hooks.json"
        if hooks_json_path.exists():
            self._validate_hooks_json(name, hooks_json_path)

        # skills ディレクトリ検証
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            self._validate_skills(name, skills_dir)

        # commands .md ファイル検証
        commands = manifest.get("commands")
        if commands is not None:
            cmd_list = commands if isinstance(commands, list) else [commands]
            for cmd_path in cmd_list:
                if not isinstance(cmd_path, str):
                    continue
                resolved = plugin_dir / cmd_path
                if resolved.exists() and resolved.suffix == ".md":
                    self._validate_command_md(name, resolved)

    def _validate_path_ref(
        self, plugin: str, plugin_dir: Path, field: str, ref_path: str
    ) -> None:
        """パス参照の形式と存在を検証する."""
        if not isinstance(ref_path, str):
            self.error(plugin, field, f"パスが文字列ではありません: {ref_path}")
            return

        if ref_path.startswith("../"):
            self.error(
                plugin,
                field,
                f"パスが '../' で始まっています (禁止): {ref_path}",
            )

        if not ref_path.startswith("./"):
            self.error(
                plugin,
                field,
                f"パスが './' で始まっていません: {ref_path}",
            )

        resolved = plugin_dir / ref_path
        if not resolved.exists():
            self.error(
                plugin,
                field,
                f"参照先が存在しません: {ref_path}",
            )

    # ── hooks.json ───────────────────────────────────────────────

    def _validate_hooks_json(self, plugin: str, hooks_path: Path) -> None:
        try:
            data = json.loads(hooks_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.error(plugin, "hooks.json", f"JSON パースエラー: {e}")
            return

        if not isinstance(data, dict):
            self.error(plugin, "hooks.json", "トップレベルがオブジェクトではありません")
            return

        # "hooks" ラッパーがある場合はその中身を検証
        if "hooks" in data and isinstance(data["hooks"], dict):
            hook_events = data["hooks"]
        else:
            hook_events = data

        for event_name, event_entries in hook_events.items():
            if event_name == "hooks":
                continue

            if event_name not in VALID_HOOK_EVENTS:
                self.error(
                    plugin,
                    "hooks.json",
                    f"無効なイベントタイプ: '{event_name}' "
                    f"(有効: {', '.join(sorted(VALID_HOOK_EVENTS))})",
                )
                continue

            if not isinstance(event_entries, list):
                self.error(
                    plugin,
                    "hooks.json",
                    f"'{event_name}' の値が配列ではありません",
                )
                continue

            for i, entry in enumerate(event_entries):
                if not isinstance(entry, dict):
                    self.error(
                        plugin,
                        "hooks.json",
                        f"'{event_name}[{i}]' がオブジェクトではありません",
                    )
                    continue

                hooks_list = entry.get("hooks", [])
                if not isinstance(hooks_list, list):
                    self.error(
                        plugin,
                        "hooks.json",
                        f"'{event_name}[{i}].hooks' が配列ではありません",
                    )
                    continue

                for j, hook in enumerate(hooks_list):
                    self._validate_hook_entry(plugin, event_name, i, j, hook)

    def _validate_hook_entry(
        self, plugin: str, event: str, entry_idx: int, hook_idx: int, hook: object
    ) -> None:
        prefix = f"'{event}[{entry_idx}].hooks[{hook_idx}]'"

        if not isinstance(hook, dict):
            self.error(plugin, "hooks.json", f"{prefix} がオブジェクトではありません")
            return

        hook_type = hook.get("type")
        if hook_type is None:
            self.error(
                plugin,
                "hooks.json",
                f"{prefix} に type フィールドがありません",
            )
            return

        if hook_type not in VALID_HOOK_TYPES:
            valid = ", ".join(sorted(VALID_HOOK_TYPES))
            self.error(
                plugin,
                "hooks.json",
                f"{prefix} の type '{hook_type}' が無効です ({valid})",
            )
            return

        if hook_type == "command" and "command" not in hook:
            self.error(
                plugin,
                "hooks.json",
                f"{prefix} type=command に command がありません",
            )

        if hook_type == "prompt" and "prompt" not in hook:
            self.error(
                plugin,
                "hooks.json",
                f"{prefix} type=prompt に prompt がありません",
            )

    # ── コマンド .md ─────────────────────────────────────────────

    def _validate_command_md(self, plugin: str, md_path: Path) -> None:
        if md_path.suffix != ".md":
            self.error(
                plugin,
                "command",
                f"コマンドファイルの拡張子が .md ではありません: {md_path.name}",
            )
            return

        content = md_path.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(content)
        if frontmatter is not None:
            self._validate_yaml(plugin, "command", md_path.name, frontmatter)

    # ── エージェント .md ─────────────────────────────────────────

    def _validate_agent_md(self, plugin: str, md_path: Path) -> None:
        if md_path.suffix != ".md":
            self.error(
                plugin,
                "agent",
                f"エージェントファイルの拡張子が .md ではありません: {md_path.name}",
            )
            return

        content = md_path.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(content)
        if frontmatter is None:
            self.error(
                plugin,
                "agent",
                f"YAML フロントマターがありません: {md_path.name}",
            )
            return

        parsed = self._validate_yaml(plugin, "agent", md_path.name, frontmatter)
        if parsed is None:
            return

        if not isinstance(parsed, dict):
            self.error(
                plugin,
                "agent",
                f"フロントマターがオブジェクトではありません: {md_path.name}",
            )
            return

        if "name" not in parsed:
            self.error(
                plugin,
                "agent",
                f"フロントマターに name がありません: {md_path.name}",
            )

        if "description" not in parsed:
            self.error(
                plugin,
                "agent",
                f"フロントマターに description がありません: {md_path.name}",
            )

    # ── スキル ────────────────────────────────────────────────────

    def _validate_skills(self, plugin: str, skills_dir: Path) -> None:
        for skill_subdir in sorted(skills_dir.iterdir()):
            if not skill_subdir.is_dir() or skill_subdir.name.startswith("."):
                continue

            skill_md = skill_subdir / "SKILL.md"
            if not skill_md.exists():
                self.error(
                    plugin,
                    "skill",
                    f"SKILL.md が存在しません: skills/{skill_subdir.name}/",
                )
                continue

            content = skill_md.read_text(encoding="utf-8")
            frontmatter = self._extract_frontmatter(content)
            if frontmatter is None:
                skill_rel = f"skills/{skill_subdir.name}/SKILL.md"
                self.error(
                    plugin,
                    "skill",
                    f"YAML フロントマターがありません: {skill_rel}",
                )
                continue

            parsed = self._validate_yaml(
                plugin, "skill", f"skills/{skill_subdir.name}/SKILL.md", frontmatter
            )
            if parsed is None:
                continue

            if not isinstance(parsed, dict):
                self.error(
                    plugin,
                    "skill",
                    f"フロントマターがオブジェクトではありません: "
                    f"skills/{skill_subdir.name}/SKILL.md",
                )
                continue

            if "name" not in parsed:
                self.error(
                    plugin,
                    "skill",
                    f"フロントマターに name がありません: "
                    f"skills/{skill_subdir.name}/SKILL.md",
                )

            if "description" not in parsed:
                self.error(
                    plugin,
                    "skill",
                    f"フロントマターに description がありません: "
                    f"skills/{skill_subdir.name}/SKILL.md",
                )

    # ── marketplace.json ─────────────────────────────────────────

    def _validate_marketplace(self, plugin_dirs: list[Path]) -> None:
        try:
            data = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.error("marketplace", "marketplace.json", f"JSON パースエラー: {e}")
            return

        plugins_list = data.get("plugins", [])
        if not isinstance(plugins_list, list):
            self.error(
                "marketplace", "marketplace.json", "plugins が配列ではありません"
            )
            return

        for entry in plugins_list:
            if not isinstance(entry, dict):
                continue

            entry_name = entry.get("name", "<unknown>")
            source = entry.get("source")
            if source is None:
                self.error(
                    "marketplace",
                    "marketplace.json",
                    f"'{entry_name}' に source がありません",
                )
                continue

            source_path = REPO_ROOT / source
            if not source_path.exists():
                self.error(
                    "marketplace",
                    "marketplace.json",
                    f"'{entry_name}' の source パス '{source}' が存在しません",
                )
                continue

            manifest = source_path / ".claude-plugin" / "plugin.json"
            if not manifest.exists():
                self.error(
                    "marketplace",
                    "marketplace.json",
                    f"'{entry_name}' の source '{source}' に "
                    ".claude-plugin/plugin.json がありません",
                )

    # ── ユーティリティ ────────────────────────────────────────────

    @staticmethod
    def _extract_frontmatter(content: str) -> str | None:
        """--- で囲まれた YAML フロントマターを抽出する."""
        if not content.startswith("---"):
            return None
        end = content.find("---", 3)
        if end == -1:
            return None
        return content[3:end].strip()

    def _validate_yaml(
        self, plugin: str, category: str, filename: str, yaml_str: str
    ) -> dict | None:
        """YAML 文字列をパースし、エラーがあれば記録する.

        PyYAML が利用可能ならそちらを使い、なければ簡易チェックのみ行う。
        """
        try:
            import yaml

            parsed = yaml.safe_load(yaml_str)
            return parsed  # type: ignore[return-value]
        except ImportError:
            # PyYAML がない環境では簡易チェックのみ
            return self._simple_yaml_parse(plugin, category, filename, yaml_str)
        except Exception as e:
            self.error(plugin, category, f"YAML パースエラー ({filename}): {e}")
            return None

    @staticmethod
    def _simple_yaml_parse(
        plugin: str, category: str, filename: str, yaml_str: str
    ) -> dict | None:
        """PyYAML なしの簡易 YAML パーサー (key: value のみ対応)."""
        result: dict[str, str] = {}
        for line in yaml_str.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip().strip("\"'")
        return result if result else None


def main() -> None:
    validator = PluginValidator()
    success = validator.validate_all()

    if success:
        print("PASS: 全プラグインのバリデーションに成功しました")
    else:
        # エラーをプラグインごとにグループ化して表示
        errors_by_plugin: dict[str, list[ValidationError]] = {}
        for err in validator.errors:
            errors_by_plugin.setdefault(err.plugin, []).append(err)

        print(f"FAIL: {len(validator.errors)} 件のエラーが見つかりました\n")
        for plugin_name, errors in sorted(errors_by_plugin.items()):
            print(f"{plugin_name}:")
            for err in errors:
                print(f"  [{err.category}] {err.message}")
            print()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
