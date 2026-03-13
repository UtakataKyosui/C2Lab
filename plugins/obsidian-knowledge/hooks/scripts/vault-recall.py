#!/usr/bin/env python3
"""Auto-recall from Obsidian Vault on every user prompt.

UserPromptSubmit hook: extracts keywords from the user's prompt, searches
the Obsidian Vault via Obsidian CLI, and injects relevant notes as
additionalContext — making past knowledge surface automatically, without
the user having to ask.

Requires:
  OBSIDIAN_VAULT_NAME   Vault name (required; resolved by Obsidian CLI)

Obsidian must be running for CLI commands to succeed.
If Obsidian is unavailable, the hook exits silently (non-blocking).
"""

import json
import os
import re
import subprocess
import sys

# ── Constants ──────────────────────────────────────────────────────────────

# Maximum characters of Vault search results to inject into context.
# Keeps token usage reasonable while providing enough context.
MAX_CONTEXT_CHARS = 3000

# Number of top keywords to build the search query from.
MAX_KEYWORDS = 5

# Obsidian CLI timeout in seconds.
CLI_TIMEOUT = 10

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
}


# ── Keyword extraction ─────────────────────────────────────────────────────


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from a prompt for Vault search.

    - Splits on whitespace and punctuation
    - Lowercases English tokens; preserves CJK tokens
    - Filters stopwords and short tokens
    - Returns up to MAX_KEYWORDS in order of appearance
    """
    keywords: list[str] = []
    seen: set[str] = set()

    tokens = re.split(r"[\s\u3000、。，．「」『』【】・\\/,.:;!?()\[\]{}\"']+", text)  # noqa: RUF001

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


# ── Obsidian CLI ───────────────────────────────────────────────────────────


def get_vault_name() -> str | None:
    """Return OBSIDIAN_VAULT_NAME env var if set, else None."""
    return os.environ.get("OBSIDIAN_VAULT_NAME") or None


def search_vault(vault_name: str, query: str) -> str | None:
    """Run `obsidian search:context` and return stdout, or None on failure."""
    try:
        result = subprocess.run(  # noqa: S603
            ["obsidian", f"vault={vault_name}", "search:context", f"query={query}"],  # noqa: S607
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


# ── Context formatting ─────────────────────────────────────────────────────


def format_context(query: str, raw: str) -> str:
    """Format Vault search results as a concise context block."""
    truncated = raw[:MAX_CONTEXT_CHARS]
    if len(raw) > MAX_CONTEXT_CHARS:
        truncated += "\n... (結果を省略)"
    return (
        "<!-- obsidian-knowledge: Vault から関連ノートが自動想起されました -->\n"
        f"## Vault 想起（クエリ: {query}）\n\n"
        f"{truncated}"
    )


# ── Entry point ────────────────────────────────────────────────────────────


def main() -> None:
    try:
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError, ValueError):
            sys.exit(0)

        prompt: str = data.get("prompt", "")
        keywords = extract_keywords(prompt)
        if not keywords:
            sys.exit(0)

        vault_name = get_vault_name()
        if not vault_name:
            sys.exit(0)

        query = " ".join(keywords)
        raw = search_vault(vault_name, query)
        if not raw:
            sys.exit(0)

        context = format_context(query, raw)
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
        print(f"[vault-recall] Unexpected error: {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
