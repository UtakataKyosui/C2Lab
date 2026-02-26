#!/usr/bin/env python3
"""Fetch PR review comments via gh CLI."""

import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass


@dataclass
class ReviewComment:
    id: int
    author: str
    body: str
    path: str | None
    line: int | None
    diff_hunk: str | None
    state: str | None
    created_at: str
    in_reply_to_id: int | None = None


@dataclass
class ReviewThread:
    """A group of review comments forming a conversation thread."""
    thread_id: int
    path: str | None
    line: int | None
    comments: list[ReviewComment]
    resolved: bool = False


def parse_pr_reference(pr_ref: str) -> tuple[str | None, str]:
    """Parse PR reference into (repo, pr_number).

    Accepts:
      - Full URL: https://github.com/owner/repo/pull/123
      - Short reference: 123
      - Repo + number: owner/repo#123
    """
    # Full URL
    url_match = re.match(r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)", pr_ref)
    if url_match:
        return url_match.group(1), url_match.group(2)

    # owner/repo#number
    short_match = re.match(r"([^/]+/[^#]+)#(\d+)", pr_ref)
    if short_match:
        return short_match.group(1), short_match.group(2)

    # Just a number
    if pr_ref.strip().isdigit():
        return None, pr_ref.strip()

    print(json.dumps({"error": f"Cannot parse PR reference: {pr_ref}"}))
    sys.exit(1)


def fetch_pr_info(repo: str | None, pr_number: str) -> dict:
    """Fetch basic PR information."""
    cmd = ["gh", "pr", "view", pr_number, "--json",
           "number,title,state,headRefName,baseRefName,author,url"]
    if repo:
        cmd.extend(["--repo", repo])

    result = subprocess.run(  # noqa: S603
        cmd, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        err = f"Failed to fetch PR info: {result.stderr}"
        print(json.dumps({"error": err}))
        sys.exit(1)

    return json.loads(result.stdout)


def _detect_repo() -> str | None:
    """Detect repo name from current directory via gh CLI."""
    detect_result = subprocess.run(
        ["gh", "repo", "view", "--json",  # noqa: S607
         "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True, text=True, check=False,
    )
    if detect_result.returncode != 0:
        return None
    return detect_result.stdout.strip()


def fetch_review_comments(repo: str | None, pr_number: str) -> list[ReviewComment]:
    """Fetch all review comments on a PR."""
    # Fetch review comments (inline comments on code)
    cmd = ["gh", "api"]
    if repo:
        cmd.append(f"repos/{repo}/pulls/{pr_number}/comments")
    else:
        detected_repo = _detect_repo()
        if not detected_repo:
            msg = "Cannot detect repository. Specify full PR URL."
            print(json.dumps({"error": msg}))
            sys.exit(1)
        cmd.append(
            f"repos/{detected_repo}/pulls/{pr_number}/comments",
        )

    cmd.extend(["--paginate"])

    result = subprocess.run(  # noqa: S603
        cmd, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []

    raw_comments = json.loads(result.stdout)
    comments = []
    for c in raw_comments:
        comments.append(ReviewComment(
            id=c["id"],
            author=c.get("user", {}).get("login", "unknown"),
            body=c.get("body", ""),
            path=c.get("path"),
            line=c.get("original_line") or c.get("line"),
            diff_hunk=c.get("diff_hunk"),
            state=c.get("state"),
            created_at=c.get("created_at", ""),
            in_reply_to_id=c.get("in_reply_to_id"),
        ))

    return comments


def fetch_review_bodies(repo: str | None, pr_number: str) -> list[ReviewComment]:
    """Fetch top-level review bodies (not inline comments)."""
    cmd = ["gh", "api"]
    if repo:
        cmd.append(f"repos/{repo}/pulls/{pr_number}/reviews")
    else:
        detected_repo = _detect_repo()
        if not detected_repo:
            return []
        cmd.append(
            f"repos/{detected_repo}/pulls/{pr_number}/reviews",
        )

    result = subprocess.run(  # noqa: S603
        cmd, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []

    raw_reviews = json.loads(result.stdout)
    comments = []
    for r in raw_reviews:
        body = r.get("body", "").strip()
        if body:
            comments.append(ReviewComment(
                id=r["id"],
                author=r.get("user", {}).get("login", "unknown"),
                body=body,
                path=None,
                line=None,
                diff_hunk=None,
                state=r.get("state"),
                created_at=r.get("submitted_at", ""),
            ))

    return comments


def group_into_threads(comments: list[ReviewComment]) -> list[ReviewThread]:
    """Group inline comments into conversation threads."""
    threads: dict[int, ReviewThread] = {}
    reply_map: dict[int, int] = {}

    for c in comments:
        if c.in_reply_to_id:
            reply_map[c.id] = c.in_reply_to_id

    # Find root comment for each reply chain
    def find_root(comment_id: int) -> int:
        visited = set()
        current = comment_id
        while current in reply_map and current not in visited:
            visited.add(current)
            current = reply_map[current]
        return current

    for c in comments:
        root_id = find_root(c.id)
        if root_id not in threads:
            root_comment = next((x for x in comments if x.id == root_id), c)
            threads[root_id] = ReviewThread(
                thread_id=root_id,
                path=root_comment.path,
                line=root_comment.line,
                comments=[],
            )
        threads[root_id].comments.append(c)

    # Sort comments within each thread by creation time
    for thread in threads.values():
        thread.comments.sort(key=lambda x: x.created_at)

    return list(threads.values())


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: review_fetcher.py <PR_URL_or_number>"}))
        sys.exit(1)

    pr_ref = sys.argv[1]
    repo, pr_number = parse_pr_reference(pr_ref)

    # Fetch PR info
    pr_info = fetch_pr_info(repo, pr_number)

    # Fetch all comments
    inline_comments = fetch_review_comments(repo, pr_number)
    review_bodies = fetch_review_bodies(repo, pr_number)

    # Group inline comments into threads
    threads = group_into_threads(inline_comments)

    # Build output
    output = {
        "pr": {
            "number": pr_info.get("number"),
            "title": pr_info.get("title"),
            "state": pr_info.get("state"),
            "url": pr_info.get("url"),
            "head_branch": pr_info.get("headRefName"),
            "base_branch": pr_info.get("baseRefName"),
            "author": pr_info.get("author", {}).get("login"),
        },
        "review_comments": {
            "total_threads": len(threads),
            "total_inline_comments": len(inline_comments),
            "total_review_bodies": len(review_bodies),
        },
        "threads": [
            {
                "thread_id": t.thread_id,
                "path": t.path,
                "line": t.line,
                "comment_count": len(t.comments),
                "comments": [asdict(c) for c in t.comments],
            }
            for t in threads
        ],
        "review_bodies": [asdict(r) for r in review_bodies],
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
