#!/usr/bin/env python3
"""
Rain API Docs Cache Refresh Script

Fetches the latest llms.txt and llms-full.txt from docs.rain.xyz
and updates the local cache in the skill's cache/ directory.

Usage:
    python3 refresh_cache.py [--code ACCESS_CODE]

The Rain docs are hosted on Mintlify behind a simple access-code gate.
This script authenticates with the access code and downloads fresh copies.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
    from urllib.parse import urlencode
    from http.cookiejar import CookieJar
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# Default access code for Rain's Mintlify docs
DEFAULT_ACCESS_CODE = "8QFfkXPJ!XGdsCBk4n"

DOCS_BASE = "https://docs.rain.xyz"
LOGIN_URL = f"{DOCS_BASE}/login/callback/password"
LLMS_TXT_URL = f"{DOCS_BASE}/.well-known/llms.txt"
LLMS_FULL_URL = f"{DOCS_BASE}/.well-known/llms-full.txt"

# Cache directory is sibling to scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPT_DIR.parent / "cache"

# CloudFront rejects default python-urllib user agents with 403.
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) rain-api-docs-refresh"


def fetch_with_requests(access_code: str) -> tuple[str, str]:
    """Fetch docs using the requests library."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # Authenticate - Mintlify password callback expects JSON {"password": ...}
    print("  Authenticating with Mintlify...")
    auth_resp = session.post(
        LOGIN_URL,
        json={"password": access_code},
        allow_redirects=True,
        timeout=30,
    )
    if auth_resp.status_code != 200:
        raise RuntimeError(f"Auth failed with status {auth_resp.status_code}")

    # Fetch llms.txt
    print("  Fetching llms.txt...")
    resp1 = session.get(LLMS_TXT_URL, timeout=60)
    resp1.raise_for_status()
    llms_txt = resp1.text

    # Fetch llms-full.txt
    print("  Fetching llms-full.txt (this may take a moment)...")
    resp2 = session.get(LLMS_FULL_URL, timeout=120)
    resp2.raise_for_status()
    llms_full = resp2.text

    return llms_txt, llms_full


def fetch_with_urllib(access_code: str) -> tuple[str, str]:
    """Fetch docs using urllib (no external dependencies)."""
    import json as _json

    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    # Authenticate - Mintlify password callback expects JSON {"password": ...}
    print("  Authenticating with Mintlify...")
    data = _json.dumps({"password": access_code}).encode("utf-8")
    req = Request(
        LOGIN_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    resp = opener.open(req, timeout=30)
    if resp.status != 200:
        raise RuntimeError(f"Auth failed with status {resp.status}")

    # Fetch llms.txt
    print("  Fetching llms.txt...")
    resp1 = opener.open(
        Request(LLMS_TXT_URL, headers={"User-Agent": USER_AGENT}), timeout=60
    )
    llms_txt = resp1.read().decode("utf-8")

    # Fetch llms-full.txt
    print("  Fetching llms-full.txt (this may take a moment)...")
    resp2 = opener.open(
        Request(LLMS_FULL_URL, headers={"User-Agent": USER_AGENT}), timeout=120
    )
    llms_full = resp2.read().decode("utf-8")

    return llms_txt, llms_full


def main():
    parser = argparse.ArgumentParser(description="Refresh Rain API docs cache")
    parser.add_argument(
        "--code",
        default=DEFAULT_ACCESS_CODE,
        help="Mintlify access code (default: stored code)",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(CACHE_DIR),
        help=f"Cache directory (default: {CACHE_DIR})",
    )
    args = parser.parse_args()

    cache_path = Path(args.cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    print(f"Refreshing Rain API docs cache...")
    print(f"  Cache dir: {cache_path}")

    try:
        if HAS_REQUESTS:
            llms_txt, llms_full = fetch_with_requests(args.code)
        elif HAS_URLLIB:
            llms_txt, llms_full = fetch_with_urllib(args.code)
        else:
            print("\nError: No HTTP library available (need requests or urllib).")
            print("Try: pip install requests")
            sys.exit(1)

        # Validate we got real content (not a login page)
        if "<html" in llms_txt[:500].lower() or len(llms_txt) < 100:
            print("\nWarning: llms.txt looks like an HTML page, not Markdown.")
            print("The access code may be incorrect or the auth flow may have changed.")
            print("You can paste the content manually instead.")
            sys.exit(1)

        # Write cache files
        llms_txt_path = cache_path / "llms.txt"
        llms_full_path = cache_path / "llms-full.txt"

        llms_txt_path.write_text(llms_txt, encoding="utf-8")
        print(f"  Wrote {llms_txt_path.name} ({len(llms_txt):,} chars)")

        llms_full_path.write_text(llms_full, encoding="utf-8")
        print(f"  Wrote {llms_full_path.name} ({len(llms_full):,} chars)")

        print("\nCache refreshed successfully!")

    except Exception as e:
        print(f"\nError fetching docs: {e}")
        print("\nIf this is a sandbox/network restriction, you can refresh manually:")
        print("  1. Open https://docs.rain.xyz/.well-known/llms.txt in your browser")
        print("  2. Enter the access code when prompted")
        print("  3. Copy the content and paste it when prompted by Claude")
        sys.exit(1)


if __name__ == "__main__":
    main()
