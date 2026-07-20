#!/usr/bin/env python3
"""PreToolUse hook: strips AI attribution trailers from `git commit` commands.

Claude (and other AI models) append attribution to commit messages:
  - `Co-Authored-By: Claude <noreply@anthropic.com>`
  - `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
This hook rewrites the Bash/PowerShell command *before* it runs, removing those
lines from the message text — so the commit is created clean, with no need for a
follow-up `git commit --amend`.

The trailers are always present verbatim inside the command string (whether the
message is passed via `-m "..."` or a `cat <<EOF` heredoc), so a text edit on the
command is surgical and atomic: no double commit, no post-hoc rewrite.

jq-free by design — jq is not guaranteed on every machine. hooks.json invokes
this with `python ... || python3 ...` so it runs whether the interpreter is named
`python` (typical on Windows) or `python3` (typical on Linux/macOS).
"""
import json
import re
import sys

# Matches a Co-Authored-By trailer line attributing the commit to an AI
# (Claude / Anthropic), together with the newline that precedes it. Case- and
# whitespace-tolerant. There is always a message line before the trailer, so
# consuming the leading "\n" cleanly removes the line without merging text.
#
# Each pattern matches one attribution line together with the newline that
# precedes it. There is always a message line before these trailers, so consuming
# the leading "\n" cleanly removes the line without merging text.
#
# Both patterns anchor their END on the line's own closing delimiter — ">" for the
# email address, ")" for the markdown link. Anchoring there is deliberate: when a
# trailer is the last line of the message, shell syntax (a closing quote or paren)
# follows it on the SAME line — a greedy "[^\n]*" to end-of-line would eat that and
# corrupt the command.
TRAILER_PATTERNS = (
    # Co-authored-by: NAME <EMAIL>  (only AI attributions: Claude / Anthropic)
    re.compile(
        r"\n[ \t]*co-authored-by:[^\n]*(?:claude|anthropic)[^\n]*>",
        re.IGNORECASE,
    ),
    # 🤖 Generated with [Claude Code](https://claude.com/claude-code)
    re.compile(
        r"\n[ \t]*(?:🤖[ \t]*)?generated with[^\n]*claude[^\n]*\)",
        re.IGNORECASE,
    ),
)


def strip_trailer(command: str) -> str:
    """Remove AI attribution trailer lines from a command string."""
    cleaned = command
    for pattern in TRAILER_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    # Collapse blank lines left dangling right before a heredoc terminator or a
    # closing quote (git already strips trailing blanks, this just keeps it tidy).
    cleaned = re.sub(r"\n(?:[ \t]*\n)+(\s*(?:EOF|['\"]))", r"\n\1", cleaned)
    return cleaned


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0

    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    if not command:
        return 0

    cleaned = strip_trailer(command)
    if cleaned == command:
        return 0  # nothing to strip — stay silent, let the command through

    updated_input = dict(tool_input)
    updated_input["command"] = cleaned

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": updated_input,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
