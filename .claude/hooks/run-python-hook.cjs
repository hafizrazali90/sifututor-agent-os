#!/usr/bin/env node
// AGENT-OS-CLAUDE-HOOK-DISPATCHER
// Umbrella wrapper for sub-projects whose settings call
// `node .claude/hooks/run-python-hook.cjs <script.py>` (sifu-tutor). It only
// names its hook and hands over; the sub-project's own launcher does the work.
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "../..");
const dispatcher = path.join(root, "scripts/agent-checks/claude_hook_dispatch.py");
const result = spawnSync(
  "python3",
  [dispatcher, "--dispatch-hook", path.basename(__filename), "--self-path", __filename, "--", ...process.argv.slice(2)],
  { cwd: root, input: fs.readFileSync(0), stdio: ["pipe", "inherit", "inherit"] },
);

if (result.error) {
  process.stderr.write(`[agent-os] claude hook dispatch: ${path.basename(__filename)} dispatcher could not start; reporting an error\n`);
  process.exit(1);
}
process.exit(result.status ?? 1);
