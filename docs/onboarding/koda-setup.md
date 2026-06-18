# Koda Memory Setup for Developers

When you use Claude Code to build features, fix bugs, or debug issues — Claude forgets everything the moment the session ends. Next session it starts from zero.

**Koda fixes that.**

It's a memory server that runs alongside Claude. When it's connected:
- Claude remembers past decisions you made together ("we use X pattern for this")
- Claude recalls gotchas and bugs you've already solved ("don't do Y, it breaks Z")
- Claude applies lessons from your previous sessions without you having to explain context again

**Setup takes 5 minutes.** You need your personal key from Hafiz before starting.

---

## Step 1 — Get your key

Ask Hafiz for your personal Koda API key. He will send it to you privately via DM.

---

## Step 2 — Connect Koda to Claude Code

Copy the prompt below, replace `YOUR_KEY_HERE` with the key Hafiz gave you, then paste it into Claude Code.

```
Set up Koda memory MCP for my Claude Code session.

My Koda API key is: YOUR_KEY_HERE

Do the following:
1. Read ~/.mcp.json (create it if it doesn't exist — use {} as the base)
2. Add or merge this server block under "mcpServers":
   {
     "memory": {
       "type": "http",
       "url": "https://koda.tutorla.tech/mcp",
       "headers": {
         "Authorization": "Bearer YOUR_KEY_HERE"
       }
     }
   }
   If a "memory" key already exists, replace it with this one.
3. Write the updated file back to ~/.mcp.json
4. Confirm what was written.
```

---

## Step 3 — Enforce the workflow in Claude

Paste this into Claude Code as-is (no changes needed):

```
Add the following block to my ~/.claude/CLAUDE.md file
(create the file if it doesn't exist, append if it does):

---

## Koda Memory — Always On

I have a Koda memory server connected via the "memory" MCP.
Use it every session without being asked.

At the start of any non-trivial task — call memory_search
with the task description before doing anything. Surface
relevant past decisions or lessons and mention them.

When I correct you ("no, that's wrong", "actually we do X",
"stop doing Y") — immediately call memory_store with the
correction. Don't wait for end of session.

When you discover something non-obvious mid-session — store
it immediately (a gotcha, a workaround, a broken pattern).

At end of session — I will type /save-session. Flush
everything worth keeping to Koda before stopping.

Skip Koda for trivial tasks (typo fix, rename, format).

---
```

---

## Step 4 — Restart Claude Code

Close and reopen Claude Code completely so it picks up the new MCP config.

---

## Step 5 — Verify it works

Paste this into Claude Code to confirm everything is connected:

```
Verify my Koda memory setup:

1. Call memory_store with content "koda setup verified", 
   category "fact", tags ["test"]
2. Call memory_search with query "koda setup verified"
3. Tell me if you found the memory you just stored.
4. Then delete or note it as a test entry.

If any step fails, show me the exact error.
```

Claude should store the memory, find it in the search, and confirm success. If it errors, send the error message to Hafiz.

---

## Daily habit

At the end of every coding session, type:

```
/save-session
```

That's the only active thing you need to do. Everything else is automatic.
