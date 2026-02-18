#!/usr/bin/env python3
"""VCS detection and unified interface for jj/git operations."""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class VCSType(str, Enum):
    JJ = "jj"
    GIT = "git"


@dataclass
class VCSInfo:
    vcs_type: VCSType
    root_dir: str
    current_branch: Optional[str]
    remote_url: Optional[str]


def run_cmd(cmd: list[str], cwd: Optional[str] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        check=check,
    )


def detect_vcs(directory: Optional[str] = None) -> VCSInfo:
    """Detect VCS type by checking for .jj directory first, then .git."""
    search_dir = Path(directory) if directory else Path.cwd()

    # Walk up to find VCS root
    current = search_dir.resolve()
    while current != current.parent:
        if (current / ".jj").is_dir():
            return _build_jj_info(str(current))
        if (current / ".git").exists():
            return _build_git_info(str(current))
        current = current.parent

    print(json.dumps({"error": "No VCS repository found", "searched_from": str(search_dir)}))
    sys.exit(1)


def _build_jj_info(root: str) -> VCSInfo:
    """Build VCS info for jj repository."""
    branch = None
    try:
        result = run_cmd(
            ["jj", "log", "--no-graph", "-r", "@", "-T", "bookmarks", "--color=never"],
            cwd=root,
            check=False,
        )
        if result.returncode == 0:
            branch = result.stdout.strip().split("\n")[0].strip() or None
    except FileNotFoundError:
        pass

    remote_url = None
    try:
        result = run_cmd(
            ["jj", "git", "remote", "list"],
            cwd=root,
            check=False,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("origin"):
                    remote_url = line.split(None, 1)[1] if len(line.split()) > 1 else None
                    break
    except FileNotFoundError:
        pass

    return VCSInfo(
        vcs_type=VCSType.JJ,
        root_dir=root,
        current_branch=branch,
        remote_url=remote_url,
    )


def _build_git_info(root: str) -> VCSInfo:
    """Build VCS info for git repository."""
    branch = None
    try:
        result = run_cmd(["git", "branch", "--show-current"], cwd=root, check=False)
        if result.returncode == 0:
            branch = result.stdout.strip() or None
    except FileNotFoundError:
        pass

    remote_url = None
    try:
        result = run_cmd(["git", "remote", "get-url", "origin"], cwd=root, check=False)
        if result.returncode == 0:
            remote_url = result.stdout.strip() or None
    except FileNotFoundError:
        pass

    return VCSInfo(
        vcs_type=VCSType.GIT,
        root_dir=root,
        current_branch=branch,
        remote_url=remote_url,
    )


def get_changed_files(vcs_info: VCSInfo) -> list[str]:
    """Get list of changed files in the working copy."""
    if vcs_info.vcs_type == VCSType.JJ:
        result = run_cmd(
            ["jj", "diff", "--stat", "--color=never"],
            cwd=vcs_info.root_dir,
            check=False,
        )
    else:
        result = run_cmd(
            ["git", "diff", "--name-only"],
            cwd=vcs_info.root_dir,
            check=False,
        )

    if result.returncode != 0:
        return []

    files = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith(" ") and "|" not in line:
            files.append(line)
        elif "|" in line:
            # jj stat format: "file | N +++---"
            files.append(line.split("|")[0].strip())
    return [f for f in files if f and not f.endswith("changed")]


def commit_changes(
    vcs_info: VCSInfo,
    message: str,
    files: Optional[list[str]] = None,
) -> dict:
    """Commit changes with the given message."""
    if vcs_info.vcs_type == VCSType.JJ:
        return _jj_commit(vcs_info, message, files)
    else:
        return _git_commit(vcs_info, message, files)


def _jj_commit(vcs_info: VCSInfo, message: str, files: Optional[list[str]]) -> dict:
    """Commit using jj."""
    cwd = vcs_info.root_dir

    if files:
        # Create new change from specific files
        split_cmd = ["jj", "split", "--quiet"]
        split_cmd.extend(files)
        env = os.environ.copy()
        env["EDITOR"] = "true"
        env["JJ_EDITOR"] = "true"
        result = subprocess.run(
            split_cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            return {"success": False, "error": f"jj split failed: {result.stderr}"}

        # Describe the split-off change
        result = run_cmd(
            ["jj", "describe", "@-", "-m", message],
            cwd=cwd,
            check=False,
        )
    else:
        # Describe current change
        result = run_cmd(
            ["jj", "describe", "-m", message],
            cwd=cwd,
            check=False,
        )
        if result.returncode == 0:
            # Create new empty change on top
            run_cmd(["jj", "new"], cwd=cwd, check=False)

    return {
        "success": result.returncode == 0,
        "vcs": "jj",
        "message": message,
        "error": result.stderr if result.returncode != 0 else None,
    }


def _git_commit(vcs_info: VCSInfo, message: str, files: Optional[list[str]]) -> dict:
    """Commit using git."""
    cwd = vcs_info.root_dir

    if files:
        result = run_cmd(["git", "add"] + files, cwd=cwd, check=False)
        if result.returncode != 0:
            return {"success": False, "error": f"git add failed: {result.stderr}"}
    else:
        result = run_cmd(["git", "add", "-u"], cwd=cwd, check=False)
        if result.returncode != 0:
            return {"success": False, "error": f"git add failed: {result.stderr}"}

    result = run_cmd(["git", "commit", "-m", message], cwd=cwd, check=False)
    return {
        "success": result.returncode == 0,
        "vcs": "git",
        "message": message,
        "error": result.stderr if result.returncode != 0 else None,
    }


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    info = detect_vcs(directory)
    print(json.dumps({
        "vcs_type": info.vcs_type.value,
        "root_dir": info.root_dir,
        "current_branch": info.current_branch,
        "remote_url": info.remote_url,
    }, indent=2))
