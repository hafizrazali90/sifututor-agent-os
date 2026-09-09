#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
EXEC = ROOT / "tekun-executive-stakeholder-deck.md"
PROPOSAL = ROOT / "tekun-controlled-external-proposal.md"
INTERNAL = ROOT / "tekun-internal-technical-operations-deck.md"

errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

def pages(pdf):
    output = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    return int(re.search(r"^Pages:\s+(\d+)", output, re.M).group(1))

exec_text = EXEC.read_text()
proposal_text = PROPOSAL.read_text()
internal_text = INTERNAL.read_text()

exec_slides = re.split(r"\n---\n", exec_text)
internal_slides = re.split(r"\n---\n", internal_text)
require(len(exec_slides) == 18, "executive deck must contain 18 slides")
require(len(internal_slides) == 42, "internal deck must contain 42 slides")
require("# Internal next step" in internal_slides[34], "internal core decision must remain slide 35")
require(all("# Internal appendix:" in slide for slide in internal_slides[35:]), "slides 36–42 must remain optional internal appendices")
for number in range(1, 25):
    require(re.search(rf"^## {number}\. ", proposal_text, re.M) is not None, f"proposal section {number} is missing")

claim_pattern = re.compile(r"\b(?:CLM|HIS|ARCH|SYS|NAR|TRU|RES)-[A-Z0-9-]+\b")
require(not claim_pattern.search(exec_text), "executive deck exposes an internal claim ID")
require(not claim_pattern.search(proposal_text), "controlled proposal exposes an internal claim ID")

expected_visuals = {
    EXEC: {"diagram-2.svg", "diagram-4.svg", "diagram-6.svg", "diagram-12.svg", "diagram-14.svg", "diagram-15.svg"},
    PROPOSAL: {"diagram-1.svg", "diagram-3.svg", "diagram-4.svg", "diagram-6.svg", "diagram-8.svg", "diagram-11.svg", "diagram-12.svg", "diagram-14.svg"},
    INTERNAL: {"diagram-1.svg", "diagram-2.svg", "diagram-4.svg", "diagram-6.svg", "diagram-8.svg", "diagram-10.svg", "diagram-11.svg", "diagram-12.svg"},
}
for source, expected in expected_visuals.items():
    actual = set(re.findall(r"diagram-\d+\.svg", source.read_text()))
    require(actual == expected, f"{source.name} diagram set differs: expected {sorted(expected)}, got {sorted(actual)}")

require(pages(ROOT / "tekun-executive-stakeholder-deck.pdf") == 18, "executive PDF page count is not 18")
require(20 <= pages(ROOT / "tekun-controlled-external-proposal.pdf") <= 30, "proposal PDF must remain 20–30 pages")
require(pages(ROOT / "tekun-internal-technical-operations-deck.pdf") == 42, "internal PDF page count is not 42")

docx = ROOT / "tekun-controlled-external-proposal.docx"
try:
    with zipfile.ZipFile(docx) as archive:
        require(archive.testzip() is None, "proposal DOCX archive contains a corrupt member")
        require("word/document.xml" in archive.namelist(), "proposal DOCX lacks word/document.xml")
except (FileNotFoundError, zipfile.BadZipFile) as exc:
    errors.append(f"proposal DOCX invalid: {exc}")

for stem in ["tekun-executive-stakeholder-deck", "tekun-internal-technical-operations-deck"]:
    require((ROOT / f"{stem}.html").exists(), f"{stem}.html is missing")
    require((ROOT / f"{stem}.pdf").exists(), f"{stem}.pdf is missing")
    require((ROOT / f"{stem}.html").stat().st_mtime >= (ROOT / f"{stem}.md").stat().st_mtime, f"{stem}.html is stale")
    require((ROOT / f"{stem}.pdf").stat().st_mtime >= (ROOT / f"{stem}.md").stat().st_mtime, f"{stem}.pdf is stale")
for suffix in ["md", "html", "pdf", "docx"]:
    require((ROOT / f"tekun-controlled-external-proposal.{suffix}").exists(), f"proposal {suffix} is missing")
for suffix in ["html", "pdf", "docx"]:
    require((ROOT / f"tekun-controlled-external-proposal.{suffix}").stat().st_mtime >= PROPOSAL.stat().st_mtime, f"proposal {suffix} is stale")

if errors:
    print("Derivative package check: FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Derivative package check: PASS")
print("- executive deck: 18 slides")
print(f"- controlled proposal: {pages(ROOT / 'tekun-controlled-external-proposal.pdf')} A4 pages")
print("- internal technical/operations deck: 35-slide core + 7-slide appendix")
print("- external claim IDs: none")
print("- diagram mappings: exact")
print("- editable and rendered outputs: present")
print("- DOCX archive: valid")
