#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd "$script_dir/../.." && pwd)"
derivatives="$workspace_root/docs/tekun-collection-derivatives"
research="$workspace_root/docs/tekun-collection-research"
plan="$workspace_root/docs/tekun-collection-plan"
pack_tmp="$(mktemp -d /tmp/tekun-partnership-pack.XXXXXX)"
internal_dir="$pack_tmp/internal"
external_dir="$pack_tmp/external"

cleanup() {
  case "$pack_tmp" in
    /tmp/tekun-partnership-pack.*) rm -rf -- "$pack_tmp" ;;
  esac
}
trap cleanup EXIT

node "$derivatives/render-proposal.mjs" \
  "$script_dir/TEKUN-PARTNERSHIP-PACK-START-HERE.md" \
  "$script_dir/TEKUN-PARTNERSHIP-PACK-START-HERE.html"
node "$derivatives/render-proposal-pdf.cjs" \
  "$script_dir/TEKUN-PARTNERSHIP-PACK-START-HERE.html" \
  "$script_dir/TEKUN-PARTNERSHIP-PACK-START-HERE.pdf"
node "$derivatives/render-proposal.mjs" \
  "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.md" \
  "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.html"
node "$derivatives/render-proposal-pdf.cjs" \
  "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.html" \
  "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.pdf"

mkdir -p \
  "$internal_dir/00-START-HERE" \
  "$internal_dir/01-Executive-Decision" \
  "$internal_dir/02-Controlled-External-Proposal" \
  "$internal_dir/03-Internal-Technical-Operations" \
  "$internal_dir/04-Governed-Sourcebook" \
  "$internal_dir/05-Research-Evidence" \
  "$internal_dir/06-Planning-Governance" \
  "$external_dir/00-READ-ME-FIRST" \
  "$external_dir/01-Executive-Presentation" \
  "$external_dir/02-Controlled-Proposal"

sed \
  -e 's#../tekun-collection-derivatives/tekun-executive-stakeholder-deck.html#../01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.html#g' \
  -e 's#../tekun-collection-derivatives/tekun-executive-stakeholder-deck.pdf#../01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.pdf#g' \
  -e 's#../tekun-collection-derivatives/tekun-executive-stakeholder-deck.md#../01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.md#g' \
  -e 's#../tekun-collection-derivatives/tekun-controlled-external-proposal.pdf#../02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.pdf#g' \
  -e 's#../tekun-collection-derivatives/tekun-controlled-external-proposal.docx#../02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.docx#g' \
  -e 's#../tekun-collection-derivatives/tekun-controlled-external-proposal.md#../02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.md#g' \
  -e 's#../tekun-collection-derivatives/tekun-internal-technical-operations-deck.pdf#../03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.pdf#g' \
  -e 's#../tekun-collection-derivatives/tekun-internal-technical-operations-deck.html#../03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.html#g' \
  -e 's#../tekun-collection-derivatives/tekun-internal-technical-operations-deck.md#../03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.md#g' \
  -e 's#../tekun-collection-partnership-sourcebook.pdf#../04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.pdf#g' \
  -e 's#../tekun-collection-partnership-sourcebook.docx#../04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.docx#g' \
  -e 's#../tekun-collection-partnership-sourcebook.md#../04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.md#g' \
  -e 's#../tekun-collection-research/research-handback.md#../05-Research-Evidence/research-handback.md#g' \
  -e 's#../tekun-collection-research/executive-research-brief.md#../05-Research-Evidence/executive-research-brief.md#g' \
  -e 's#../tekun-collection-research/claim-register.md#../05-Research-Evidence/claim-register.md#g' \
  -e 's#../tekun-collection-research/source-register.md#../05-Research-Evidence/source-register.md#g' \
  "$script_dir/TEKUN-PARTNERSHIP-PACK-START-HERE.md" \
  > "$internal_dir/00-START-HERE/TEKUN-Partnership-Pack-Start-Here.md"
node "$derivatives/render-proposal.mjs" \
  "$internal_dir/00-START-HERE/TEKUN-Partnership-Pack-Start-Here.md" \
  "$internal_dir/00-START-HERE/TEKUN-Partnership-Pack-Start-Here.html"
node "$derivatives/render-proposal-pdf.cjs" \
  "$internal_dir/00-START-HERE/TEKUN-Partnership-Pack-Start-Here.html" \
  "$internal_dir/00-START-HERE/TEKUN-Partnership-Pack-Start-Here.pdf"
cp "$derivatives/tekun-executive-stakeholder-deck.pdf" "$internal_dir/01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.pdf"
cp "$derivatives/tekun-executive-stakeholder-deck.html" "$internal_dir/01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.html"
cp "$derivatives/tekun-executive-stakeholder-deck.md" "$internal_dir/01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.md"
cp "$derivatives/tekun-controlled-external-proposal.pdf" "$internal_dir/02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.pdf"
cp "$derivatives/tekun-controlled-external-proposal.docx" "$internal_dir/02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.docx"
cp "$derivatives/tekun-controlled-external-proposal.md" "$internal_dir/02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.md"
cp "$derivatives/tekun-internal-technical-operations-deck.pdf" "$internal_dir/03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.pdf"
cp "$derivatives/tekun-internal-technical-operations-deck.html" "$internal_dir/03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.html"
cp "$derivatives/tekun-internal-technical-operations-deck.md" "$internal_dir/03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.md"
cp "$workspace_root/docs/tekun-collection-partnership-sourcebook.pdf" "$internal_dir/04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.pdf"
cp "$workspace_root/docs/tekun-collection-partnership-sourcebook.docx" "$internal_dir/04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.docx"
cp "$workspace_root/docs/tekun-collection-partnership-sourcebook.md" "$internal_dir/04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.md"
cp "$research"/*.md "$internal_dir/05-Research-Evidence/"
cp "$plan"/*.md "$internal_dir/06-Planning-Governance/"
cp "$derivatives/derivative-contract.md" "$derivatives/extraction-matrix.md" "$derivatives/review-and-acceptance.md" "$internal_dir/06-Planning-Governance/"

cp "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.md" "$external_dir/00-READ-ME-FIRST/TEKUN-Controlled-External-Review-Pack-Read-Me.md"
cp "$script_dir/TEKUN-CONTROLLED-EXTERNAL-REVIEW-PACK-READ-ME.pdf" "$external_dir/00-READ-ME-FIRST/TEKUN-Controlled-External-Review-Pack-Read-Me.pdf"
cp "$derivatives/tekun-executive-stakeholder-deck.pdf" "$external_dir/01-Executive-Presentation/TEKUN-Executive-Stakeholder-Presentation.pdf"
cp "$derivatives/tekun-executive-stakeholder-deck.html" "$external_dir/01-Executive-Presentation/TEKUN-Executive-Stakeholder-Presentation.html"
cp "$derivatives/tekun-controlled-external-proposal.pdf" "$external_dir/02-Controlled-Proposal/TEKUN-Controlled-External-Proposal.pdf"
cp "$derivatives/tekun-controlled-external-proposal.docx" "$external_dir/02-Controlled-Proposal/TEKUN-Controlled-External-Proposal.docx"

(cd "$internal_dir" && find . -type f ! -name SHA256SUMS.txt -exec shasum -a 256 {} \; | sort > SHA256SUMS.txt)
(cd "$external_dir" && find . -type f ! -name SHA256SUMS.txt -exec shasum -a 256 {} \; | sort > SHA256SUMS.txt)
(cd "$internal_dir" && zip -qr "$pack_tmp/internal.zip" .)
(cd "$external_dir" && zip -qr "$pack_tmp/external.zip" .)

mv "$pack_tmp/internal.zip" "$script_dir/TEKUN-Partnership-Complete-Internal-Pack-2026-09-01.zip"
mv "$pack_tmp/external.zip" "$script_dir/TEKUN-Partnership-Controlled-External-Review-Pack-2026-09-01.zip"

python3 "$script_dir/check-compiled-packs.py"
