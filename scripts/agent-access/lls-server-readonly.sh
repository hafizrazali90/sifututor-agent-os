#!/usr/bin/env bash
# Lane 41: read-only server access for the Learnest (LLS) box over the existing `lls` ssh alias.
# Commands run as the www-data account the app itself uses, never as root. No password or key is handled here.
#
# Usage:  scripts/agent-access/lls-server-readonly.sh <prod|staging|develop> artisan <name> [flags]
#         scripts/agent-access/lls-server-readonly.sh <env> logs [lines]       (default 200, max 2000)
#         scripts/agent-access/lls-server-readonly.sh <env> pm2                (queue worker names and status)
# Test switch: LLS_SERVER_DRY_RUN=1 prints the remote command instead of running it.

set -euo pipefail

ALIAS_NAME="${LLS_SERVER_SSH_ALIAS:-lls}"
APP_USER="www-data"

refuse() { echo "refused: $1" >&2; exit 3; }
usage() { echo "usage: lls-server-readonly.sh <prod|staging|develop> artisan <name> [flags] | logs [lines] | pm2" >&2; exit 2; }

[[ $# -ge 2 ]] || usage
ENV_NAME="$1"; ACTION="$2"; shift 2

case "$ENV_NAME" in
  prod) APP_DIR=/var/www/learnest ;;
  staging) APP_DIR=/var/www/learnest-staging ;;
  develop) APP_DIR=/var/www/learnest-develop ;;
  *) usage ;;
esac
[[ "$ALIAS_NAME" =~ ^[a-z0-9_-]+$ ]] || refuse "bad ssh alias name"

case "$ACTION" in
  artisan)
    [[ $# -ge 1 ]] || usage
    NAME="$1"; shift
    case "$NAME" in
      about|env|route:list|schedule:list|migrate:status|queue:failed) ;;
      *) refuse "artisan command '$NAME' is not on the read-only list (about, env, route:list, schedule:list, migrate:status, queue:failed)" ;;
    esac
    FLAGS=""
    for a in "$@"; do
      case "$a" in
        --json|--compact|--pending|--no-ansi|--path=*|--name=*|--method=*|--domain=*) ;;
        *) refuse "flag '$a' is not allowed" ;;
      esac
      [[ "$a" =~ ^[A-Za-z0-9_.:=/*-]+$ ]] || refuse "flag has unsafe characters"
      FLAGS="$FLAGS $a"
    done
    REMOTE="cd $APP_DIR && runuser -u $APP_USER -- php artisan $NAME$FLAGS"
    ;;
  logs)
    N="${1:-200}"
    [[ "$N" =~ ^[0-9]+$ ]] || refuse "lines must be a number"
    (( N >= 1 && N <= 2000 )) || refuse "lines must be between 1 and 2000"
    REMOTE="runuser -u $APP_USER -- tail -n $N $APP_DIR/storage/logs/laravel.log"
    ;;
  pm2)
    REMOTE="pm2 jlist 2>/dev/null | python3 -c \"import sys,json; [print(p['name'], p['pm2_env']['status'], 'restarts=' + str(p['pm2_env'].get('restart_time', 0))) for p in json.load(sys.stdin)]\""
    ;;
  *) usage ;;
esac

if [[ "${LLS_SERVER_DRY_RUN:-0}" == "1" ]]; then
  echo "$REMOTE"
  exit 0
fi

exec ssh -o BatchMode=yes "$ALIAS_NAME" "$REMOTE"
