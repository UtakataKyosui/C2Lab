#!/usr/bin/env python3
"""Sync Claude memory files to Obsidian Vault via Obsidian CLI.

Usage:
  python3 sync-memory.py           # PostToolUse mode: reads tool input from stdin
  python3 sync-memory.py --all     # SessionEnd mode: syncs all memory files

Required env:
  OBSIDIAN_VAULT_NAME   Vault name (preferred; uses CLI to resolve path)
  OBSIDIAN_VAULT_PATH   Vault root path (fallback if CLI unavailable)

Encoding Specificity:
  Memory files are copied to Obsidian with additional context fields injected
  into their frontmatter (context_project, context_synced_at, context_tags).
  These fields enable context-aware retrieval — searching with the same project
  context in which a memory was encoded improves recall precision.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import datetime
from pathlib import Path

# Allowlist for mem_type directory names to prevent path traversal
_ALLOWED_TYPES = frozenset({"user", "feedback", "project", "reference", "misc"})

# ── Vault path resolution ──────────────────────────────────────────────────


def resolve_vault_path() -> Path | None:
    """Resolve vault root path via CLI (preferred) or env var (fallback)."""
    vault_name = os.environ.get("OBSIDIAN_VAULT_NAME", "")
    if vault_name:
        path = _vault_path_from_cli(vault_name)
        if path:
            return path

    vault_path = os.environ.get("OBSIDIAN_VAULT_PATH", "")
    if vault_path:
        return Path(vault_path).expanduser().resolve()

    return None


def _vault_path_from_cli(vault_name: str) -> Path | None:
    """Run `obsidian vault=<name> vault info=path` and return the path."""
    try:
        result = subprocess.run(  # noqa: S603
            ["obsidian", f"vault={vault_name}", "vault", "info=path"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=15,
        )
        path = result.stdout.strip()
        if result.returncode == 0 and path:
            return Path(path)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


# ── Frontmatter helpers ────────────────────────────────────────────────────


def parse_frontmatter_type(content: str) -> str:
    """Extract 'type' field from YAML frontmatter, validated against allowlist."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return "misc"
    for line in match.group(1).splitlines():
        if line.startswith("type:"):
            raw = line.split(":", 1)[1].strip()
            # Sanitize: only return known types to prevent path traversal
            return raw if raw in _ALLOWED_TYPES else "misc"
    return "misc"


def extract_project_from_path(src: Path) -> str:
    """Extract project name from memory file path.

    e.g. ~/.claude/projects/-Users-taiki-amo-Documents-C2Lab/memory/f.md → C2Lab
    The project directory name is the absolute path with '/' replaced by '-'.
    """
    parts = src.parts
    for i, part in enumerate(parts):
        if part == "projects" and i + 1 < len(parts):
            project_hash = parts[i + 1]
            segments = [s for s in project_hash.split("-") if s]
            return segments[-1] if segments else project_hash
    return "unknown"


def inject_encoding_context(content: str, src: Path) -> str:
    """Inject encoding context fields into the frontmatter of the Obsidian copy.

    Adds:
      context_project:   project name derived from the memory file path
      context_synced_at: ISO 8601 UTC timestamp of this sync
      context_tags:      list form of project (enables Obsidian tag filtering)

    These fields are injected only into the destination copy; the original
    memory file is never modified.
    """
    project = extract_project_from_path(src)
    synced_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ctx = (
        f"context_project: {project}\n"
        f"context_synced_at: {synced_at}\n"
        f"context_tags:\n  - {project}\n"
    )

    match = re.match(r"^(---\n)(.*?)(\n---\n?)", content, re.DOTALL)
    if match:
        before, body, closing = match.group(1), match.group(2), match.group(3)
        rest = content[match.end():]
        return before + body + "\n" + ctx + closing + rest
    else:
        return f"---\n{ctx}---\n{content}"


# ── Sync logic ─────────────────────────────────────────────────────────────


def sync_file(src: Path, vault_path: Path) -> None:
    """Sync a single memory file to Obsidian Vault.

    Reads the file exactly once; for MEMORY.md copies as-is,
    for typed memory files injects encoding context into the copy.
    """
    if src.name == "MEMORY.md":
        dest = vault_path / "Claude-Memory" / "MEMORY.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    else:
        content = src.read_text(encoding="utf-8")
        mem_type = parse_frontmatter_type(content)  # sanitized, safe for path
        dest = vault_path / "Claude-Memory" / mem_type / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        enriched = inject_encoding_context(content, src)
        dest.write_text(enriched, encoding="utf-8")
        # Preserve original timestamps
        st = src.stat()
        os.utime(dest, (st.st_atime, st.st_mtime))


def sync_all(vault_path: Path) -> int:
    pattern = str(Path.home() / ".claude" / "projects" / "*" / "memory" / "*.md")
    files = glob.glob(pattern)
    for f in files:
        sync_file(Path(f), vault_path)
    return len(files)


def _validate_memory_path(file_path: str) -> Path | None:
    """Validate that file_path is a .md file under ~/.claude/projects/*/memory/.

    Returns the resolved Path if valid, None otherwise.
    Prevents path traversal attacks via crafted file_path values.
    """
    if not file_path:
        return None

    try:
        src = Path(file_path).expanduser().resolve()
    except (OSError, RuntimeError):
        return None

    if src.suffix.lower() != ".md":
        return None

    projects_root = (Path.home() / ".claude" / "projects").resolve()
    if not str(src).startswith(str(projects_root) + os.sep):
        return None

    # Enforce ~/.claude/projects/<project>/memory/<file>.md structure
    parts = src.parts
    try:
        projects_idx = parts.index("projects")
    except ValueError:
        return None

    if len(parts) <= projects_idx + 2 or parts[projects_idx + 2] != "memory":
        return None

    return src if src.exists() else None


# ── Entry point ────────────────────────────────────────────────────────────


def main() -> None:
    try:
        vault_path = resolve_vault_path()
        if vault_path is None:
            sys.exit(0)

        if "--all" in sys.argv:
            count = sync_all(vault_path)
            if count:
                print(
                    f"[obsidian-memory] Synced {count} memory file(s) → {vault_path}/Claude-Memory",  # noqa: E501
                    file=sys.stderr,
                )
            sys.exit(0)

        # PostToolUse mode: parse stdin
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError, ValueError):
            sys.exit(0)

        # Skip if tool_name is present and is not "Write".
        # If tool_name is absent, fall through and check tool_input instead.
        tool_name = data.get("tool_name")
        if tool_name is not None and tool_name != "Write":
            sys.exit(0)

        tool_input = data.get("tool_input")
        if not isinstance(tool_input, dict):
            sys.exit(0)

        src = _validate_memory_path(tool_input.get("file_path", ""))
        if src is None:
            sys.exit(0)

        sync_file(src, vault_path)
        print(f"[obsidian-memory] Synced {src.name} → Obsidian", file=sys.stderr)
        sys.exit(0)

    except Exception as exc:
        print(f"[obsidian-memory] Non-fatal error during sync: {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
