# Workspace Parity Quick Check

Use this before trusting a Claude/Codex switch, before a commit wave, or after
editing workflow files.

## Baseline Matrix

```bash
for d in sifu-tutor ripple-suite sifututor_tutor sifututor_parent lls lls-frontend lls-mobile creative-hub team-inbox finch-inbox; do
  printf '%s ' "$d"
  test -f "$d/AGENTS.md" && printf 'AGENTS=yes ' || printf 'AGENTS=no '
  test -f "$d/.claude/tasks/active.json" && printf 'tasks=yes ' || printf 'tasks=no '
  test -d "$d/.claude/hooks" && printf 'hooks=yes\n' || printf 'hooks=no\n'
done
```

Expected result: every project prints `AGENTS=yes tasks=yes hooks=yes`.

## Guard All Projects

```bash
for d in sifu-tutor ripple-suite sifututor_tutor sifututor_parent lls lls-frontend lls-mobile creative-hub team-inbox finch-inbox; do
  printf '\n== %s ==\n' "$d"
  (cd "$d" && ../scripts/agent-checks/pre-commit-guard.sh)
done
```

Expected result:

- Branch name is valid.
- Sensitive paths are not staged.
- Active task file is found or correctly absent.
- Any active task reports its next step.

## Validate Workflow Files

```bash
find . -path '*/.claude/tasks/active.json' -o -path '*/.claude/settings.json' |
  sort |
  xargs jq . >/dev/null
```

```bash
find . -path '*/.claude/hooks/*.py' -print0 |
  xargs -0 python3 -m py_compile
```

## Stale Text Scan

```bash
rg -n 'Workflow conventions are not yet codified|falls through to the global generic|Source of truth read order: `CLAUDE.md|Workflow skills are NOT yet codified|no `\\.claude/` config yet' -S .
```

Expected result: no matches.
