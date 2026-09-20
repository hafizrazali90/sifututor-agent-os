#!/usr/bin/env python3
"""Model-agnostic, read-only SharePoint access through Microsoft Graph."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

GRAPH = "https://graph.microsoft.com/v1.0"
DEFAULT_CONFIG = Path.home() / ".config/sifututor/sharepoint-readonly.json"
DEFAULT_CACHE = Path.home() / ".config/sifututor/runtime/sharepoint-token.json"
SAFE_FIELDS = "id,name,size,lastModifiedDateTime,webUrl,file,folder,parentReference"


class LaneError(RuntimeError):
    pass


def read_private_json(path: Path, *, required: bool = True) -> dict:
    if not path.exists():
        if required:
            raise LaneError(f"configuration missing: {path}")
        return {}
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise LaneError(f"private file permissions too broad: {path} (expected 600)")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise LaneError(f"invalid private JSON file: {path}") from exc
    if not isinstance(value, dict):
        raise LaneError(f"private JSON root must be an object: {path}")
    return value


def write_private_json(path: Path, value: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    temp = path.with_suffix(path.suffix + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(value, handle)
    os.replace(temp, path)
    os.chmod(path, 0o600)


def validate_config(config: dict) -> dict:
    required = ("tenant_id", "client_id", "drive_id", "allowed_path_prefixes", "download_root")
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise LaneError("configuration missing required keys: " + ", ".join(missing))
    prefixes = config["allowed_path_prefixes"]
    if not isinstance(prefixes, list) or not prefixes:
        raise LaneError("allowed_path_prefixes must be a non-empty list")
    config["allowed_path_prefixes"] = [normalize_relative_path(value) for value in prefixes]
    hosts = config.get("allowed_download_hosts", ["*.sharepoint.com", "*.sharepoint-df.com"])
    if not isinstance(hosts, list) or not hosts:
        raise LaneError("allowed_download_hosts must be a non-empty list")
    config["allowed_download_hosts"] = [str(value).lower() for value in hosts]
    return config


def normalize_relative_path(value: object) -> str:
    text = str(value or "").replace("\\", "/").strip("/")
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise LaneError("path must be a clean drive-relative path")
    return str(path)


def path_allowed(path: str, prefixes: list[str]) -> bool:
    normalized = normalize_relative_path(path)
    return any(normalized == prefix or normalized.startswith(prefix + "/") for prefix in prefixes)


def host_allowed(host: str, patterns: list[str]) -> bool:
    host = host.lower().rstrip(".")
    for pattern in patterns:
        pattern = pattern.lower().rstrip(".")
        if pattern.startswith("*.") and host.endswith(pattern[1:]) and host != pattern[2:]:
            return True
        if host == pattern:
            return True
    return False


def graph_path(config: dict, path: str, *, children: bool = False) -> str:
    normalized = normalize_relative_path(path)
    if not path_allowed(normalized, config["allowed_path_prefixes"]):
        raise LaneError("requested path is outside the configured read-only allow-list")
    quoted = urllib.parse.quote(normalized, safe="/")
    suffix = "/children" if children else ""
    return f"{GRAPH}/drives/{urllib.parse.quote(str(config['drive_id']), safe='')}/root:/{quoted}:{suffix}"


def safe_error(exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"Microsoft Graph returned HTTP {exc.code}"
    if isinstance(exc, urllib.error.URLError):
        return "Microsoft Graph connection failed"
    return str(exc)


def request_json(url: str, *, token: str | None = None, data: dict | None = None, timeout: int = 20) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "graph.microsoft.com":
        raise LaneError("refused non-Graph API URL")
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode() or "{}")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise LaneError(safe_error(exc)) from exc


def valid_access_token(cache: dict) -> str | None:
    token = cache.get("access_token")
    expires_at = int(cache.get("expires_at") or 0)
    return str(token) if token and expires_at > int(time.time()) + 60 else None


def acquire_token(config: dict, cache_path: Path, *, interactive: bool = False) -> str:
    cache = read_private_json(cache_path, required=False)
    token = valid_access_token(cache)
    if token:
        return token
    tenant = urllib.parse.quote(str(config["tenant_id"]), safe="")
    client_id = str(config["client_id"])
    scopes = config.get("scopes", ["Files.Read", "offline_access"])
    endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"
    if cache.get("refresh_token"):
        result = post_identity(endpoint + "/token", {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": str(cache["refresh_token"]),
            "scope": " ".join(scopes),
        })
        if result.get("access_token"):
            write_private_json(cache_path, {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token") or cache["refresh_token"],
                "expires_at": int(time.time()) + int(result.get("expires_in") or 3600),
            })
            return str(result["access_token"])
    if not interactive:
        raise LaneError("not authenticated; run the login command interactively")
    device = post_identity(endpoint + "/devicecode", {"client_id": client_id, "scope": " ".join(scopes)})
    print(device.get("message") or "Complete Microsoft device sign-in in your browser.", file=sys.stderr)
    deadline = time.time() + int(device.get("expires_in") or 900)
    interval = max(2, int(device.get("interval") or 5))
    while time.time() < deadline:
        time.sleep(interval)
        result = post_identity(endpoint + "/token", {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id,
            "device_code": str(device.get("device_code") or ""),
        }, allow_oauth_wait=True)
        if result.get("error") in {"authorization_pending", "slow_down"}:
            interval += 5 if result.get("error") == "slow_down" else 0
            continue
        if not result.get("access_token"):
            raise LaneError("Microsoft sign-in failed: " + str(result.get("error") or "unknown_error"))
        saved = {
            "access_token": result["access_token"],
            "refresh_token": result.get("refresh_token"),
            "expires_at": int(time.time()) + int(result.get("expires_in") or 3600),
        }
        write_private_json(cache_path, saved)
        return str(result["access_token"])
    raise LaneError("Microsoft sign-in expired before completion")


def post_identity(url: str, data: dict, *, allow_oauth_wait: bool = False) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "login.microsoftonline.com":
        raise LaneError("refused non-Microsoft identity URL")
    request = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode() or "{}")
        except json.JSONDecodeError:
            body = {}
        if allow_oauth_wait and body.get("error") in {"authorization_pending", "slow_down"}:
            return body
        raise LaneError(f"Microsoft identity returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LaneError("Microsoft identity connection failed") from exc


def graph_get_all(url: str, token: str, *, max_pages: int = 20) -> list[dict]:
    values: list[dict] = []
    for _ in range(max_pages):
        data = request_json(url, token=token)
        values.extend(value for value in data.get("value", []) if isinstance(value, dict))
        next_url = data.get("@odata.nextLink")
        if not next_url:
            return values
        parsed = urllib.parse.urlparse(str(next_url))
        if parsed.scheme != "https" or parsed.hostname != "graph.microsoft.com" or not parsed.path.startswith("/v1.0/"):
            raise LaneError("refused unsafe Microsoft Graph pagination URL")
        url = str(next_url)
    raise LaneError("pagination exceeded the configured safety limit")


def public_item(item: dict) -> dict:
    return {key: item[key] for key in ("id", "name", "size", "lastModifiedDateTime", "webUrl", "file", "folder") if key in item}


def safe_destination(config: dict, relative: str) -> Path:
    root = Path(config["download_root"]).expanduser().resolve()
    destination = (root / normalize_relative_path(relative)).resolve()
    if destination == root or root not in destination.parents:
        raise LaneError("download destination escapes the configured root")
    return destination


def download(item: dict, config: dict, destination: Path) -> None:
    url = item.get("@microsoft.graph.downloadUrl")
    parsed = urllib.parse.urlparse(str(url or ""))
    if parsed.scheme != "https" or not parsed.hostname or not host_allowed(parsed.hostname, config["allowed_download_hosts"]):
        raise LaneError("download URL host is outside the configured allow-list")
    if destination.exists():
        raise LaneError("download destination already exists; refusing to overwrite")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".part")
    allowed_hosts = config["allowed_download_hosts"]

    class SafeRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, msg, headers, newurl):
            target = urllib.parse.urlparse(newurl)
            if target.scheme != "https" or not target.hostname or not host_allowed(target.hostname, allowed_hosts):
                raise LaneError("download redirect host is outside the configured allow-list")
            return super().redirect_request(request, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(SafeRedirect())
    try:
        with opener.open(str(url), timeout=30) as response, temp.open("wb") as handle:
            limit = int(config.get("max_download_bytes", 25 * 1024 * 1024))
            total = 0
            while True:
                chunk = response.read(min(1024 * 1024, limit - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise LaneError("download exceeds configured size limit")
                handle.write(chunk)
        os.replace(temp, destination)
    finally:
        if temp.exists():
            temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe")
    sub.add_parser("login")
    for name in ("list", "metadata"):
        command = sub.add_parser(name)
        command.add_argument("path")
    command = sub.add_parser("download")
    command.add_argument("path")
    command.add_argument("--to", required=True)
    args = parser.parse_args()
    try:
        config = validate_config(read_private_json(args.config))
        if args.command == "probe":
            cache = read_private_json(args.cache, required=False)
            state = "available" if valid_access_token(cache) else "not_authenticated"
            print(json.dumps({"name": "sharepoint_readonly", "state": state, "config": "valid", "write_operations": "not_implemented"}))
            return 0 if state == "available" else 2
        token = acquire_token(config, args.cache, interactive=args.command == "login")
        if args.command == "login":
            print(json.dumps({"name": "sharepoint_readonly", "state": "available", "token": "stored_privately"}))
            return 0
        path = normalize_relative_path(args.path)
        url = graph_path(config, path, children=args.command == "list")
        if args.command == "list":
            separator = "&" if "?" in url else "?"
            items = graph_get_all(url + separator + urllib.parse.urlencode({"$select": SAFE_FIELDS}), token)
            print(json.dumps({"path": path, "items": [public_item(item) for item in items]}, indent=2))
            return 0
        separator = "&" if "?" in url else "?"
        item_url = url + separator + urllib.parse.urlencode({"$select": SAFE_FIELDS})
        item = request_json(url if args.command == "download" else item_url, token=token)
        if args.command == "metadata":
            print(json.dumps(public_item(item), indent=2))
            return 0
        destination = safe_destination(config, args.to)
        download(item, config, destination)
        print(json.dumps({"downloaded": str(destination), "bytes": destination.stat().st_size}))
        return 0
    except LaneError as exc:
        print(json.dumps({"state": "error", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
