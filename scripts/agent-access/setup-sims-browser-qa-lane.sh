#!/usr/bin/env bash
# Create the private file for lane 39 (sims-staging-browser-qa).
# Hafiz runs this himself in a terminal. An agent must never run it or see what
# is typed: the password is read with echo off and is never printed.
#
# Usage: scripts/agent-access/setup-sims-browser-qa-lane.sh
# Test override: SIFUTUTOR_AGENT_ACCESS_DIR=<dir> changes where the file is written.

set -euo pipefail

CONF_DIR="${SIFUTUTOR_AGENT_ACCESS_DIR:-${HOME}/.config/sifututor/agent-access}"
CONF="$CONF_DIR/sims-staging-browser-qa.conf"
DEFAULT_URL="https://sifu-staging.tutorla.tech"

if [[ ! -t 0 ]]; then
  echo "This script needs a real terminal so the password can be typed with echo off." >&2
  echo "Run it yourself in a terminal. Do not pipe input into it." >&2
  exit 2
fi

umask 077
EMAIL=""
PASSWORD=""
CONFIRM=""
cleanup() {
  unset EMAIL PASSWORD CONFIRM
  if [[ -n "${TMP:-}" ]]; then rm -f "$TMP"; fi
}
trap cleanup EXIT

if [[ -e "$CONF" ]]; then
  printf 'A file already exists at %s\nReplace it? [y/N] ' "$CONF"
  read -r ANSWER
  if [[ "$ANSWER" != "y" && "$ANSWER" != "Y" ]]; then
    echo "Kept the existing file. Nothing changed."
    exit 0
  fi
fi

printf 'Staging URL [%s]: ' "$DEFAULT_URL"
read -r BASE_URL
BASE_URL="${BASE_URL:-$DEFAULT_URL}"
if [[ "$BASE_URL" != https://*staging* || "$BASE_URL" == *sifututor.my* ]]; then
  echo "This lane is for staging only. The URL must start with https:// and name a staging host." >&2
  exit 1
fi

printf 'Browser QA account email: '
read -r EMAIL
if [[ -z "$EMAIL" || "$EMAIL" != *@* || "$EMAIL" == *[[:space:]]* ]]; then
  echo "That does not look like an email address." >&2
  exit 1
fi

printf 'Password (hidden): '
read -rs PASSWORD
printf '\n'
printf 'Password again (hidden): '
read -rs CONFIRM
printf '\n'
if [[ -z "$PASSWORD" ]]; then
  echo "The password is empty. Nothing written." >&2
  exit 1
fi
if [[ "$PASSWORD" != "$CONFIRM" ]]; then
  echo "The two passwords differ. Nothing written." >&2
  exit 1
fi

if [[ ! -d "$CONF_DIR" ]]; then
  mkdir -p "$CONF_DIR"
  chmod 700 "$CONF_DIR"
fi
TMP="$(mktemp "$CONF_DIR/.sims-staging-browser-qa.XXXXXX")"
{
  printf 'SIMS_BROWSER_QA_BASE_URL=%q\n' "$BASE_URL"
  printf 'SIMS_BROWSER_QA_EMAIL=%q\n' "$EMAIL"
  printf 'SIMS_BROWSER_QA_PASSWORD=%q\n' "$PASSWORD"
} > "$TMP"
chmod 600 "$TMP"
mv "$TMP" "$CONF"
TMP=""

echo "Saved $CONF (mode 600)."
echo "It holds: SIMS_BROWSER_QA_BASE_URL, SIMS_BROWSER_QA_EMAIL, SIMS_BROWSER_QA_PASSWORD."
echo "Check it with: scripts/agent-access/agent-access-doctor.sh"
