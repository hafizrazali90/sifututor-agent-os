#!/usr/bin/env bash
# Lane 45: read-only view of the Ripple PM2 error log (issue #371), over `ssh staging` (the KVM8 box that runs both
# Ripple staging and Ripple production). The log is read as the `deploy` account that owns it, never as root.
# The box sends back the last 400 lines at most; this script keeps the error-level ones, masks them, and prints at
# most 60, newest last. It never prints the environment and never calls `pm2 env` or `pm2 jlist`.
#
# Usage:  scripts/agent-access/ripple-logs-readonly.sh staging|prod [--lines N] [--pattern REGEX]
#           --lines N        error lines to print, 1 to 60 (default 30)
#           --pattern REGEX  keep only lines matching this extended regex; it is matched against the MASKED line,
#                            so it cannot be used to probe a hidden value
#         some-command | scripts/agent-access/ripple-logs-readonly.sh --mask-stdin [--lines N] [--pattern REGEX]
#           masks and filters lines from standard input instead of using ssh (the tests use it)
# Masks:  secret, token, password and key values; cookies; authorization headers; connection URLs; long tokens and
#         JWTs; phone numbers; email addresses.
# Env:    RIPPLE_LOGS_DRY_RUN=1 prints the remote command instead of running it.

set -euo pipefail

ALIAS_NAME="${RIPPLE_LOGS_SSH_ALIAS:-staging}"
LOG_DIR="/home/deploy/.pm2/logs"
READ_LINES=400
MAX_PRINT=60

refuse() { echo "refused: $1" >&2; exit 3; }
usage() { echo "usage: ripple-logs-readonly.sh staging|prod [--lines N] [--pattern REGEX] | --mask-stdin [--lines N] [--pattern REGEX]" >&2; exit 2; }

[[ $# -ge 1 ]] || usage
case "$1" in
  staging) MODE=ssh; FILE="$LOG_DIR/ripple-suite-staging-error.log" ;;
  prod) MODE=ssh; FILE="$LOG_DIR/ripple-suite-prod-error.log" ;;
  --mask-stdin) MODE=stdin; FILE="" ;;
  *) usage ;;
esac
shift

LINES=30
PATTERN=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lines)
      [[ $# -ge 2 ]] || usage
      LINES="$2"; shift 2 ;;
    --pattern)
      [[ $# -ge 2 ]] || usage
      PATTERN="$2"; shift 2 ;;
    *) refuse "unknown argument '$1' (only --lines N and --pattern REGEX)" ;;
  esac
done

[[ "$LINES" =~ ^[0-9]+$ ]] || refuse "lines must be a number"
(( LINES >= 1 && LINES <= MAX_PRINT )) || refuse "lines must be between 1 and $MAX_PRINT"
(( ${#PATTERN} <= 200 )) || refuse "the pattern is longer than 200 characters"
[[ "$ALIAS_NAME" =~ ^[a-z0-9_-]+$ ]] || refuse "bad ssh alias name"

read -r -d '' MASKER <<'PY' || true
import re
import sys

limit = int(sys.argv[1])
pattern = sys.argv[2]
try:
    wanted = re.compile(pattern) if pattern else None
except re.error:
    print("refused: the pattern is not a valid regular expression", file=sys.stderr)
    sys.exit(3)

# Error-level lines: what Next.js, Node and the app write when something fails. Stack frames ("    at ...") are left
# out on purpose, so the 60 printed lines are errors, not one long trace.
ERROR = re.compile(r"(?i)(\berror\b|\berr!|\bfatal\b|\bexception\b|\bunhandled|\bfailed\b|\bfailure\b|\bpanic\b|"
                   r"\b[A-Z][A-Za-z]*Error\b|\bE[A-Z]{3,}\b|⨯|\bstatus(?:code)?[\"']?\s*[:=]\s*5\d\d\b|\b5\d\d\s+(?:internal|bad gateway))")

SECRET_KEY = (r"[A-Za-z0-9_.-]*(?:password|passwd|pwd|secret|token|api[-_]?key|apikey|access[-_]?key|private[-_]?key|"
              r"client[-_]?secret|credential|session[-_]?id|sessionid|signature)[A-Za-z0-9_.-]*")
# Record ids (UUIDs) and 40-hex commit ids stay readable: they are what a diagnosis needs and not secrets.
KEEP_ID = r"(?![0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![A-Za-z0-9_-]))(?![0-9a-f]{40}(?![A-Za-z0-9_-]))"


def mask(line: str) -> str:
    # Connection URLs (database, cache, queue): the whole URL, since host and database names are not for logs either.
    line = re.sub(r"(?i)\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|rediss|amqps?|mssql|sqlserver)://[^\s\"'<>]+",
                  "[connection-url]", line)
    # user:pass@ inside any other URL.
    line = re.sub(r"([A-Za-z][A-Za-z0-9+.-]*://)[^/\s:@\"']+:[^@\s/\"']+@", r"\1***@", line)
    # Cookie and Set-Cookie headers, in header form and in JSON or object form.
    line = re.sub(r"(?i)\b((?:set-)?cookie[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\n]*)", r"\1***", line)
    # Authorization headers and bearer or basic credentials.
    line = re.sub(r"(?i)\b((?:proxy-)?authorization[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|(?:bearer|basic|token)\s+\S+|\S+)",
                  r"\1***", line)
    line = re.sub(r"(?i)\b(bearer|basic)(\s+)[A-Za-z0-9._~+/=-]{8,}", r"\1\2***", line)
    # key=value, key: value and "key": "value" where the key looks secret.
    line = re.sub(r"(?i)([\"']?\b" + SECRET_KEY + r"[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;&\"'})\]]+)", r"\1***", line)
    # JWTs and other long opaque tokens.
    line = re.sub(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?:\.[A-Za-z0-9_-]+)?", "[token]", line)
    line = re.sub(r"(?<![A-Za-z0-9/_-])" + KEEP_ID + r"(?=[A-Za-z0-9_-]*[0-9])(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{32,}(?![A-Za-z0-9/_-])", "[token]", line)
    # Email addresses.
    line = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email]", line)
    # Phone numbers: Malaysian mobile and fixed forms, and any international number written with a plus.
    line = re.sub(r"(?<![\w.:/-])\+\d[\d ()-]{7,16}\d(?![\w])", "[phone]", line)
    line = re.sub(r"(?<![\w.:/+-])(?:\+?60|0)1\d[- ]?\d{3,4}[- ]?\d{4}(?![\w])", "[phone]", line)
    line = re.sub(r"(?<![\w.:/+-])(?:60|0)[3-9][- ]?\d{3,4}[- ]?\d{4}(?![\w])", "[phone]", line)
    return line


kept = []
for raw in sys.stdin:
    line = raw.rstrip("\n").replace("\r", "")
    if not ERROR.search(line):
        continue
    line = mask(line)[:600]
    if wanted is not None and not wanted.search(line):
        continue
    kept.append(line)
for line in kept[-limit:]:
    print(line)
PY

if [[ "$MODE" == "stdin" ]]; then
  exec python3 -c "$MASKER" "$LINES" "$PATTERN"
fi

# The pattern is checked before any ssh, so a bad one never touches the box.
python3 -c "$MASKER" "$LINES" "$PATTERN" </dev/null

REMOTE="runuser -u deploy -- tail -n $READ_LINES $FILE"

if [[ "${RIPPLE_LOGS_DRY_RUN:-0}" == "1" ]]; then
  echo "$REMOTE"
  exit 0
fi

ssh -o BatchMode=yes -o ConnectTimeout=20 "$ALIAS_NAME" "$REMOTE" | python3 -c "$MASKER" "$LINES" "$PATTERN"
