#!/bin/zsh
# Rebuild the deck and run the check suites. Usage: runall.sh [desktop|phone|pdf|all|build]
set -e
S=/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/build
D=/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude
W=${1:-all}
python3 $S/builddeck2.py
python3 /Users/hafizrazali/Projects/Sifututor/.claude/skills/doc-design/scripts/build.py $D/kota-buku-deck.template.html $D/kota-buku-deck.html 2>&1 | tail -1
python3 $S/share.py
cd /Users/hafizrazali/Projects/Sifututor/kelas
if [[ $W == all ]]; then rm -f $D/screenshots/deck/*.png; fi
if [[ $W == all || $W == desktop ]]; then
  node $S/shotdeck.js > $S/deck-run.json 2>&1 || true
  python3 - <<'EOF'
import json, re
p = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/build/deck-run.json'
raw = open(p).read()
try:
    j = json.loads(raw)
except Exception:
    print(raw[:2500]); raise SystemExit
n = 0
for r in j['results']:
    bad = [b for b in r['bad'] if not re.search(r'photo blk', b)]
    if bad:
        print(r['l'], bad); n += len(bad)
print('desktop findings', n, 'errors', j['errors'], 'identical', j['identical'])
print('ix', json.dumps(j['ix'], ensure_ascii=False)[:900])
print('nav', j['nav'])
EOF
fi
if [[ $W == all || $W == phone ]]; then
  echo ---- phone; node $S/shotdeckm.js 2>&1 | grep -v '^   "' | head -60
fi
if [[ $W == all || $W == pdf ]]; then
  echo ---- pdf; node $S/pdfdeck.js 2>&1 | grep -v '"credit"' | head -40
fi
