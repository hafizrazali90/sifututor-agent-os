# Koda Memory — Staff Onboarding Guide

Koda is our shared team memory system. When you work in VS Code with Claude Code, Koda automatically stores important decisions and lessons from your session so the whole team benefits.

This guide gets you connected in about 5 minutes.

---

## Step 1 — Get your API key from Hafiz

Ask Hafiz for your personal Koda API key. It looks like this:

```
koda_a1b2c3d4e5f6...
```

Each person has a unique key. Do not share it or commit it to any file.

---

## Step 2 — Add the key to your shell profile

Open your terminal and run:

```bash
echo 'export KODA_API_KEY=YOUR_KEY_HERE' >> ~/.zshrc
source ~/.zshrc
```

> If you use bash instead of zsh, replace `~/.zshrc` with `~/.bashrc`.

Replace `YOUR_KEY_HERE` with the actual key Hafiz gave you.

---

## Step 3 — Configure VS Code / Codex

Open (or create) the file `~/.codex/config.toml` and add this block:

```toml
[mcp_servers.memory]
command = "npx"
args = ["-y", "supergateway", "--streamableHttp", "https://koda.tutorla.tech/mcp"]

[mcp_servers.memory.env]
KODA_API_KEY = "${KODA_API_KEY}"
```

> **Restart VS Code** after saving this file so it picks up the new MCP server.

---

## Step 4 — Verify your connection

In your VS Code terminal, navigate to the Sifututor project root and run:

```bash
python3 scripts/agent-checks/koda-verify.py
```

If everything is set up correctly you will see:

```
==================================================
  Koda Setup Verifier — Sifututor Team
==================================================

Step 1 — Checking KODA_API_KEY
  ✓ KODA_API_KEY is set (koda_a1b2...)

Step 2 — Connecting to Koda
  ✓ Connected — session abc123...

Step 3 — Verifying required tools
  ✓ All required tools available (16 total)

Step 4 — Sending setup confirmation to Hafiz
  ✓ Confirmation sent — memory mem_xxxxxxxxxxxx

==================================================
  ALL CHECKS PASSED — Your Koda setup is working!
==================================================

  Hafiz can see your confirmation at:
  https://koda.tutorla.tech/dashboard
```

This script stores a confirmation in Koda so Hafiz knows your setup is working. **Run it once after setup** — that's all.

---

## Troubleshooting

**`KODA_API_KEY is not set`**
- You skipped Step 2, or the terminal session hasn't picked up the new variable yet.
- Run `source ~/.zshrc` and try again.

**`Could not connect to Koda`**
- Check that your API key is exactly as Hafiz gave it (no extra spaces).
- Make sure you have internet access.
- If the error says `HTTP 401`, your key may be wrong — contact Hafiz.

**`python3: command not found`**
- Install Python 3: `brew install python3`

---

## What happens next

Once connected, Koda works automatically in the background. When Claude Code starts a session, it reads relevant memories. When you end a session with `/save-session`, it stores lessons learned.

You can view all team memories at [koda.tutorla.tech/dashboard](https://koda.tutorla.tech/dashboard) using the login credentials Hafiz provides.

---

*Questions? Message Hafiz on WhatsApp or Teams.*
