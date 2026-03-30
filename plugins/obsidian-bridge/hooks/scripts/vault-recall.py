#!/usr/bin/env python3
"""Unified recall: Obsidian Vault search with local memory fallback.

UserPromptSubmit hook that unifies obsidian-memory and obsidian-knowledge:
  1. Searches Obsidian Vault with encoding specificity (project-filtered query).
     The Vault contains both synced Claude memories and manually captured notes,
     so a single Vault search covers all long-term knowledge.
  2. Falls back to full Vault search if the project-filtered query yields nothing.
  3. Falls back to local ~/.claude memory files if Obsidian is unavailable.

Requires:
  OBSIDIAN_VAULT_NAME   Vault name (resolved by Obsidian CLI)
"""

import glob
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

MAX_RESULTS = 3
MIN_SCORE = 1
MAX_CONTEXT_CHARS = 3000
MAX_KEYWORDS = 5
CLI_TIMEOUT = 10

STOPWORDS = {
    # English
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "about",
    "as",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "from",
    "up",
    "down",
    "out",
    "off",
    "over",
    "under",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "each",
    "both",
    "this",
    "that",
    "these",
    "those",
    "and",
    "but",
    "or",
    "nor",
    "not",
    "no",
    "so",
    "yet",
    "if",
    "it",
    "its",
    "i",
    "me",
    "my",
    "we",
    "you",
    "your",
    "he",
    "she",
    "they",
    "them",
    "their",
    "what",
    "which",
    "who",
    "just",
    "more",
    "also",
    "very",
    "get",
    "use",
    "new",
    "one",
    "any",
    # Japanese particles / auxiliary verbs (single/double chars filtered by length)
}


# ── Keyword extraction ─────────────────────────────────────────────────────


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from a prompt. Returns up to MAX_KEYWORDS."""
    keywords: list[str] = []
    seen: set[str] = set()

    tokens = re.split(r"[\s\u3000、。，．「」『』【】・\\/,.:;!?()[\]{}\"']+", text)

    for token in tokens:
        if not token:
            continue

        # CJK: keep tokens ≥ 2 chars
        if re.search(r"[\u3040-\u9FFF\uAC00-\uD7AF]", token):
            if len(token) >= 2 and token not in seen:
                keywords.append(token)
                seen.add(token)
        else:
            lower = token.lower()
            if (
                len(lower) >= 3
                and lower not in STOPWORDS
                and re.fullmatch(r"[a-z0-9_\-]+", lower)
                and lower not in seen
            ):
                keywords.append(lower)
                seen.add(lower)

        if len(keywords) >= MAX_KEYWORDS:
            break

    return keywords


# ── Project detection ──────────────────────────────────────────────────────


def extract_project_from_cwd(cwd: str) -> str:
    """Derive a short project name from the current working directory."""
    if not cwd:
        return ""
    parts = Path(cwd).parts
    return parts[-1] if parts else ""


# ── Vault search ───────────────────────────────────────────────────────────


def _run_vault_search(vault_name: str, query: str) -> str | None:
    """Run `obsidian search:context` and return stdout, or None on failure."""
    try:
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "obsidian",
                f"vault={vault_name}",
                "search:context",
                f"query={shlex.quote(query)}",
            ],
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
        )
        output = result.stdout.strip()
        if result.returncode == 0 and output:
            return output
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def recall_from_vault(vault_name: str, keywords: list[str], project: str) -> str | None:
    """Search Vault with encoding specificity, falling back to full search."""
    keyword_str = " ".join(keywords)

    # Primary: project-filtered search (encoding specificity)
    # Synced memories carry context_project frontmatter, enabling precise recall
    if project:
        filtered_query = f"[context_project:{project}] {keyword_str}"
        raw = _run_vault_search(vault_name, filtered_query)
        if raw:
            return _format_vault_context(filtered_query, raw, project)

    # Fallback: full Vault search (cross-project + manual knowledge)
    raw = _run_vault_search(vault_name, keyword_str)
    if raw:
        return _format_vault_context(keyword_str, raw, project)

    return None


def _format_vault_context(query: str, raw: str, project: str) -> str:
    """Format Vault search results as a context block."""
    truncated = raw[:MAX_CONTEXT_CHARS]
    if len(raw) > MAX_CONTEXT_CHARS:
        truncated += "\n... (結果を省略)"
    project_note = f" (プロジェクト: {project})" if project else ""
    header = f"<!-- obsidian-bridge: Vault から関連ノートが自動想起されました{project_note} -->"
    return f"{header}\n## Vault 想起（クエリ: {query}）\n\n{truncated}"


# ── Local memory fallback ──────────────────────────────────────────────────


def _parse_frontmatter(content: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def _extract_project_from_memory_path(src: Path) -> str:
    parts = src.parts
    for i, part in enumerate(parts):
        if part == "projects" and i + 1 < len(parts):
            project_hash = parts[i + 1]
            segments = [s for s in project_hash.split("-") if s]
            return segments[-1] if segments else project_hash
    return "unknown"


def _load_memories() -> list[dict]:
    pattern = str(Path.home() / ".claude" / "projects" / "*" / "memory" / "*.md")
    memories = []
    for path_str in glob.glob(pattern):
        src = Path(path_str)
        if src.name == "MEMORY.md":
            continue
        try:
            content = src.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            memories.append(
                {
                    "path": src,
                    "project": _extract_project_from_memory_path(src),
                    "name": fm.get("name", src.stem),
                    "description": fm.get("description", ""),
                    "type": fm.get("type", "misc"),
                    "content": content,
                }
            )
        except OSError:
            continue
    return memories


def _score_memory(memory: dict, keywords: list[str], current_project: str) -> int:
    score = 0
    name_lower = memory["name"].lower()
    desc_lower = memory["description"].lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in name_lower:
            score += 2
        elif kw_lower in desc_lower:
            score += 1
    # Encoding specificity bonus
    if current_project and memory["project"].lower() == current_project.lower():
        score += 1
    return score


def recall_from_local(keywords: list[str], project: str) -> str | None:
    """Search local Claude memory files when Obsidian is unavailable."""
    memories = _load_memories()
    if not memories:
        return None

    scored = [(_score_memory(m, keywords, project), m) for m in memories]
    scored.sort(key=lambda x: x[0], reverse=True)
    matches = [m for score, m in scored if score >= MIN_SCORE][:MAX_RESULTS]
    if not matches:
        return None

    project_label = project or "unknown"
    lines = [
        f"<!-- obsidian-bridge: ローカルメモリから関連記憶が見つかりました (プロジェクト: {project_label}) -->",
        f"## 関連記憶 (プロジェクト: {project_label})\n",
    ]
    for m in matches:
        project_note = "" if m["project"] == project else f" _(from {m['project']})_"
        lines.append(f"### [{m['type']}] {m['name']}{project_note}")
        if m["description"]:
            lines.append(f"> {m['description']}\n")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────


def main() -> None:
    try:
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError, ValueError):
            sys.exit(0)

        prompt: str = data.get("prompt", "")
        cwd: str = data.get("cwd", "")

        keywords = extract_keywords(prompt)
        if not keywords:
            print("{}")
            sys.exit(0)

        project = extract_project_from_cwd(cwd)
        vault_name = os.environ.get("OBSIDIAN_VAULT_NAME") or None

        context: str | None = None

        if vault_name:
            context = recall_from_vault(vault_name, keywords, project)
        else:
            # No Obsidian vault configured — fall back to local memory files
            context = recall_from_local(keywords, project)

        if not context:
            print("{}")
            sys.exit(0)

        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": context,
                    }
                },
                ensure_ascii=False,
            )
        )
        sys.exit(0)

    except Exception as exc:
        print(
            f"[obsidian-bridge] Unexpected error in vault-recall: {exc}",
            file=sys.stderr,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
