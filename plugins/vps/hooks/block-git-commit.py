#!/usr/bin/env python3
"""PreToolUse hook: asks for confirmation before `git commit` runs via Bash or PowerShell.

jq-free by design — jq is not guaranteed to be installed on every machine
that clones this repo, but python3 is a safe bet on this project.
"""
import json
import re
import sys

COMMIT_PATTERN = re.compile(
    r"(^|[;&|])\s*git(\s+[A-Za-z0-9_.=/:-]+)*\s+commit(\s|$)"
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command or not COMMIT_PATTERN.search(command):
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                "This agent is about to run 'git commit'. "
                "Approve only if you explicitly asked for this commit."
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
