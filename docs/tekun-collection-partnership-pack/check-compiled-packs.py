#!/usr/bin/env python3
from pathlib import Path
import hashlib
import posixpath
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parent
INTERNAL = ROOT / "TEKUN-Partnership-Complete-Internal-Pack-2026-09-01.zip"
EXTERNAL = ROOT / "TEKUN-Partnership-Controlled-External-Review-Pack-2026-09-01.zip"

EXPECTED_INTERNAL = {
    "00-START-HERE/TEKUN-Partnership-Pack-Start-Here.md",
    "00-START-HERE/TEKUN-Partnership-Pack-Start-Here.html",
    "00-START-HERE/TEKUN-Partnership-Pack-Start-Here.pdf",
    "01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.pdf",
    "01-Executive-Decision/TEKUN-Executive-Stakeholder-Presentation.html",
    "02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.pdf",
    "02-Controlled-External-Proposal/TEKUN-Controlled-External-Proposal.docx",
    "03-Internal-Technical-Operations/TEKUN-Internal-Technical-Operations-Deck.pdf",
    "04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.pdf",
    "04-Governed-Sourcebook/TEKUN-Collection-Partnership-Sourcebook.docx",
    "05-Research-Evidence/research-handback.md",
    "05-Research-Evidence/claim-register.md",
    "05-Research-Evidence/source-register.md",
    "06-Planning-Governance/derivative-contract.md",
    "06-Planning-Governance/extraction-matrix.md",
    "06-Planning-Governance/review-and-acceptance.md",
    "SHA256SUMS.txt",
}

EXPECTED_EXTERNAL = {
    "00-READ-ME-FIRST/TEKUN-Controlled-External-Review-Pack-Read-Me.md",
    "00-READ-ME-FIRST/TEKUN-Controlled-External-Review-Pack-Read-Me.pdf",
    "01-Executive-Presentation/TEKUN-Executive-Stakeholder-Presentation.pdf",
    "01-Executive-Presentation/TEKUN-Executive-Stakeholder-Presentation.html",
    "02-Controlled-Proposal/TEKUN-Controlled-External-Proposal.pdf",
    "02-Controlled-Proposal/TEKUN-Controlled-External-Proposal.docx",
    "SHA256SUMS.txt",
}

FORBIDDEN_EXTERNAL_PARTS = {
    "Internal-Technical",
    "Sourcebook",
    "Research-Evidence",
    "claim-register",
    "source-register",
    "Governance",
}


def check_zip(path: Path, expected: set[str]) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing archive: {path.name}"], set()
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt = archive.testzip()
            if corrupt:
                errors.append(f"{path.name} contains corrupt member: {corrupt}")
            names = {name for name in archive.namelist() if not name.endswith("/")}
            manifest = archive.read("SHA256SUMS.txt").decode("utf-8")
            for line in manifest.splitlines():
                digest, member = line.split(maxsplit=1)
                member = member.removeprefix("./")
                if member not in names:
                    errors.append(f"{path.name} checksum member is missing: {member}")
                    continue
                actual = hashlib.sha256(archive.read(member)).hexdigest()
                if actual != digest:
                    errors.append(f"{path.name} checksum mismatch: {member}")
    except zipfile.BadZipFile:
        return [f"invalid ZIP archive: {path.name}"], set()
    missing = expected - names
    if missing:
        errors.append(f"{path.name} missing: {sorted(missing)}")
    return errors, names


errors, internal_names = check_zip(INTERNAL, EXPECTED_INTERNAL)
external_errors, external_names = check_zip(EXTERNAL, EXPECTED_EXTERNAL)
errors.extend(external_errors)

if INTERNAL.exists():
    with zipfile.ZipFile(INTERNAL) as archive:
        guide_name = "00-START-HERE/TEKUN-Partnership-Pack-Start-Here.md"
        guide = archive.read(guide_name).decode("utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", guide):
            if target.startswith(("http://", "https://", "#")):
                continue
            normalised = posixpath.normpath(posixpath.join(posixpath.dirname(guide_name), target))
            if normalised not in internal_names:
                errors.append(f"internal Start Here link target is missing: {target}")

for forbidden in FORBIDDEN_EXTERNAL_PARTS:
    leaked = sorted(name for name in external_names if forbidden.lower() in name.lower())
    if leaked:
        errors.append(f"external pack exposes internal material matching {forbidden}: {leaked}")

if errors:
    print("Compiled partnership pack check: FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Compiled partnership pack check: PASS")
print(f"- internal pack: {len(internal_names)} files")
print(f"- controlled external pack: {len(external_names)} files")
print("- required documents: present")
print("- archive integrity: valid")
print("- packaged checksums and Start Here links: valid")
print("- internal-only material in external pack: none")
