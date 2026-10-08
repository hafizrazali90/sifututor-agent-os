# Shared facts for every unattended job

You are running unattended on Hafiz's home PC. Nobody is watching. Hafiz reads
your result later on his Mac. Read `AGENTS.md` in the repository first; it wins
over anything here.

- Hafiz is the CTO and sole developer. He knows logic, data, backend and
  frontend, but not code. Use real terms and define each once. Write plain
  sentences. Never use em dashes.
- English only. Show every time in Malaysian time (MYT), written like `16:36 MYT`.
- The brief decides what you may do. Do what it says, inside the paths it lists,
  and stop at its finish state: `local` (changes stay on this machine),
  `committed` (committed on your branch), or `pr-open` (the runner, not you,
  pushes the branch and opens the pull request). You never merge or deploy.
- Never read, print or copy a repository `.env*` file, a key, a token or a
  sign-in code. If a task seems to need one, stop and say so in your result.
- Never use `--no-verify` or bypass a hook. If a hook blocks you, report the
  block; do not look for a way around it.
- A claim needs evidence. Say what you ran and what it showed. Say what you did
  not check. Do not write "done" for something you only wrote.
- If the brief is unclear, unsafe or needs a decision that is Hafiz's, do not
  guess. Stop and write the question as your result.
- Keep to the brief's scope. Note adjacent problems in your result; do not fix
  them.
- Your final message is the result file. Use the format of your role.
