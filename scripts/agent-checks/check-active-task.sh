#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
active_file="$repo_root/.claude/tasks/active.json"

if [[ ! -f "$active_file" ]]; then
  echo "active-task: none"
  exit 0
fi

echo "active-task: found $active_file"

python3 - "$active_file" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception as exc:
    print(f"active-task: invalid json: {exc}")
    sys.exit(1)

task_id = data.get("activeTask") or data.get("id")
task_file = data.get("taskFile") or data.get("file") or ""
route = data.get("route") or "unknown"

if not task_id:
    print("active-task: none")
    sys.exit(0)

print(f"active-task: id={task_id} route={route}")
if task_file:
    print(f"active-task: file={task_file}")

candidate = path.parent / f"{task_id}.json"
if candidate.exists():
    try:
        task = json.loads(candidate.read_text())
        steps = task.get("steps", [])
        pending = [
            s.get("name", "?")
            for s in steps
            if s.get("status") not in ("done", "skipped")
        ]
        if pending:
            print(f"active-task: next={pending[0]}")
        else:
            print("active-task: all steps done")
    except Exception as exc:
        print(f"active-task: could not read task file: {exc}")
        sys.exit(1)
PY
