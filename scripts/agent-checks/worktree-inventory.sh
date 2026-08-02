#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
WITH_PR=0

usage() {
  cat <<'EOF'
Usage: scripts/agent-checks/worktree-inventory.sh [--with-pr]

Prints a read-only inventory of every worktree owned by the current repository:
path, branch, HEAD, dirty/staged counts, upstream, ahead/behind, remote-branch
tracking, and (with --with-pr) the current GitHub PR.

Notes:
  - Remote-branch presence uses local remote refs; fetch first when freshness matters.
  - --with-pr performs read-only GitHub queries through gh.
  - The script never stages, commits, pushes, removes, or prunes worktrees.
EOF
}

if [[ $# -gt 1 ]]; then
  usage
  exit 2
fi
if [[ $# -eq 1 ]]; then
  case "$1" in
    --with-pr) WITH_PR=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
fi

if [[ -z "$ROOT" ]]; then
  echo "worktree-inventory: not inside a Git repository" >&2
  exit 1
fi

printf 'repository: %s\n' "$ROOT"
printf 'remote_evidence: %s\n' "$([[ "$WITH_PR" -eq 1 ]] && echo 'local refs + live PR query' || echo 'local refs only')"

git -C "$ROOT" worktree list --porcelain | awk '/^worktree / {sub(/^worktree /, ""); print}' |
while IFS= read -r worktree; do
  if [[ ! -d "$worktree" ]]; then
    echo
    printf 'worktree: %s\n' "$worktree"
    printf 'state: missing-or-prunable\n'
    printf 'branch: unknown\n'
    printf 'head: unknown\n'
    printf 'dirty: unknown (staged=unknown unstaged=unknown untracked=unknown)\n'
    printf 'upstream: unknown\n'
    printf 'ahead_behind: ahead=unknown behind=unknown\n'
    printf 'remote_branch: unknown\n'
    printf 'pr: not-queried\n'
    continue
  fi
  branch="$(git -C "$worktree" symbolic-ref --quiet --short HEAD 2>/dev/null || echo detached)"
  head="$(git -C "$worktree" rev-parse --short=12 HEAD)"
  status="$(git -C "$worktree" status --porcelain=v1)"
  dirty=0
  staged=0
  unstaged=0
  untracked=0
  if [[ -n "$status" ]]; then
    dirty="$(printf '%s\n' "$status" | awk 'NF {count++} END {print count+0}')"
    staged="$(printf '%s\n' "$status" | awk 'substr($0,1,1) != " " && substr($0,1,2) != "??" {count++} END {print count+0}')"
    unstaged="$(printf '%s\n' "$status" | awk 'substr($0,2,1) != " " && substr($0,1,2) != "??" {count++} END {print count+0}')"
    untracked="$(printf '%s\n' "$status" | awk 'substr($0,1,2) == "??" {count++} END {print count+0}')"
  fi

  upstream="$(git -C "$worktree" rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || true)"
  ahead="unknown"
  behind="unknown"
  if [[ -n "$upstream" ]]; then
    counts="$(git -C "$worktree" rev-list --left-right --count "$upstream...HEAD" 2>/dev/null || true)"
    if [[ -n "$counts" ]]; then
      behind="${counts%%[[:space:]]*}"
      ahead="${counts##*[[:space:]]}"
    fi
  fi

  remote_branch="not-applicable"
  if [[ "$branch" != "detached" ]]; then
    if git -C "$ROOT" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
      remote_branch="present-in-local-refs"
    else
      remote_branch="absent-from-local-refs"
    fi
  fi

  pr="not-queried"
  if [[ "$WITH_PR" -eq 1 ]]; then
    if [[ "$branch" == "detached" ]]; then
      pr="not-applicable"
    elif command -v gh >/dev/null 2>&1; then
      pr="$(gh pr list --repo "$(git -C "$ROOT" remote get-url origin)" --head "$branch" --state all --limit 1 --json number,state,url --jq 'if length == 0 then "none" else .[0] | "#\(.number) \(.state) \(.url)" end' 2>/dev/null || echo unavailable)"
    else
      pr="gh-unavailable"
    fi
  fi

  echo
  printf 'worktree: %s\n' "$worktree"
  printf 'branch: %s\n' "$branch"
  printf 'head: %s\n' "$head"
  printf 'dirty: %s (staged=%s unstaged=%s untracked=%s)\n' "$dirty" "$staged" "$unstaged" "$untracked"
  printf 'upstream: %s\n' "${upstream:-none}"
  printf 'ahead_behind: ahead=%s behind=%s\n' "$ahead" "$behind"
  printf 'remote_branch: %s\n' "$remote_branch"
  printf 'pr: %s\n' "$pr"
done
