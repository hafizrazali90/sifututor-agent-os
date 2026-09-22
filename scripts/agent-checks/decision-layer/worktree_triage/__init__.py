# Package marker so `python3 -m unittest discover -s scripts/agent-checks/decision-layer -p 'test_*.py'`
# recurses into this folder. Without it, the triage tests were silently skipped
# by that command.
