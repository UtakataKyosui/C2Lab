#!/usr/bin/env python3
"""Smoke test for plugin hook scripts.

Discovers all command-type hooks in plugins/, runs each script with minimal
mock stdin, and verifies:
  - Exit code is 0 (advisory/allow) or 2 (deny for blocking hooks)
  - stdout is empty or valid JSON

Prompt-type hooks (LLM-evaluated) and complex setup commands are skipped.

Usage:
  python3 scripts/smoke-test-hooks.py
  python3 scripts/smoke-test-hooks.py --verbose
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"
TIMEOUT_SEC = 15

# Minimal mock stdin by event type
MOCK_INPUTS: dict[str, dict] = {
    "UserPromptSubmit": {"prompt": "smoke test prompt"},
    "PostToolUse": {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/nonexistent/smoke-test.py",
            "content": "x = 1",
        },
        "tool_response": {"filePath": "/nonexistent/smoke-test.py"},
        "session_id": "smoke-test-session",
    },
    "PostToolUseFailure": {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test"},
        "error": "command failed",
        "session_id": "smoke-test-session",
    },
    "PreToolUse": {
        "tool_name": "Bash",
        "tool_input": {"command": "jj status"},
        "session_id": "smoke-test-session",
    },
    "Stop": {"session_id": "smoke-test-session", "cwd": "/nonexistent"},
    "SessionEnd": {},
    "SessionStart": {},
    "Notification": {"message": "smoke test notification"},
    "TaskCompleted": {"task_id": "smoke-test-task"},
    "SubagentStart": {},
    "SubagentStop": {},
    "TeammateIdle": {},
    "PreCompact": {},
    "PermissionRequest": {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test"},
        "session_id": "smoke-test-session",
    },
}

# Keywords that indicate a setup/install script — skip these
_SKIP_KEYWORDS = frozenset(
    ["install", "setup", "npm", "pip", "apt", "brew", "cargo install"]
)


def parse_command(command: str, plugin_root: Path) -> list[str] | None:
    """Parse a hook command into argv.

    Returns None if the command is too complex to smoke-test (setup scripts,
    pipelines, compound commands, etc.).
    """
    # Expand CLAUDE_PLUGIN_ROOT
    cmd = command.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root))
    cmd = cmd.replace('"$CLAUDE_PLUGIN_ROOT"', str(plugin_root))
    cmd = cmd.replace("$CLAUDE_PLUGIN_ROOT", str(plugin_root))

    # Skip compound/pipeline commands
    if any(op in cmd for op in ["&&", "||", "|", ";"]):
        return None

    # Skip known setup patterns
    cmd_lower = cmd.lower()
    if any(kw in cmd_lower for kw in _SKIP_KEYWORDS):
        return None

    # Parse with shlex (handles quoted paths)
    try:
        parts = shlex.split(cmd)
    except ValueError:
        return None

    if not parts:
        return None

    # Only handle python3/python/bash/sh runners
    if parts[0] not in ("python3", "python", "bash", "sh"):
        return None

    return parts


def iter_hooks(hooks_json: Path):
    """Yield (event, command_str) from a hooks.json file.

    Handles two formats:
      - Flat array: [{"event": "Stop", "type": "command", "command": "..."}]
      - Nested object: {"hooks": {"EventName": [{"hooks": [{"type": "command", ...}]}]}}
    """
    with open(hooks_json) as f:
        data = json.load(f)

    if isinstance(data, list):
        # Flat array format
        for entry in data:
            if entry.get("type") == "command" and entry.get("command"):
                yield entry.get("event", ""), entry["command"]

    elif isinstance(data, dict) and "hooks" in data:
        # Nested: {"hooks": {"EventName": [{"matcher": "", "hooks": [...]}]}}
        for event, matchers in data["hooks"].items():
            if not isinstance(matchers, list):
                continue
            for matcher_entry in matchers:
                inner_hooks = matcher_entry.get("hooks", [])
                for hook in inner_hooks:
                    if hook.get("type") == "command" and hook.get("command"):
                        yield event, hook["command"]


def validate_stdout(stdout: str) -> str | None:
    """Return an error message if stdout is non-empty and not valid JSON."""
    stripped = stdout.strip()
    if not stripped:
        return None
    try:
        json.loads(stripped)
        return None
    except json.JSONDecodeError as exc:
        return f"invalid JSON output: {exc}"


def run_smoke_test(
    argv: list[str],
    mock_input: dict,
    plugin_root: Path,
    verbose: bool,
) -> tuple[bool, str]:
    """Run a hook with mock input.

    Returns (passed: bool, detail: str).
    """
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    # Unset Obsidian/OTel env vars so external-dependency hooks exit gracefully
    for var in ("OBSIDIAN_VAULT_NAME", "OBSIDIAN_VAULT_PATH", "CLAUDE_ENV_FILE"):
        env.pop(var, None)

    stdin_data = json.dumps(mock_input)

    try:
        result = subprocess.run(  # noqa: S603
            argv,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEC,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {TIMEOUT_SEC}s"
    except Exception as exc:
        return False, f"failed to launch: {exc}"

    # Exit code: 0 = allow/advisory, 2 = deny (blocking hooks), others = error
    if result.returncode not in (0, 2):
        detail = (
            f"exit {result.returncode}\n"
            f"    stdout: {result.stdout[:300]}\n"
            f"    stderr: {result.stderr[:300]}"
        )
        return False, detail

    output_err = validate_stdout(result.stdout)
    if output_err:
        return False, f"{output_err}\n    stdout: {result.stdout[:300]}"

    if verbose:
        rc_label = f"exit {result.returncode}"
        out_snip = result.stdout.strip()[:60]
        out_label = f"  stdout={out_snip!r}" if out_snip else ""
        return True, f"{rc_label}{out_label}"

    return True, f"exit {result.returncode}"


def main() -> None:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    passed_list: list[str] = []
    failed_list: list[str] = []
    skipped_count = 0

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        hooks_json = plugin_dir / "hooks" / "hooks.json"
        if not hooks_json.exists():
            continue

        try:
            hook_entries = list(iter_hooks(hooks_json))
        except (json.JSONDecodeError, KeyError) as exc:
            failed_list.append(f"{plugin_dir.name}: failed to parse hooks.json: {exc}")
            continue

        for event, command in hook_entries:
            label = f"{plugin_dir.name}/{event}"

            argv = parse_command(command, plugin_dir)
            if argv is None:
                if verbose:
                    print(f"  SKIP  {label}  (complex command)")
                skipped_count += 1
                continue

            # Check script file exists
            script_path = next(
                (Path(p) for p in argv[1:] if p.endswith((".py", ".sh"))), None
            )
            if script_path and not script_path.exists():
                failed_list.append(f"{label}: script not found: {script_path}")
                continue

            mock_input = MOCK_INPUTS.get(event, {})
            ok, detail = run_smoke_test(argv, mock_input, plugin_dir, verbose)

            if ok:
                passed_list.append(label)
                print(f"  PASS  {label}  ({detail})")
            else:
                failed_list.append(f"{label}: {detail}")
                print(f"  FAIL  {label}  ({detail})")

    total = len(passed_list) + len(failed_list) + skipped_count
    print(
        f"\n{len(passed_list)} passed, {len(failed_list)} failed, "
        f"{skipped_count} skipped  (total {total})"
    )

    if failed_list:
        print("\nFailed:")
        for msg in failed_list:
            print(f"  • {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
