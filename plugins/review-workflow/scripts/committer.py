#!/usr/bin/env python3
"""Commit changes grouped by review comment."""

import json
import sys
from pathlib import Path

from vcs import VCSInfo, commit_changes, detect_vcs, get_changed_files


def load_fix_plan(plan_path: str) -> list[dict]:
    """Load the fix plan JSON that maps review comments to changed files.

    Expected format:
    [
      {
        "thread_id": 123,
        "summary": "Fix type annotation for user prop",
        "files": ["src/components/UserCard.tsx"],
        "commit_message": "fix: correct type annotation for user prop"
      },
      ...
    ]
    """
    path = Path(plan_path)
    if not path.is_file():
        print(json.dumps({"error": f"Fix plan not found: {plan_path}"}))
        sys.exit(1)

    return json.loads(path.read_text(encoding="utf-8"))


def commit_by_review_comment(vcs_info: VCSInfo, fix_plan: list[dict]) -> dict:
    """Commit changes grouped by review comment."""
    results = {
        "vcs": vcs_info.vcs_type.value,
        "total_commits": 0,
        "successful": 0,
        "failed": 0,
        "commits": [],
    }

    changed_files = get_changed_files(vcs_info)
    if not changed_files:
        results["warning"] = "No changed files detected"
        return results

    for fix in fix_plan:
        default_msg = "fix: address review feedback"
        message = fix.get(
            "commit_message", fix.get("summary", default_msg),
        )
        files = fix.get("files", [])

        # Filter to only files that actually changed
        actual_files = [f for f in files if f in changed_files]

        if not actual_files and not files:
            # No specific files - skip this commit group
            continue

        result = commit_changes(
            vcs_info,
            message=message,
            files=actual_files if actual_files else None,
        )

        results["commits"].append({
            "thread_id": fix.get("thread_id"),
            "message": message,
            "files": actual_files or files,
            **result,
        })

        if result["success"]:
            results["successful"] += 1
        else:
            results["failed"] += 1

        results["total_commits"] += 1

    return results


def commit_all_at_once(vcs_info: VCSInfo, message: str) -> dict:
    """Fallback: commit all changes as a single commit."""
    result = commit_changes(vcs_info, message=message)
    return {
        "vcs": vcs_info.vcs_type.value,
        "total_commits": 1,
        "successful": 1 if result["success"] else 0,
        "failed": 0 if result["success"] else 1,
        "commits": [result],
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: committer.py <fix_plan.json> [project_dir]",
            "hint": "fix_plan.json maps review comments to files",
        }))
        sys.exit(1)

    plan_path = sys.argv[1]
    project_dir = sys.argv[2] if len(sys.argv) > 2 else None

    vcs_info = detect_vcs(project_dir)
    fix_plan = load_fix_plan(plan_path)

    if fix_plan:
        results = commit_by_review_comment(vcs_info, fix_plan)
    else:
        results = commit_all_at_once(vcs_info, "fix: address review feedback")

    print(json.dumps(results, indent=2, ensure_ascii=False))

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
