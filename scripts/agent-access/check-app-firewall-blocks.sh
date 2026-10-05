#!/usr/bin/env bash
# Count mobile app requests that the SIMS production server answered with 403,
# via Cloudflare's read-only analytics API. The server firewall (Imunify360)
# blocked the Parent and Tutor apps daily for a month before it was noticed
# (sifu-tutor #2438); a blocked request never reaches Laravel, so this is the
# only exact count.
#
# Safe: read-only token, no token printed, no client address printed.
# Usage: ./scripts/agent-access/check-app-firewall-blocks.sh [hours, default 24, max 720]
# Exit: 0 when no app request was blocked in the window, 1 when some were,
#       2 when the count could not be read.

set -euo pipefail

HOURS="${1:-24}"
if ! [[ "$HOURS" =~ ^[0-9]+$ ]] || (( HOURS < 1 || HOURS > 720 )); then
  echo "Usage: $0 [hours 1-720]" >&2
  exit 2
fi

CONF="${HOME}/.config/sifututor/agent-access/cloudflare-readonly.conf"
HOST="sifu-tutor.tutorla.tech"

echo "=== App firewall block check: ${HOST}, last ${HOURS}h ==="

if [[ ! -f "$CONF" ]]; then
  echo "  missing access file: cloudflare-readonly.conf"
  exit 2
fi

unset CLOUDFLARE_API_TOKEN CLOUDFLARE_ZONE_ID CF_API_TOKEN CF_ZONE_ID
set -a
# shellcheck disable=SC1090
. "$CONF"
set +a
TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-}}"
ZONE="${CLOUDFLARE_ZONE_ID:-${CF_ZONE_ID:-}}"
if [[ -z "$TOKEN" || -z "$ZONE" ]]; then
  echo "  access file has no token or zone"
  exit 2
fi

WORK="$(mktemp -d)"
trap 'rm -rf -- "$WORK"' EXIT

# Two small queries: every request (for the total) and only the blocked ones (with detail).
python3 - "$ZONE" "$HOURS" "$HOST" "$WORK" <<'PY'
import datetime, json, sys

zone, hours, host, work = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
until = datetime.datetime.now(datetime.timezone.utc)
since = until - datetime.timedelta(hours=hours)
fmt = "%Y-%m-%dT%H:%M:%SZ"
base = 'datetime_geq:"%s",datetime_leq:"%s",clientRequestHTTPHost:"%s",clientRequestPath_like:"/api/%%"' % (
    since.strftime(fmt), until.strftime(fmt), host)
wrap = '{viewer{zones(filter:{zoneTag:"%s"}){httpRequestsAdaptiveGroups(limit:9000,filter:{%s}){count dimensions{%s}}}}}'
queries = {
    "total": wrap % (zone, base, "datetimeHour"),
    "blocked": wrap % (zone, base + ",originResponseStatus:403", "datetimeHour clientRequestPath userAgent"),
}
for name, query in queries.items():
    with open(f"{work}/{name}.query.json", "w") as handle:
        json.dump({"query": query}, handle)
PY

for name in total blocked; do
  curl -s -m 60 -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
    --data @"${WORK}/${name}.query.json" -o "${WORK}/${name}.json" \
    https://api.cloudflare.com/client/v4/graphql || true
done

python3 - "$WORK" <<'PY'
import collections, datetime, json, sys

work = sys.argv[1]
data = {}
try:
    def groups(name):
        global data
        with open(f"{work}/{name}.json") as handle:
            data = json.load(handle)
        return data["data"]["viewer"]["zones"][0]["httpRequestsAdaptiveGroups"]
    total = sum(row["count"] for row in groups("total"))
    rows = groups("blocked")
except Exception:
    errors = []
    try:
        errors = [e.get("message", "")[:120] for e in (data.get("errors") or [])][:2]
    except Exception:
        pass
    print("  could not read the count", errors or "")
    sys.exit(2)

MYT = datetime.timedelta(hours=8)
blocked = 0
by_day = collections.Counter()
by_area = collections.Counter()
by_app = collections.Counter()
last_block = None
for row in rows:
    dims = row["dimensions"]
    agent = dims["userAgent"] or ""
    if "SifuParent" in agent:
        app = "Parent app"
    elif "sifututor" in agent.lower() or "SifuTutor" in agent:
        app = "Tutor app"
    elif "okhttp" in agent.lower() or "CFNetwork" in agent or "Dart" in agent:
        app = "app (generic client name)"
    else:
        continue  # browsers and scanners are challenged on purpose
    blocked += row["count"]
    when = datetime.datetime.strptime(dims["datetimeHour"][:13], "%Y-%m-%dT%H") + MYT
    by_day[when.strftime("%Y-%m-%d")] += row["count"]
    last_block = max(last_block, when) if last_block else when
    path = dims["clientRequestPath"]
    area = "/api/parent" if path.startswith("/api/parent") else (
        "/api/tutor" if path.startswith("/api/tutor") else "/api/other")
    by_area[area] += row["count"]
    by_app[app] += row["count"]

print(f"  API requests seen (sampled, lower bound): {total}")
print(f"  app requests blocked by the server (origin 403): {blocked}")
if blocked:
    print("  by day (MYT):", dict(sorted(by_day.items())))
    print("  by area:", dict(by_area.most_common()))
    print("  by app:", dict(by_app.most_common()))
    print("  last blocked hour (MYT):", last_block.strftime("%d %b %H:00"))
    print("  See sifu-tutor docs/deployment/incident-runbook.md, section 4E2.")
    sys.exit(1)
print("  OK: no app request was blocked.")
PY
