#!/usr/bin/env python3
"""
Rain API Docs Cache Refresh Script

Subcommands:
    auto     (default) Run a freshness check; refresh only if stale.
    check    Read-only: report whether the local cache matches live docs.
    refresh  Force a full re-download and rewrite the cache + metadata.

Usage:
    python3 refresh_cache.py [auto|check|refresh] --cache-dir PATH [--code CODE] [--quiet]

Status line printed to stdout (always exactly one of):
    fresh          cache matches live docs
    refreshed      cache was updated to match live docs
    stale          cache differs from live docs (only emitted by `check`)
    network-error  could not reach docs.rain.xyz; existing cache (if any) is untouched
    auth-error     access code rejected or response was an HTML login page
    no-cache       no local cache exists yet (only emitted by `check`)

Exit codes mirror the status:
    0  fresh | refreshed
    1  stale | no-cache
    2  network-error | auth-error | other
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from urllib.request import Request, build_opener, HTTPCookieProcessor
    from urllib.error import HTTPError, URLError
    from http.cookiejar import CookieJar
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

DEFAULT_ACCESS_CODE = "8QFfkXPJ!XGdsCBk4n"
DOCS_BASE = "https://docs.rain.xyz"
LOGIN_URL = f"{DOCS_BASE}/login/callback/password"
LLMS_TXT_URL = f"{DOCS_BASE}/.well-known/llms.txt"
LLMS_FULL_URL = f"{DOCS_BASE}/.well-known/llms-full.txt"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) rain-api-docs-refresh"

FILES = [
    ("llms_txt", LLMS_TXT_URL, "llms.txt", 60),
    ("llms_full", LLMS_FULL_URL, "llms-full.txt", 180),
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def metadata_path(cache_dir: Path) -> Path:
    return cache_dir / ".metadata.json"


def load_metadata(cache_dir: Path) -> dict:
    path = metadata_path(cache_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_metadata(cache_dir: Path, meta: dict) -> None:
    metadata_path(cache_dir).write_text(json.dumps(meta, indent=2) + "\n")


def cache_files_present(cache_dir: Path) -> bool:
    return all((cache_dir / fname).exists() for _, _, fname, _ in FILES)


class AuthError(RuntimeError):
    pass


class NetworkError(RuntimeError):
    pass


def authenticate(access_code: str):
    """Return (kind, session-like) tuple. Raises AuthError or NetworkError."""
    if HAS_REQUESTS:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        try:
            resp = s.post(
                LOGIN_URL,
                json={"password": access_code},
                allow_redirects=True,
                timeout=30,
            )
        except requests.RequestException as e:
            raise NetworkError(f"auth request failed: {e}") from e
        if resp.status_code != 200:
            raise AuthError(f"auth returned HTTP {resp.status_code}")
        return ("requests", s)

    if HAS_URLLIB:
        cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cj))
        data = json.dumps({"password": access_code}).encode("utf-8")
        req = Request(
            LOGIN_URL,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            resp = opener.open(req, timeout=30)
        except HTTPError as e:
            raise AuthError(f"auth returned HTTP {e.code}") from e
        except URLError as e:
            raise NetworkError(f"auth request failed: {e}") from e
        if resp.status != 200:
            raise AuthError(f"auth returned HTTP {resp.status}")
        return ("urllib", opener)

    raise RuntimeError("No HTTP library available (need requests or urllib)")


def conditional_get(session, url: str, etag: str | None, last_modified: str | None, timeout: int):
    """
    Conditional GET. Returns (status, body_or_None, headers).
    - status 304: body is None, headers contain ETag/Last-Modified if echoed.
    - status 200: body is the text content.
    Raises NetworkError on transport failure.
    """
    kind, sess = session
    extra = {"User-Agent": USER_AGENT}
    if etag:
        extra["If-None-Match"] = etag
    if last_modified:
        extra["If-Modified-Since"] = last_modified

    if kind == "requests":
        try:
            resp = sess.get(url, headers=extra, timeout=timeout)
        except requests.RequestException as e:
            raise NetworkError(f"GET {url} failed: {e}") from e
        if resp.status_code == 304:
            return 304, None, dict(resp.headers)
        if resp.status_code != 200:
            raise NetworkError(f"GET {url} returned HTTP {resp.status_code}")
        return 200, resp.text, dict(resp.headers)

    # urllib
    req = Request(url, headers=extra)
    try:
        resp = sess.open(req, timeout=timeout)
    except HTTPError as e:
        if e.code == 304:
            return 304, None, dict(e.headers)
        raise NetworkError(f"GET {url} returned HTTP {e.code}") from e
    except URLError as e:
        raise NetworkError(f"GET {url} failed: {e}") from e
    return resp.status, resp.read().decode("utf-8"), dict(resp.headers)


def header(headers: dict, name: str) -> str | None:
    """Case-insensitive header lookup; returns the first matching value."""
    target = name.lower()
    for k, v in headers.items():
        if k.lower() == target:
            return v
    return None


def looks_like_login_page(text: str) -> bool:
    head = text[:500].lower()
    return "<html" in head or len(text) < 100


def fetch_one(session, key: str, url: str, fname: str, timeout: int, meta_entry: dict):
    """
    Conditional fetch + decision. Returns:
        ("fresh", new_meta)        -> server confirmed unchanged (304) or content hash matches
        ("changed", text, new_meta) -> content differs from cache; caller should write text
    Raises AuthError if response looks like a login page; NetworkError on transport failure.
    """
    etag = meta_entry.get("etag")
    last_mod = meta_entry.get("last_modified")
    status, text, headers = conditional_get(session, url, etag, last_mod, timeout)

    if status == 304:
        # Refresh header capture in case the server rotates ETags
        return ("fresh", {
            **meta_entry,
            "etag": header(headers, "ETag") or etag,
            "last_modified": header(headers, "Last-Modified") or last_mod,
        })

    if looks_like_login_page(text):
        raise AuthError(f"{fname} looked like HTML/login page; access code may be wrong")

    new_hash = sha256_text(text)
    new_meta = {
        "sha256": new_hash,
        "size": len(text),
        "etag": header(headers, "ETag"),
        "last_modified": header(headers, "Last-Modified"),
    }
    if new_hash == meta_entry.get("sha256"):
        return ("fresh", new_meta)
    return ("changed", text, new_meta)


def cmd_auto(cache_dir: Path, access_code: str, quiet: bool, read_only: bool = False) -> int:
    """
    Verify cache freshness and refresh if needed.
    If read_only=True, never writes (used by `check`).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    meta = load_metadata(cache_dir)
    has_files = cache_files_present(cache_dir)

    try:
        session = authenticate(access_code)
    except AuthError as e:
        if not quiet:
            print(f"  Auth error: {e}", file=sys.stderr)
        print("auth-error")
        return 2
    except NetworkError as e:
        if not quiet:
            print(f"  Network error during auth: {e}", file=sys.stderr)
        print("network-error")
        return 2

    if read_only and not has_files:
        print("no-cache")
        return 1

    any_change = False
    new_meta = {"fetched_at": now_iso(), "source_base": DOCS_BASE}

    for key, url, fname, timeout in FILES:
        entry = meta.get(key, {}) if has_files else {}
        try:
            result = fetch_one(session, key, url, fname, timeout, entry)
        except AuthError as e:
            if not quiet:
                print(f"  {e}", file=sys.stderr)
            print("auth-error")
            return 2
        except NetworkError as e:
            if not quiet:
                print(f"  Network error fetching {fname}: {e}", file=sys.stderr)
            print("network-error")
            return 2

        if result[0] == "fresh":
            new_meta[key] = result[1]
        else:
            any_change = True
            _, text, entry_meta = result
            new_meta[key] = entry_meta
            if not read_only:
                (cache_dir / fname).write_text(text, encoding="utf-8")
                if not quiet:
                    print(f"  Wrote {fname} ({len(text):,} chars)")

    if read_only:
        if any_change or not has_files:
            print("stale")
            return 1
        print("fresh")
        return 0

    save_metadata(cache_dir, new_meta)
    print("refreshed" if any_change else "fresh")
    return 0


def cmd_refresh(cache_dir: Path, access_code: str, quiet: bool) -> int:
    """Force a full download regardless of cache state."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    if not quiet:
        print(f"Refreshing Rain API docs cache at {cache_dir}...")

    try:
        session = authenticate(access_code)
    except AuthError as e:
        if not quiet:
            print(f"  Auth error: {e}", file=sys.stderr)
        print("auth-error")
        return 2
    except NetworkError as e:
        if not quiet:
            print(f"  Network error: {e}", file=sys.stderr)
        print("network-error")
        return 2

    new_meta = {"fetched_at": now_iso(), "source_base": DOCS_BASE}
    for key, url, fname, timeout in FILES:
        try:
            status, text, headers = conditional_get(session, url, None, None, timeout)
        except NetworkError as e:
            if not quiet:
                print(f"  Network error fetching {fname}: {e}", file=sys.stderr)
            print("network-error")
            return 2

        if looks_like_login_page(text or ""):
            if not quiet:
                print(f"  {fname} looked like HTML/login page", file=sys.stderr)
            print("auth-error")
            return 2

        (cache_dir / fname).write_text(text, encoding="utf-8")
        new_meta[key] = {
            "sha256": sha256_text(text),
            "size": len(text),
            "etag": header(headers, "ETag"),
            "last_modified": header(headers, "Last-Modified"),
        }
        if not quiet:
            print(f"  Wrote {fname} ({len(text):,} chars)")

    save_metadata(cache_dir, new_meta)
    print("refreshed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Refresh Rain API docs cache")
    parser.add_argument(
        "subcommand",
        nargs="?",
        default="auto",
        choices=["auto", "check", "refresh"],
        help="auto (default): refresh if stale; check: read-only freshness probe; refresh: force re-download",
    )
    parser.add_argument(
        "--cache-dir",
        required=True,
        help="Cache directory (e.g. <project-root>/rain-api-docs)",
    )
    parser.add_argument(
        "--code",
        default=DEFAULT_ACCESS_CODE,
        help="Mintlify access code",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output (status line still printed)",
    )
    args = parser.parse_args()

    if not (HAS_REQUESTS or HAS_URLLIB):
        print("  No HTTP library available (need requests or urllib).", file=sys.stderr)
        print("network-error")
        sys.exit(2)

    cache_dir = Path(args.cache_dir).expanduser().resolve()

    if args.subcommand == "check":
        sys.exit(cmd_auto(cache_dir, args.code, args.quiet, read_only=True))
    if args.subcommand == "refresh":
        sys.exit(cmd_refresh(cache_dir, args.code, args.quiet))
    sys.exit(cmd_auto(cache_dir, args.code, args.quiet))


if __name__ == "__main__":
    main()
