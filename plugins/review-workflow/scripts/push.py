#!/usr/bin/env python3
"""Push changes to remote. Outputs push command for Claude to execute."""

import json
import subprocess
import sys

from vcs import VCSType, detect_vcs


def get_push_info(project_dir: str | None = None) -> dict:
    """Get information needed for pushing, without actually pushing.

    Returns the recommended push command and context for Claude
    to execute (with user confirmation for git, via safe-push for jj).
    """
    vcs_info = detect_vcs(project_dir)

    if vcs_info.vcs_type == VCSType.JJ:
        # For jj, recommend using safe-push skill
        return {
            "vcs": "jj",
            "method": "safe-push",
            "instruction": "Use the jj-safe-push skill to push safely.",
            "branch": vcs_info.current_branch,
            "remote_url": vcs_info.remote_url,
        }
    else:
        # For git, provide the push command for user confirmation
        branch = vcs_info.current_branch
        if not branch:
            return {
                "vcs": "git",
                "error": "Not on a branch. Cannot determine push target.",
            }

        # Check if branch has upstream
        upstream_ref = f"{branch}@{{u}}"
        result = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--abbrev-ref", upstream_ref],  # noqa: S607
            capture_output=True,
            text=True,
            cwd=vcs_info.root_dir,
            check=False,
        )

        has_upstream = result.returncode == 0

        # Count unpushed commits
        if has_upstream:
            rev_range = f"origin/{branch}..HEAD"
            count_result = subprocess.run(  # noqa: S603
                ["git", "rev-list", "--count", rev_range],  # noqa: S607
                capture_output=True,
                text=True,
                cwd=vcs_info.root_dir,
                check=False,
            )
            if count_result.returncode == 0:
                unpushed = int(count_result.stdout.strip())
            else:
                unpushed = "unknown"
        else:
            unpushed = "all (new branch)"

        push_cmd = f"git push origin {branch}"
        if not has_upstream:
            push_cmd = f"git push -u origin {branch}"

        return {
            "vcs": "git",
            "method": "confirm_and_push",
            "push_command": push_cmd,
            "branch": branch,
            "has_upstream": has_upstream,
            "unpushed_commits": unpushed,
            "remote_url": vcs_info.remote_url,
        }


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    info = get_push_info(project_dir)
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
