#!/usr/bin/env python3
"""Proactively surface relevant memories on each user prompt.

UserPromptSubmit hook: reads the user's prompt, searches local memory files
for relevant entries via keyword matching, and injects them as additionalContext.

Encoding Specificity is applied: memories encoded in the same project as the
current working directory receive a score bonus, matching the principle that
recall is best when retrieval context matches encoding context.
"""

import glob
import json
import re
import sys
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

MAX_RESULTS = 3
MIN_SCORE = 1

# Words to ignore in keyword extraction
STOPWORDS = {
    # English
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "to", "of", "in", "on", "at", "by", "for", "with", "about", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "from", "up", "down", "out", "off", "over", "under", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "each", "both",
    "this", "that", "these", "those", "and", "but", "or", "nor", "not",
    "no", "so", "yet", "if", "it", "its", "i", "me", "my", "we", "you",
    "your", "he", "she", "they", "them", "their", "what", "which", "who",
    "just", "more", "also", "very", "get", "use", "new", "one", "any",
    # Japanese particles / auxiliary verbs (single/double chars filtered by length)
}


# ── Keyword extraction ─────────────────────────────────────────────────────


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from a prompt.

    - Splits on whitespace and punctuation
    - Lowercases English tokens
    - Filters stopwords and short tokens (< 3 chars for ASCII, < 2 chars for CJK)
    """
    keywords: set[str] = set()

    # Split on whitespace and common punctuation
    tokens = re.split(r"[\s\u3000、。，．「」『』【】・\-\\/,.:;!?()\[\]{}\"']+", text)  # noqa: RUF001

    for token in tokens:
        if not token:
            continue

        # CJK characters: keep tokens ≥ 2 chars
        if re.search(r"[\u3040-\u9FFF\uAC00-\uD7AF]", token):
            if len(token) >= 2:
                keywords.add(token)
        else:
            lower = token.lower()
            if (
                len(lower) >= 3
                and lower not in STOPWORDS
                and re.fullmatch(r"[a-z0-9_]+", lower)
            ):
                keywords.add(lower)

    return keywords


# ── Project detection ──────────────────────────────────────────────────────


def extract_project_from_cwd(cwd: str) -> str:
    """Derive a short project name from the current working directory."""
    if not cwd:
        return "unknown"
    parts = Path(cwd).parts
    # Return the last path component (directory name)
    return parts[-1] if parts else "unknown"


def extract_project_from_memory_path(src: Path) -> str:
    """Extract project name from a memory file path.

    e.g. ~/.claude/projects/-Users-taiki-amo-Documents-C2Lab/memory/f.md → C2Lab
    """
    parts = src.parts
    for i, part in enumerate(parts):
        if part == "projects" and i + 1 < len(parts):
            project_hash = parts[i + 1]
            segments = [s for s in project_hash.split("-") if s]
            return segments[-1] if segments else project_hash
    return "unknown"


# ── Memory loading ─────────────────────────────────────────────────────────


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter into a dict (simple key: value only)."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def load_memories() -> list[dict]:
    """Load all memory files from ~/.claude/projects/*/memory/*.md"""
    pattern = str(Path.home() / ".claude" / "projects" / "*" / "memory" / "*.md")
    memories = []
    for path_str in glob.glob(pattern):
        src = Path(path_str)
        if src.name == "MEMORY.md":
            continue
        try:
            content = src.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            memories.append({
                "path": src,
                "project": extract_project_from_memory_path(src),
                "name": fm.get("name", src.stem),
                "description": fm.get("description", ""),
                "type": fm.get("type", "misc"),
                "content": content,
            })
        except OSError:
            continue
    return memories


# ── Matching & scoring ─────────────────────────────────────────────────────


def score_memory(memory: dict, keywords: set[str], current_project: str) -> int:
    """Score a memory's relevance to the current prompt.

    Scoring:
      +2 per keyword found in memory name
      +1 per keyword found in memory description
      +1 if memory's project matches current project (encoding specificity)
    """
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
    if memory["project"].lower() == current_project.lower():
        score += 1

    return score


def find_relevant_memories(
    keywords: set[str],
    memories: list[dict],
    current_project: str,
) -> list[dict]:
    """Return top-scored memories above MIN_SCORE, up to MAX_RESULTS."""
    scored = [
        (score_memory(m, keywords, current_project), m)
        for m in memories
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for score, m in scored if score >= MIN_SCORE][:MAX_RESULTS]


# ── Output formatting ──────────────────────────────────────────────────────


def format_context(matches: list[dict], current_project: str) -> str:
    """Format matched memories as a concise context block."""
    lines = [
        "<!-- obsidian-memory: 関連する過去の記憶が見つかりました -->",
        f"## 関連記憶 (プロジェクト: {current_project})\n",
    ]
    for m in matches:
        project_note = "" if m["project"] == current_project else f" _(from {m["project"]})_"  # noqa: E501
        lines.append(f"### [{m["type"]}] {m["name"]}{project_note}")
        if m["description"]:
            lines.append(f"> {m["description"]}\n")
        # Include full content (memories are small)
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

        current_project = extract_project_from_cwd(cwd)
        memories = load_memories()
        if not memories:
            print("{}")
            sys.exit(0)

        matches = find_relevant_memories(keywords, memories, current_project)
        if not matches:
            print("{}")
            sys.exit(0)

        context = format_context(matches, current_project)
        print(json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        ))
        sys.exit(0)

    except Exception as exc:
        print(f"[recall-on-prompt] Unexpected error: {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
