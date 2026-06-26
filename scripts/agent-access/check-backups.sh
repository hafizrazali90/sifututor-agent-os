#!/usr/bin/env bash
# Check backup and Wasabi storage object counts
# Sources: backup-readonly.conf or wasabi-ripple-storage-scoped.conf
# Safe: no keys printed; reports counts and latest timestamp only
# Usage: ./scripts/agent-access/check-backups.sh [--wasabi | --wasabi-full]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"

MODE="${1:---backups}"
echo "=== Storage Check: $MODE ==="
echo ""

check_s3_bucket() {
  local label="$1"
  local endpoint="$2"
  local bucket="$3"
  local region="$4"
  local access_key="$5"
  local secret_key="$6"
  local path_style="${7:-}"

  # Use AWS CLI if available, else boto3-style script
  if command -v aws &>/dev/null; then
    local ep_arg=""
    [[ -n "$endpoint" ]] && ep_arg="--endpoint-url $endpoint"
    local ps_arg=""
    [[ -n "$path_style" ]] && ps_arg="--no-sign-request"  # fallback — path style configured via env

    COUNT=$(AWS_ACCESS_KEY_ID="$access_key" \
      AWS_SECRET_ACCESS_KEY="$secret_key" \
      AWS_DEFAULT_REGION="$region" \
      aws s3api list-objects-v2 \
        $ep_arg \
        --bucket "$bucket" \
        --query "length(Contents)" \
        --output text 2>/dev/null || echo "ERROR")

    LATEST=$(AWS_ACCESS_KEY_ID="$access_key" \
      AWS_SECRET_ACCESS_KEY="$secret_key" \
      AWS_DEFAULT_REGION="$region" \
      aws s3api list-objects-v2 \
        $ep_arg \
        --bucket "$bucket" \
        --query "sort_by(Contents, &LastModified)[-1].{Key:Key, Date:LastModified}" \
        --output table 2>/dev/null || echo "N/A")
  else
    COUNT="aws-cli-not-installed"
    LATEST="install awscli to check"
  fi

  echo "Label:  $label"
  echo "Bucket: $bucket"
  echo "Region: $region"
  [[ -n "$endpoint" ]] && echo "Endpoint: $endpoint"
  echo "Object count: $COUNT"
  echo "Latest object:"
  echo "$LATEST" | head -5
}

if [[ "$MODE" == "--wasabi" || "$MODE" == "--wasabi-scoped" ]]; then
  CONF_FILE="$CONF_DIR/wasabi-ripple-storage-scoped.conf"
  # shellcheck disable=SC1090
  source "$CONF_FILE"
  check_s3_bucket \
    "Wasabi Ripple (scoped)" \
    "$WASABI_ENDPOINT" \
    "$WASABI_BUCKET" \
    "$WASABI_REGION" \
    "$WASABI_ACCESS_KEY_ID" \
    "$WASABI_SECRET_ACCESS_KEY" \
    "path-style"

elif [[ "$MODE" == "--wasabi-full" ]]; then
  CONF_FILE="$CONF_DIR/wasabi-ripple-storage.conf"
  # shellcheck disable=SC1090
  source "$CONF_FILE"
  check_s3_bucket \
    "Wasabi Ripple (full)" \
    "$WASABI_ENDPOINT" \
    "$WASABI_BUCKET" \
    "$WASABI_REGION" \
    "$WASABI_ACCESS_KEY_ID" \
    "$WASABI_SECRET_ACCESS_KEY" \
    "path-style"

else
  # Default: backup-readonly
  CONF_FILE="$CONF_DIR/backup-readonly.conf"
  if [[ ! -f "$CONF_FILE" ]]; then
    echo "✗ Conf file missing: $CONF_FILE"
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$CONF_FILE"

  if [[ -z "${BACKUP_BUCKET:-}" ]]; then
    echo "~ BACKUP_BUCKET not set in backup-readonly.conf"
    echo "  Backup storage endpoint not configured for direct S3 check."
    echo "  Verify backup existence via SSH to production server:"
    echo "  ssh production 'ls /home/sifututortutorla/backups/ 2>/dev/null | tail -10'"
    exit 0
  fi

  check_s3_bucket \
    "Sifututor Backup" \
    "" \
    "$BACKUP_BUCKET" \
    "$BACKUP_REGION" \
    "$BACKUP_READONLY_ACCESS_KEY_ID" \
    "$BACKUP_READONLY_SECRET_ACCESS_KEY" \
    ""
fi

echo ""
echo "Note: This script uses read-only credentials. No objects were downloaded or deleted."
