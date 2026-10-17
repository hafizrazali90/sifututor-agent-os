#!/usr/bin/env python3
"""Check a filled Session Map page before showing it to Hafiz.

The page template (docs/agent-playbooks/templates/session-map.html) draws every
part of the page from one data block. This check reads that block and reports
anything that would show a blank, a misspelled state, or an unfilled
placeholder. It prints one plain line per problem and exits 1 if there is any.

Usage: python3 scripts/agent-checks/session_map_page_check.py <page.html> [...]
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

STATES = {"todo", "discussing", "agreed", "written", "checked", "done"}
BLOCK = re.compile(r"/\* SESSION DATA START \*/(.*?)/\* SESSION DATA END \*/", re.S)
BAD_TEXT = (
    ("—", "an em dash"),
    ("REPLACE", "an unfilled placeholder (REPLACE)"),
    ("undefined", "the word undefined"),
    ("Not recorded", "the words Not recorded"),
)
# The data block is JavaScript, so Node has to run it to read it. Node's vm module is NOT a
# security boundary, so Node is started with its permission model, which denies file,
# process and network access. Still check only pages you wrote or trust.
NODE_FLAGS = ["--experimental-permission"]
NODE_READER = (
    "const vm=require('vm');let c='';"
    "process.stdin.on('data',d=>c+=d).on('end',()=>{try{"
    "const r=vm.runInNewContext(c+';JSON.stringify(SESSION)',{},{timeout:1000});"
    "process.stdout.write(r)}catch(e){process.stderr.write(String(e.message));process.exit(2)}})"
)


def read_data(text: str) -> tuple[dict | None, str]:
    match = BLOCK.search(text)
    if not match:
        return None, "No data block found between the SESSION DATA START and END markers."
    try:
        done = subprocess.run(
            ["node", *NODE_FLAGS, "-e", NODE_READER], input=match.group(1), capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"The data block could not be read ({type(exc).__name__})."
    if done.returncode != 0:
        if "bad option" in done.stderr:
            return None, "This check needs Node 20 or newer, because it runs the data block with Node's permission model."
        reason = next((ln for ln in done.stderr.splitlines() if "Warning" not in ln and ln.strip()), "").strip()
        return None, f"The data block could not be read or tried something it may not do: {reason[:120]}"
    try:
        return json.loads(done.stdout), ""
    except json.JSONDecodeError:
        return None, "The data block did not turn into plain data."


def strings(value, path: str = ""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, f"{path}[{index}]")


def blank(value) -> bool:
    return not isinstance(value, str) or not value.strip()


def check_data(data: dict) -> list[str]:
    problems: list[str] = []
    for key in ("title", "asOf", "defaultBy"):
        if blank(data.get(key)):
            problems.append(f"{key} is empty.")
    if not blank(data.get("asOf")) and "MYT" not in data["asOf"]:
        problems.append("asOf must give the time in MYT, for example 17/10 19:29 MYT.")

    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        problems.append("There are no groups. Add at least one goal with steps.")
        groups = []
    here_steps = 0
    open_work = False
    for group in groups:
        name = group.get("name") if isinstance(group, dict) else None
        steps = group.get("steps") if isinstance(group, dict) else None
        if blank(name):
            problems.append("A group has no name.")
        if not isinstance(steps, list) or not steps:
            problems.append(f"Group '{name}' has no steps.")
            continue
        for step in steps:
            label = step.get("n") if blank(step.get("n")) is False else "(unnamed step)"
            if blank(step.get("n")):
                problems.append(f"A step in group '{name}' has no name.")
            if blank(step.get("d")):
                problems.append(f"Step '{label}' has no description. Write one or two plain sentences.")
            state = str(step.get("s", "")).strip().lower()
            if state not in STATES:
                problems.append(f"Step '{label}' has an unknown state '{step.get('s')}'. Use one of: {', '.join(sorted(STATES))}.")
            elif state != "done":
                open_work = True
            if step.get("here"):
                here_steps += 1
            by = step.get("by")
            if isinstance(by, list) and not all(isinstance(item, str) and item.strip() for item in by):
                problems.append(f"Step '{label}' has a 'by' list with a blank entry.")
    if here_steps > 1:
        problems.append("More than one step is marked here. Mark only the step we are on.")
    if here_steps == 0 and open_work:
        problems.append("No step is marked here. Add here: true to the step we are on.")

    for row in data.get("usage") or []:
        label = row.get("n") or "(unnamed)"
        for key in ("n", "where", "plan"):
            if blank(row.get(key)):
                problems.append(f"Usage '{label}' has no {key}.")
        used = row.get("used")
        if isinstance(used, (int, float)) and not isinstance(used, bool):
            if blank(row.get("read")) or "MYT" not in row["read"] or blank(row.get("resets")) or "MYT" not in row["resets"]:
                problems.append(f"Usage '{label}' shows a number but has no reading time (read) and reset time (resets) in MYT.")
        elif used is not None:
            problems.append(f"Usage '{label}' must be a number or null, never text.")
    for row in data.get("jobs") or []:
        label = row.get("n") or "(unnamed)"
        for key in ("n", "where", "acct", "ai"):
            if blank(row.get(key)):
                problems.append(f"Job '{label}' has no {key}.")
        if str(row.get("s", "")).strip().lower() not in STATES:
            problems.append(f"Job '{label}' has an unknown state '{row.get('s')}'.")

    seen: set[str] = set()
    for path, text in strings(data):
        for needle, words in BAD_TEXT:
            if needle in text:
                message = f"{path} contains {words}."
                if message not in seen:
                    seen.add(message)
                    problems.append(message)
    return problems


def check_page(path: Path) -> list[str]:
    data, error = read_data(Path(path).read_text(encoding="utf-8"))
    if data is None:
        return [error]
    return check_data(data)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    failed = False
    for name in argv:
        problems = check_page(Path(name))
        if problems:
            failed = True
            print(f"{name}: {len(problems)} problem(s)")
            for line in problems:
                print(f"  - {line}")
        else:
            print(f"{name}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
