#!/usr/bin/env bash
set -uo pipefail

input=$(cat)
tool_name=$(printf '%s' "$input" | jq -r '.tool_name // empty')

if [[ "$tool_name" != "Bash" ]]; then
  exit 0
fi

command=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

commit_pattern='(^|[;&|])[[:space:]]*git([[:space:]]+[A-Za-z0-9_.=/:-]+)*[[:space:]]+commit([[:space:]]|$)'

if printf '%s\n' "$command" | grep -qE "$commit_pattern"; then
  jq -n \
    --arg reason "This agent is about to run 'git commit'. Approve only if you explicitly asked for this commit." \
    '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: $reason
      }
    }'
  exit 0
fi

exit 0
