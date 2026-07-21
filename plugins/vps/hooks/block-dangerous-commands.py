#!/usr/bin/env python3
"""PreToolUse hook: asks for confirmation before potentially destructive commands run via Bash or PowerShell.

Covers five categories of dangerous operations, each with a dedicated confirmation
message: git commit, git reset --hard, git push --force, destructive git deletions
(branch -D / tag -d / clean -f), and recursive filesystem deletions (rm -r / find
-delete on POSIX, Remove-Item -Recurse on PowerShell).

The script scans an ordered list of categories and, on the FIRST match, emits a
single "ask" permission decision naming that category — never multiple prompts for
one command.

jq-free by design — jq is not guaranteed to be installed on every machine that
clones this repo. hooks.json invokes this with `python ... || python3 ...` so it
runs whether the interpreter is named `python` (typical on Windows) or `python3`
(typical on Linux/macOS).

The matchers tolerate chained/multi-line commands (`cd repo && git commit`, or a
command on its own line) and leading env-var assignments (`GIT_AUTHOR_DATE=... git
commit`).
"""
import json
import re
import sys

# Start-of-command boundary: string start or a shell separator, optional
# whitespace, then optional leading env-var assignments (e.g. FOO=bar cmd).
CMD_START = r"(?:^|[;&|\n\r])\s*(?:\w+=\S*\s+)*"
# `git` plus any options/paths between it and the subcommand (e.g. `git -C repo`).
GIT_LEAD = r"git(?:\s+[A-Za-z0-9_.=/:-]+)*\s+"
# A run of characters that stays within the current command (no separators),
# used to scan for a flag that may appear anywhere after the subcommand.
SAME_CMD = r"[^;&|\n\r]*"

# Each category: (name, [compiled patterns], reason message).
# Order = priority. The first category with any matching pattern wins.
GIT_CATEGORIES = [
    (
        "git commit",
        [re.compile(CMD_START + GIT_LEAD + r"commit(?:\s|$)")],
        "This agent is about to run 'git commit'. "
        "Approve only if you explicitly asked for this commit.",
    ),
    (
        "git reset --hard",
        [re.compile(CMD_START + GIT_LEAD + r"reset\b" + SAME_CMD + r"--hard\b")],
        "This agent is about to run 'git reset --hard', "
        "which discards uncommitted changes irreversibly.",
    ),
    (
        "git push --force",
        [re.compile(
            CMD_START + GIT_LEAD + r"push\b" + SAME_CMD
            + r"(?:--force\b|\s-[A-Za-z]*f[A-Za-z]*(?=\s|$))"
        )],
        "This agent is about to force-push, "
        "which can overwrite remote history or others' work.",
    ),
    (
        "git branch -D / tag -d / clean -f",
        [
            # branch force-delete: uppercase -D only (case-sensitive; -d is safe).
            re.compile(CMD_START + GIT_LEAD + r"branch\b" + SAME_CMD
                       + r"\s-[A-Za-z]*D[A-Za-z]*(?=\s|$)"),
            # tag delete: lowercase -d (tag has no uppercase form) or --delete.
            re.compile(CMD_START + GIT_LEAD + r"tag\b" + SAME_CMD
                       + r"(?:\s-[A-Za-z]*d[A-Za-z]*(?=\s|$)|--delete\b)"),
            # clean: -f / --force (with or without -d).
            re.compile(CMD_START + GIT_LEAD + r"clean\b" + SAME_CMD
                       + r"(?:\s-[A-Za-z]*f[A-Za-z]*(?=\s|$)|--force\b)"),
        ],
        "This agent is about to permanently delete a branch, tag, or untracked files.",
    ),
]

FS_MESSAGE = (
    "This agent is about to recursively/forcefully delete files or directories "
    "— this cannot be undone."
)

# POSIX (Bash): rm with a recursion flag, or `find ... -delete`. Force is
# irrelevant — recursion is what makes it destructive on directories.
FS_POSIX_PATTERNS = [
    re.compile(CMD_START + r"rm\b" + SAME_CMD
               + r"(?:\s-[A-Za-z]*[rR][A-Za-z]*(?=\s|$)|--recursive\b)"),
    re.compile(CMD_START + r"find\b" + SAME_CMD + r"\s-delete\b"),
]

# PowerShell: Remove-Item (and aliases) with -Recurse. PowerShell accepts any
# unambiguous parameter-name prefix, and -Recurse is the only Remove-Item parameter
# starting with "r", so -r / -re / -rec / -recurse are all valid and all matched.
# Longer alias names come first so \b resolves cleanly.
FS_POWERSHELL_PATTERNS = [
    re.compile(
        CMD_START
        + r"(?:Remove-Item|rmdir|erase|del|ri|rd|rm)\b"
        + SAME_CMD + r"\s-r[a-z]*\b",
        re.IGNORECASE,
    ),
]


def matched_reason(command, tool_name):
    """Return the reason message of the first dangerous category that matches, or None."""
    for _name, patterns, message in GIT_CATEGORIES:
        if any(p.search(command) for p in patterns):
            return message
    fs_patterns = (
        FS_POWERSHELL_PATTERNS if tool_name == "PowerShell" else FS_POSIX_PATTERNS
    )
    if any(p.search(command) for p in fs_patterns):
        return FS_MESSAGE
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in ("Bash", "PowerShell"):
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    reason = matched_reason(command, tool_name)
    if reason is None:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
