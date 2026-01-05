#!/usr/bin/env python3
"""
Merge all local branches into a single target branch in chronological (committer date) order.

Usage:
  python merge_branches.py --target main       # merge into main
  python merge_branches.py --dry-run           # just show the planned order
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import List, Tuple


DELIMITER = "||"


def run_git(args: List[str], check: bool = True) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def get_current_branch() -> str:
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def ensure_clean_worktree(allow_dirty: bool) -> None:
    if allow_dirty:
        return
    if run_git(["status", "--porcelain"], check=False):
        raise RuntimeError("Working tree is not clean. Commit or stash changes first, or use --allow-dirty.")


def ensure_branch_exists(branch: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Target branch '{branch}' does not exist locally.")


def list_branches_by_date() -> List[Tuple[str, str]]:
    """Return (date, branch) sorted by committer date (oldest first)."""
    output = run_git([
        "for-each-ref",
        "--sort=committerdate",
        f"--format=%(committerdate:iso8601){DELIMITER}%(refname:short)",
        "refs/heads",
    ])
    branches = []
    for line in output.splitlines():
        if DELIMITER not in line:
            raise RuntimeError(f"Unexpected ref line: {line}")
        date, name = line.split(DELIMITER, 1)
        branches.append((date, name))
    return branches


def merged_branches(target: str) -> set[str]:
    output = run_git(["branch", "--merged", target])
    merged = set()
    for line in output.splitlines():
        merged.add(line.replace("*", "").strip())
    return merged


def merge_branches(target: str, dry_run: bool, allow_dirty: bool) -> None:
    ensure_clean_worktree(allow_dirty)
    ensure_branch_exists(target)

    current_branch = get_current_branch()
    branches = list_branches_by_date()
    already_merged = merged_branches(target)

    branches_to_merge = [name for _, name in branches if name != target]
    if not branches_to_merge:
        print("No other local branches to merge.")
        return

    print(f"Merge order into '{target}' (oldest first):")
    for idx, name in enumerate(branches_to_merge, start=1):
        status = " (already merged)" if name in already_merged else ""
        print(f"{idx}. {name}{status}")

    if dry_run:
        return

    if current_branch != target:
        run_git(["checkout", target])

    for name in branches_to_merge:
        if name in already_merged:
            continue
        print(f"Merging {name} into {target} ...")
        merge_args = [
            "merge",
            "--no-ff",
            "--message",
            f"Merge branch '{name}' into {target}",
            name,
        ]
        try:
            run_git(merge_args)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Merge from '{name}' into '{target}' failed. See git output above. "
                "If conflicts occurred, resolve them and run `git merge --continue`, or run `git merge --abort` to cancel before rerunning."
            ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge all local branches into one branch by committer date (oldest first)."
    )
    parser.add_argument("--target", default=None, help="Target branch to merge into (defaults to current branch).")
    parser.add_argument("--dry-run", action="store_true", help="Only show planned merge order.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow running with a dirty working tree.",
    )
    args = parser.parse_args()

    target_branch = args.target or get_current_branch()
    merge_branches(target_branch, args.dry_run, args.allow_dirty)


if __name__ == "__main__":
    main()
