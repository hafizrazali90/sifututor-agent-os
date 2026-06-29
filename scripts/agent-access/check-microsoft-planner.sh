#!/usr/bin/env bash
# Check Microsoft 365 / Teams Planner access availability
# Uses Lokka MCP binary or m365-readonly.env config
# Safe: no tokens printed
# Usage: ./scripts/agent-access/check-microsoft-planner.sh

set -euo pipefail

echo "=== Microsoft 365 / Teams Planner Check ==="
echo ""

# 1. Check m365-readonly.env
M365_ENV="${HOME}/.config/sifututor/m365-readonly.env"
if [[ -f "$M365_ENV" ]]; then
  KEYS=$(grep -c '^[A-Za-z]' "$M365_ENV" 2>/dev/null || echo 0)
  printf '\033[32m✓\033[0m m365-readonly.env: present (%s config lines)\n' "$KEYS"
else
  printf '\033[31m✗\033[0m m365-readonly.env: missing (%s)\n' "$M365_ENV"
fi

# 2. Check Lokka binary
LOKKA_BIN="${HOME}/.codex/bin/m365-lokka-from-agent-access.sh"
if [[ -x "$LOKKA_BIN" ]]; then
  printf '\033[32m✓\033[0m Lokka binary: present and executable (%s)\n' "$LOKKA_BIN"
else
  printf '\033[31m✗\033[0m Lokka binary: missing or not executable (%s)\n' "$LOKKA_BIN"
fi

echo ""
echo "── Access method by agent ──"
echo "  Claude Code: mcp__microsoft365__Lokka-Microsoft (MCP server)"
echo "  Codex:       \$HOME/.codex/bin/m365-lokka-from-agent-access.sh"
echo "  Both:        Read-only intake from Teams Planner 'Development & Support > Task Management Board'"
echo ""
echo "── What this access provides ──"
echo "  • List Planner tasks (staff-reported issues, support tickets, TREQs)"
echo "  • Read task details, descriptions, assignees, status"
echo "  • Cross-reference with SIMS / mobile app bugs before engineering work"
echo ""
echo "── What is NOT allowed ──"
echo "  • No updating Planner cards (state, assignment, priority)"
echo "  • No posting to Teams channels"
echo "  • No accessing mailboxes or calendars"
echo "  • Intake and read-only routing only"
echo ""

# 3. Try a quick read-only connectivity test through the Agent OS probe
PROBE="${PWD}/scripts/agent-checks/agent-os-planner-probe.py"
if [[ -x "$PROBE" ]]; then
  echo "── Connectivity test ──"
  if "$PROBE" >/tmp/agent-os-planner-probe.out 2>/tmp/agent-os-planner-probe.err; then
    printf '\033[32m✓\033[0m Microsoft Graph Planner probe: responsive\n'
    sed -n '1,12p' /tmp/agent-os-planner-probe.out | sed 's/^/  /'
  else
    printf '\033[33m~\033[0m Microsoft Graph Planner probe: unavailable or timed out\n'
    sed -n '1,8p' /tmp/agent-os-planner-probe.out 2>/dev/null | sed 's/^/  /'
    sed -n '1,4p' /tmp/agent-os-planner-probe.err 2>/dev/null | sed 's/^/  /'
  fi
  rm -f /tmp/agent-os-planner-probe.out /tmp/agent-os-planner-probe.err
else
  echo "── Connectivity test ──"
  printf '\033[33m~\033[0m Agent OS Planner probe missing (%s)\n' "$PROBE"
fi
