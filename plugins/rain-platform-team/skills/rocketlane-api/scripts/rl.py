#!/usr/bin/env python3
"""Generic Rocketlane API client for the rocketlane-api skill.

Reads the API key from $ROCKETLANE_API_KEY or ~/.config/rain-claude/rocketlane.env
so the key never appears on the command line or in any repo file.

Usage:
  rl.py METHOD PATH [-q key=value ...] [-d '<json>'] [--v1] [--all]
        [--download DIR] [--raw]

Examples:
  rl.py GET /projects -q projectName.cn=Acme
  rl.py GET /projects --all
  rl.py GET /tasks -q projectId.eq=123 -q pageSize=100
  rl.py --v1 GET /tasks/4567                      # v1 returns attachments[]
  rl.py --v1 GET /attachments/99/download --download ./out
  rl.py POST /time-entries -d '{"date":"2026-07-28","minutes":120,"task":{"taskId":4567}}'
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

CONFIG_PATH = os.path.expanduser("~/.config/rain-claude/rocketlane.env")
BASES = {
    "1.0": "https://api.rocketlane.com/api/1.0",
    "v1": "https://api.rocketlane.com/api/v1",
}
SETUP_MSG = (
    "No Rocketlane API key found.\n"
    f"Expected $ROCKETLANE_API_KEY or a line 'ROCKETLANE_API_KEY=...' in {CONFIG_PATH}.\n"
    "Run the rocketlane-api skill's first-time setup (Step 0 in SKILL.md):\n"
    "generate a key in Rocketlane under Settings -> API, then save it with:\n"
    "  mkdir -p ~/.config/rain-claude && chmod 700 ~/.config/rain-claude\n"
    "  printf 'ROCKETLANE_API_KEY=%s\\n' '<your-key>' > ~/.config/rain-claude/rocketlane.env\n"
    "  chmod 600 ~/.config/rain-claude/rocketlane.env"
)


def load_key():
    key = os.environ.get("ROCKETLANE_API_KEY", "").strip()
    if key:
        return key
    try:
        with open(CONFIG_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ROCKETLANE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return None


def http(method, url, key, body=None):
    headers = {"api-key": key, "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    return urllib.request.urlopen(req, timeout=60)


def fail_http(err):
    try:
        detail = err.read().decode(errors="replace")
    except Exception:
        detail = ""
    print(f"HTTP {err.code} {err.reason}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    if err.code == 401:
        print(
            "Key invalid or revoked - re-run the rocketlane-api skill setup "
            f"to replace {CONFIG_PATH}.",
            file=sys.stderr,
        )
    elif err.code == 429:
        print("Rate limited - wait a moment and retry.", file=sys.stderr)
    sys.exit(1)


def filename_from(resp, fallback):
    name = resp.headers.get("x-filename")
    if not name:
        cd = resp.headers.get("content-disposition", "")
        m = re.search(r'filename="?([^";]+)"?', cd)
        name = m.group(1) if m else ""
    return os.path.basename(name) or fallback


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("method", choices=["GET", "POST", "PUT", "DELETE"], type=str.upper)
    p.add_argument("path", help="e.g. /projects or /tasks/123")
    p.add_argument("-q", "--query", action="append", default=[], metavar="K=V")
    p.add_argument("-d", "--data", help="JSON request body")
    p.add_argument("--v1", action="store_true", help="use /api/v1 instead of /api/1.0")
    p.add_argument("--all", action="store_true", help="follow pagination, merge data[]")
    p.add_argument("--download", metavar="DIR", help="save binary response into DIR")
    p.add_argument("--raw", action="store_true", help="print body without pretty-printing")
    args = p.parse_args()

    key = load_key()
    if not key:
        print(SETUP_MSG, file=sys.stderr)
        sys.exit(2)

    base = BASES["v1" if args.v1 else "1.0"]
    params = {}
    for q in args.query:
        if "=" not in q:
            p.error(f"--query expects key=value, got {q!r}")
        k, v = q.split("=", 1)
        params[k] = v
    body = json.loads(args.data) if args.data else None
    path = args.path if args.path.startswith("/") else "/" + args.path

    def url_for(extra=None):
        merged = dict(params, **(extra or {}))
        qs = urllib.parse.urlencode(merged)
        return f"{base}{path}" + (f"?{qs}" if qs else "")

    try:
        if args.download:
            os.makedirs(args.download, exist_ok=True)
            with http(args.method, url_for(), key, body) as resp:
                name = filename_from(resp, path.strip("/").replace("/", "-"))
                dest = os.path.join(args.download, name)
                with open(dest, "wb") as f:
                    f.write(resp.read())
            print(json.dumps({"saved": dest}))
            return

        if args.all:
            merged, total, token = [], None, None
            while True:
                with http(args.method, url_for({"pageToken": token} if token else None), key, body) as resp:
                    page = json.loads(resp.read() or b"{}")
                merged.extend(page.get("data", []))
                pg = page.get("pagination", {})
                total = pg.get("totalRecordCount", total)
                # nextPage URLs may claim http://; we rebuild from BASES so it's always https
                token = pg.get("nextPageToken")
                if not pg.get("hasMore") or not token:
                    break
            print(json.dumps({"data": merged, "totalFetched": len(merged),
                              "totalRecordCount": total}, indent=None if args.raw else 2))
            return

        with http(args.method, url_for(), key, body) as resp:
            raw = resp.read()
            if not raw:
                print(json.dumps({"status": resp.status}))
                return
            if args.raw:
                sys.stdout.write(raw.decode(errors="replace"))
                return
            try:
                print(json.dumps(json.loads(raw), indent=2))
            except ValueError:
                sys.stdout.write(raw.decode(errors="replace"))
    except urllib.error.HTTPError as e:
        fail_http(e)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
