#!/usr/bin/env python3
"""Run project-specific verification commands from config."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_config_file(start_dir: Optional[str] = None) -> Optional[Path]:
    """Find .claude/review-workflow.local.md in the project."""
    search_dir = Path(start_dir) if start_dir else Path.cwd()
    current = search_dir.resolve()

    while current != current.parent:
        config = current / ".claude" / "review-workflow.local.md"
        if config.is_file():
            return config
        current = current.parent

    return None


def parse_config(config_path: Path) -> dict:
    """Parse YAML frontmatter from the config file.

    Expected format:
    ---
    verify:
      typecheck: "npx tsc --noEmit"
      test: "npm test"
      build: "docker compose build web"
    ---
    """
    content = config_path.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_content = match.group(1)

    # Simple YAML parser for our specific format (no external deps)
    config: dict = {}
    current_section = None

    for line in yaml_content.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not line.startswith(" ") and stripped.endswith(":"):
            current_section = stripped[:-1]
            config[current_section] = {}
        elif current_section and ":" in stripped:
            key, _, value = stripped.partition(":")
            value = value.strip().strip('"').strip("'")
            config[current_section][key.strip()] = value

    return config


def run_verification(commands: dict[str, str], cwd: str) -> dict:
    """Run verification commands and collect results."""
    results = {
        "total": len(commands),
        "passed": 0,
        "failed": 0,
        "steps": [],
    }

    for name, cmd in commands.items():
        # Security note: commands come from the user's local config file
        # (.claude/review-workflow.local.md). This is trusted user input.
        print(f"Running: {name} ({cmd})...", file=sys.stderr)

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            step = {
                "name": name,
                "command": cmd,
                "success": False,
                "returncode": -1,
                "stderr": f"Command timed out after 300 seconds",
            }
            results["failed"] += 1
            results["steps"].append(step)
            continue

        step = {
            "name": name,
            "command": cmd,
            "success": result.returncode == 0,
            "returncode": result.returncode,
        }

        if result.returncode != 0:
            # Include last 30 lines of output for debugging
            stderr_lines = result.stderr.strip().split("\n")[-30:]
            stdout_lines = result.stdout.strip().split("\n")[-30:]
            step["stderr"] = "\n".join(stderr_lines)
            step["stdout"] = "\n".join(stdout_lines)
            results["failed"] += 1
        else:
            results["passed"] += 1

        results["steps"].append(step)

    results["all_passed"] = results["failed"] == 0
    return results


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None

    config_path = find_config_file(project_dir)
    if not config_path:
        print(json.dumps({
            "error": "Config file not found",
            "hint": "Create .claude/review-workflow.local.md with verify commands",
            "example": "---\nverify:\n  typecheck: \"npx tsc --noEmit\"\n  test: \"npm test\"\n---",
        }, indent=2))
        sys.exit(1)

    config = parse_config(config_path)
    verify_commands = config.get("verify", {})

    if not verify_commands:
        print(json.dumps({
            "warning": "No verify commands found in config",
            "config_path": str(config_path),
            "all_passed": True,
            "steps": [],
        }, indent=2))
        sys.exit(0)

    cwd = str(config_path.parent.parent)  # .claude/ -> project root
    results = run_verification(verify_commands, cwd)
    results["config_path"] = str(config_path)

    print(json.dumps(results, indent=2, ensure_ascii=False))

    if not results["all_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
