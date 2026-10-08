# Shared MySQL client choice for the read-only database lanes (#340).
#
# Homebrew's MySQL 9.x client no longer ships the mysql_native_password
# plugin, and the SIMS read-only account signs in with it. Prefer an installed
# 8.x client; fall back to whatever `mysql` is on PATH. Source this file, then
# call sifu_mysql_client. Nothing here reads or prints credentials.

SIFU_MYSQL_DEFAULT_CANDIDATES="/opt/homebrew/opt/mysql@8.4/bin/mysql:/opt/homebrew/opt/mysql-client@8.4/bin/mysql:/opt/homebrew/opt/mysql@8.0/bin/mysql:/opt/homebrew/opt/mysql-client@8.0/bin/mysql:/usr/local/opt/mysql@8.4/bin/mysql:/usr/local/opt/mysql-client@8.4/bin/mysql:/usr/local/opt/mysql@8.0/bin/mysql"

# Prints the client path. SIFU_MYSQL_CLIENT forces one; SIFU_MYSQL_CANDIDATES
# (colon-separated) replaces the default preference list.
sifu_mysql_client() {
  if [[ -n "${SIFU_MYSQL_CLIENT:-}" && -x "${SIFU_MYSQL_CLIENT}" ]]; then
    printf '%s\n' "$SIFU_MYSQL_CLIENT"
    return 0
  fi
  local candidate
  local IFS=":"
  for candidate in ${SIFU_MYSQL_CANDIDATES:-$SIFU_MYSQL_DEFAULT_CANDIDATES}; do
    if [[ -n "$candidate" && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  command -v mysql
}

# Explains a failed connection from the client's own error text, which never
# contains the password.
sifu_mysql_failure_hint() {
  local err="$1"
  if grep -q "mysql_native_password" <<<"$err"; then
    echo "  This MySQL client cannot load mysql_native_password (MySQL 9.x removed it). Install an 8.4 client: brew install mysql@8.4"
  elif grep -qi "Access denied" <<<"$err"; then
    echo "  The server refused the read-only login. Check the conf values without printing them."
  elif grep -qiE "Can't connect|timed out|Lost connection|Unknown MySQL server host" <<<"$err"; then
    echo "  The network path was refused or timed out. If running locally, production 3306 may be firewalled by design. Use the approved SSH tunnel path before retrying."
  else
    echo "  Unrecognised client error (shown above)."
  fi
}
