#!/usr/bin/env bash
# List running processes with the full command line, secret-looking values masked.
# Read-only: runs `ps` locally (or on the machine the caller is already on) and
# rewrites each line before printing. Nothing is logged or stored.
#
# Prints: pid, user, elapsed time, command line (values masked as ***).
# Masks:
#   -p<value> and -p <value> after mysql, mariadb, mysqldump, mysqladmin
#   --password=, --passwd=, --token=, --secret=, --api-key= (and the space form)
#   Authorization: Bearer / Basic ...
#   user:pass@ inside URLs (postgres://, mysql://, https://, ...)
#   long hex or base64-looking tokens after key-like flags
#   KEY=value pairs where KEY looks secret (KEY, TOKEN, SECRET, PASSWORD, ...)
#
# Usage:
#   scripts/agent-access/proc-list-masked.sh [pattern]
#   some-command | scripts/agent-access/proc-list-masked.sh --mask-stdin [pattern]
#
# `pattern` is an extended regular expression matched against the MASKED line, so
# the pattern cannot be used to probe a hidden value.
# `--mask-stdin` masks lines read from standard input instead of running ps; the
# tests use it, and it is handy for masking a command line copied from a log.

set -euo pipefail

mode="ps"
if [[ "${1:-}" == "--mask-stdin" ]]; then
  mode="stdin"
  shift
fi
pattern="${1:-}"

read -r -d '' MASKER <<'PY' || true
import re
import sys

pattern = sys.argv[1] if len(sys.argv) > 1 else ""
self_marker = "proc-list-masked"

VALUE = r"""(?:"[^"]*"|'[^']*'|\S+)"""
SECRETISH = r"[A-Za-z0-9_.-]*(?:password|passwd|pwd|token|secret|api[-_]?key|apikey|credential|auth)[A-Za-z0-9_.-]*"
KEYFLAG = r"(?:key|token|secret|password|passwd|pass|auth|credential|api[-_]?key|apikey|access[-_]?key|private[-_]?key)"
DB_CLIENTS = ("mysql", "mariadb", "mysqldump", "mysqladmin", "mariadb-dump", "mariadb-admin")


def mask_db_password(line):
    seen_client = False
    # work on the original text so spacing is kept
    pieces = re.split(r"(\s+)", line)
    result = []
    mask_next = False
    for piece in pieces:
        if piece.isspace() or piece == "":
            result.append(piece)
            continue
        base = piece.rsplit("/", 1)[-1]
        if mask_next:
            result.append("***")
            mask_next = False
            continue
        if any(base == c or base.startswith(c + ".") for c in DB_CLIENTS):
            seen_client = True
            result.append(piece)
            continue
        if seen_client and re.fullmatch(r"-p\S+", piece):
            result.append("-p***")
            continue
        if seen_client and piece == "-p":
            result.append(piece)
            mask_next = True
            continue
        result.append(piece)
    return "".join(result)


def mask(line):
    line = mask_db_password(line)
    # --password=VALUE, --token=VALUE, --secret=VALUE, --api-key=VALUE and the space form
    line = re.sub(
        r"(?i)(--" + SECRETISH + r")(=)" + VALUE, lambda m: m.group(1) + m.group(2) + "***", line
    )
    line = re.sub(
        r"(?i)(--" + SECRETISH + r")(\s+)(?!-)" + VALUE, lambda m: m.group(1) + m.group(2) + "***", line
    )
    # Authorization headers and bearer / basic credentials
    line = re.sub(r"(?i)(authorization\s*:\s*(?:bearer|basic|token)?\s*)[^\s'\"]+", lambda m: m.group(1) + "***", line)
    line = re.sub(r"(?i)\b(bearer|basic)(\s+)[A-Za-z0-9._~+/=-]{8,}", lambda m: m.group(1) + m.group(2) + "***", line)
    # user:pass@host inside URLs
    line = re.sub(r"([A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+):[^@\s/]+@", r"\1:***@", line)
    # long hex or base64-looking tokens after key-like flags
    line = re.sub(
        r"(?i)(--?" + KEYFLAG + r"[A-Za-z0-9_-]*[= ]\s*)[A-Za-z0-9+/=_-]{16,}",
        lambda m: m.group(1) + "***",
        line,
    )
    # KEY=value pairs where KEY looks secret
    line = re.sub(
        r"(?i)\b([A-Za-z0-9_]*(?:key|token|secret|password|passwd|pass|credential|auth|mysql_pwd)[A-Za-z0-9_]*)=" + VALUE,
        lambda m: m.group(1) + "=***",
        line,
    )
    return line


rx = re.compile(pattern) if pattern else None
for raw in sys.stdin:
    line = raw.rstrip("\n")
    if self_marker in line:
        continue
    line = mask(line)
    if rx is None or rx.search(line):
        print(line)
PY

run_masker() {
  python3 -c "$MASKER" "$pattern"
}

if [[ "$mode" == "stdin" ]]; then
  run_masker
  exit 0
fi

# pid, user, elapsed time, full command line. The same flags work on macOS and Linux.
printf '%7s %-12s %12s  %s\n' PID USER ELAPSED COMMAND
ps -axo pid=,user=,etime=,command= | python3 -c '
import sys
for raw in sys.stdin:
    parts = raw.strip().split(None, 3)
    if len(parts) == 4:
        print("%7s %-12s %12s  %s" % tuple(parts))
' | run_masker
