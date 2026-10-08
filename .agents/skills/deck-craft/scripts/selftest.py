#!/usr/bin/env python3
"""Self-test for the deck-craft toolkit: the example deck builds and passes the
lint, and a half-empty card is caught. Needs Google Chrome. Run from anywhere."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
EXAMPLE = SCRIPTS.parent / "templates" / "example"


def run(deck, *args):
    return subprocess.run([sys.executable, *args], cwd=deck, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    deck = Path(tmp) / "deck"
    shutil.copytree(EXAMPLE, deck)
    b = run(deck, str(SCRIPTS / "build.py"), "--render")
    assert b.returncode == 0 and (deck / "png" / "flow.png").exists(), b.stdout + b.stderr
    good = run(deck, str(SCRIPTS / "lint.py"))
    assert good.returncode == 0 and "LINT PASS" in good.stdout, "example should pass:\n" + good.stdout
    src = (deck / "slides_example.py").read_text()
    hollow = src.replace("+ panel,", ",")
    assert hollow != src, "example changed: update the hollow mutation"
    (deck / "slides_example.py").write_text(hollow)
    run(deck, str(SCRIPTS / "build.py"), "--render")
    bad = run(deck, str(SCRIPTS / "lint.py"))
    assert bad.returncode == 1 and "HOLLOW" in bad.stdout, "half-empty cards should fail:\n" + bad.stdout
print("SELFTEST PASS: example passes, half-empty cards are caught")
