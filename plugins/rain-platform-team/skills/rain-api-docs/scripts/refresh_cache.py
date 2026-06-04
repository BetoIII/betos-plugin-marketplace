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
import re
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
LLMS_TXT_URLS = [
    f"{DOCS_BASE}/.well-known/llms.txt",
    f"{DOCS_BASE}/llms.txt",
]
LLMS_FULL_URLS = [
    f"{DOCS_BASE}/.well-known/llms-full.txt",
    f"{DOCS_BASE}/llms-full.txt",
]
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) rain-api-docs-refresh"

FILES = [
    # (key, urls, filename, timeout_seconds, required)
    ("llms_txt", LLMS_TXT_URLS, "llms.txt", 60, False),
    # llms_full is "required=False" because we have a per-page reconstruction
    # fallback (rebuild_llms_full_from_pages) when the upstream file is 404.
    ("llms_full", LLMS_FULL_URLS, "llms-full.txt", 180, False),
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
    return all(
        (cache_dir / fname).exists()
        for _, _, fname, _, required in FILES
        if required
    )


class AuthError(RuntimeError):
    pass


class NetworkError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
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
    Raises NotFoundError on HTTP 404, NetworkError on other transport/HTTP failures.
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
        if resp.status_code == 404:
            raise NotFoundError(f"GET {url} returned HTTP 404")
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
        if e.code == 404:
            raise NotFoundError(f"GET {url} returned HTTP 404") from e
        raise NetworkError(f"GET {url} returned HTTP {e.code}") from e
    except URLError as e:
        raise NetworkError(f"GET {url} failed: {e}") from e
    except (TimeoutError, OSError) as e:
        # Python 3.9 raises socket.timeout (an OSError) directly here, not
        # wrapped in URLError; catch broadly so a stalled connection becomes
        # a NetworkError the caller can recover from instead of a hard crash.
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


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https://docs\.rain\.xyz/[^)\s]+\.md)\)")


def parse_md_urls(llms_txt: str) -> list[tuple[str, str]]:
    """Return ordered, de-duplicated (title, .md-url) pairs from llms.txt."""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for m in MD_LINK_RE.finditer(llms_txt):
        title, url = m.group(1).strip(), m.group(2).strip()
        if url in seen:
            continue
        seen.add(url)
        out.append((title, url))
    return out


def reconstruct_page(title: str, md_url: str, body: str) -> str:
    """Format one page to match the canonical `# Title\\nSource: URL\\n\\n\\n<body>` layout."""
    source_url = md_url[:-3] if md_url.endswith(".md") else md_url
    stripped = body.lstrip()
    if stripped.startswith("# "):
        first_line, _, rest = stripped.partition("\n")
        return f"{first_line}\nSource: {source_url}\n\n\n{rest.lstrip()}\n"
    return f"# {title}\nSource: {source_url}\n\n\n{stripped}\n"


def _fetch_one_md_page(session, pair, timeout, retries: int = 1):
    """
    Worker for the per-page fallback. Returns (title, md_url, body) where
    `body` is the markdown text on success or None on any failure (404, login
    page response, or repeated network errors).

    Retries once on transient NetworkError to absorb stray socket timeouts
    under concurrent load. 404s aren't retried — the page genuinely doesn't
    exist at that URL.

    Thread-safe for both session kinds:
      - `requests.Session.get` is documented thread-safe after auth.
      - The stdlib `http.cookiejar.CookieJar` uses an internal RLock around
        `add_cookie_header`/`extract_cookies`, and urllib creates a fresh
        HTTPSConnection per request, so no shared mutable connection state.
    """
    title, md_url = pair
    last_err: NetworkError | None = None
    for attempt in range(retries + 1):
        try:
            status, body, _ = conditional_get(session, md_url, None, None, timeout)
        except NotFoundError:
            return title, md_url, None
        except NetworkError as e:
            last_err = e
            continue
        if status != 200 or not body or looks_like_login_page(body):
            return title, md_url, None
        return title, md_url, body
    return title, md_url, None


def rebuild_llms_full_from_pages(
    session,
    llms_txt: str,
    timeout: int,
    quiet: bool,
    max_fail_ratio: float = 0.5,
    max_workers: int = 8,
):
    """
    Walk every .md URL in llms.txt and concatenate into llms-full.txt format.

    Uses a thread pool for both session kinds:
      - `requests.Session.get` is documented thread-safe after auth.
      - The stdlib urllib opener with `HTTPCookieProcessor` is also safe to
        share because the underlying CookieJar locks its mutators and urllib
        creates a fresh HTTPSConnection per request.

    Returns (text, fetched, total, failed_urls). Raises NotFoundError if the
    proportion of per-page 404s exceeds `max_fail_ratio` — in that case the
    caller should fall back to keeping the cached llms-full.txt.
    """
    pairs = parse_md_urls(llms_txt)
    total = len(pairs)
    if total == 0:
        raise NotFoundError("no per-page .md URLs in llms.txt; cannot reconstruct")

    workers = max(1, min(max_workers, total))

    if not quiet:
        mode = f"{workers} parallel workers" if workers > 1 else "sequential"
        print(
            f"  llms-full.txt: upstream 404; reconstructing from {total} "
            f"per-page .md files ({mode})",
            file=sys.stderr,
        )

    chunks: list[str] = []
    failed: list[str] = []

    def consume(result, completed_count):
        title, md_url, body = result
        if body is None:
            failed.append(md_url)
        else:
            chunks.append(reconstruct_page(title, md_url, body))
        if not quiet and completed_count % 50 == 0:
            print(
                f"  per-page fallback: {completed_count}/{total} fetched ({len(failed)} failed)",
                file=sys.stderr,
            )

    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor
        # executor.map preserves input order, so chunks stay in llms.txt order.
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for i, result in enumerate(
                ex.map(lambda p: _fetch_one_md_page(session, p, timeout), pairs),
                1,
            ):
                consume(result, i)
    else:
        for i, pair in enumerate(pairs, 1):
            consume(_fetch_one_md_page(session, pair, timeout), i)

    if total and (len(failed) / total) > max_fail_ratio:
        raise NotFoundError(
            f"per-page fallback aborted: {len(failed)}/{total} pages failed"
        )

    text = "\n\n".join(chunks) + "\n" if chunks else ""
    return text, len(chunks), total, failed


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


def fetch_with_fallback(
    session,
    key: str,
    urls: list,
    fname: str,
    timeout: int,
    meta_entry: dict,
    quiet: bool = True,
):
    """
    Walk candidate URLs in order. Return (result, url_used) for the first URL
    that succeeds, where `result` is whatever fetch_one returns.

    Raises NotFoundError only after every candidate returns 404. AuthError and
    NetworkError propagate immediately on the first occurrence.
    """
    last_not_found: NotFoundError | None = None
    for url in urls:
        try:
            result = fetch_one(session, key, url, fname, timeout, meta_entry)
        except NotFoundError as e:
            last_not_found = e
            if not quiet:
                print(f"  {fname}: {url} returned 404; trying next candidate", file=sys.stderr)
            continue
        return result, url
    assert last_not_found is not None
    raise last_not_found


def try_rebuild_llms_full(
    session,
    cache_dir: Path,
    fname: str,
    llms_txt_text: str | None,
    quiet: bool,
):
    """
    Per-page fallback for when upstream `llms-full.txt` is 404.

    Walks every `.md` URL in `llms_txt_text`, fetches each, and writes a
    reconstructed `llms-full.txt` to `cache_dir/fname`.

    Returns the metadata entry on success, or None when reconstruction wasn't
    possible (no llms_txt content, too many per-page 404s, or transport error).
    """
    if llms_txt_text is None:
        if not quiet:
            print(
                "  per-page rebuild skipped: no llms.txt content available",
                file=sys.stderr,
            )
        return None
    try:
        text, fetched, total, failed = rebuild_llms_full_from_pages(
            session, llms_txt_text, timeout=60, quiet=quiet
        )
    except NotFoundError as e:
        if not quiet:
            print(
                f"  per-page rebuild failed ({e}); keeping cached {fname}",
                file=sys.stderr,
            )
        return None
    except NetworkError as e:
        if not quiet:
            print(
                f"  per-page rebuild aborted on network error: {e}",
                file=sys.stderr,
            )
        return None

    (cache_dir / fname).write_text(text, encoding="utf-8")
    if not quiet:
        skipped_note = f"; {len(failed)} skipped" if failed else ""
        print(
            f"  Wrote {fname} ({len(text):,} chars) reconstructed from "
            f"{fetched}/{total} per-page .md files{skipped_note}"
        )
    return {
        "sha256": sha256_text(text),
        "size": len(text),
        "etag": None,
        "last_modified": None,
        "url_used": "per-page-fallback",
        "rebuilt_pages": fetched,
        "total_pages": total,
        "skipped_pages": len(failed),
    }


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
    degraded: list[str] = []
    llms_txt_text: str | None = None

    for key, urls, fname, timeout, required in FILES:
        entry = meta.get(key, {}) if has_files else {}
        try:
            result, url_used = fetch_with_fallback(
                session, key, urls, fname, timeout, entry, quiet=quiet
            )
        except AuthError as e:
            if not quiet:
                print(f"  {e}", file=sys.stderr)
            print("auth-error")
            return 2
        except NotFoundError as e:
            # Per-page rebuild only applies to llms-full.txt and only when we
            # are allowed to write. In read-only (`check`) we just mark it
            # degraded so the freshness verdict isn't blocked by a 404 we
            # can't repair without writing.
            if key == "llms_full" and not read_only:
                rebuilt = try_rebuild_llms_full(
                    session, cache_dir, fname, llms_txt_text, quiet
                )
                if rebuilt is not None:
                    new_meta[key] = rebuilt
                    any_change = True
                    continue

            if required:
                if not quiet:
                    print(f"  Required file {fname} not found at any candidate URL: {e}", file=sys.stderr)
                print("network-error")
                return 2
            if not quiet:
                print(
                    f"  {fname} not served upstream (404) at any candidate; keeping cached copy",
                    file=sys.stderr,
                )
            if entry:
                new_meta[key] = entry
            degraded.append(key)
            continue
        except NetworkError as e:
            if not quiet:
                print(f"  Network error fetching {fname}: {e}", file=sys.stderr)
            print("network-error")
            return 2

        if result[0] == "fresh":
            new_meta[key] = {**result[1], "url_used": url_used}
        else:
            any_change = True
            _, text, entry_meta = result
            new_meta[key] = {**entry_meta, "url_used": url_used}
            if not read_only:
                (cache_dir / fname).write_text(text, encoding="utf-8")
                if not quiet:
                    print(f"  Wrote {fname} ({len(text):,} chars) from {url_used}")

        # Cache the resolved llms.txt content so the per-page fallback can
        # use it if llms-full.txt 404s in the next iteration.
        if key == "llms_txt":
            p = cache_dir / fname
            if p.exists():
                try:
                    llms_txt_text = p.read_text(encoding="utf-8")
                except OSError:
                    llms_txt_text = None

    if read_only:
        if any_change or not has_files:
            print("stale")
            return 1
        print("fresh")
        return 0

    if degraded:
        new_meta["degraded_endpoints"] = degraded
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

    prior_meta = load_metadata(cache_dir)
    new_meta = {"fetched_at": now_iso(), "source_base": DOCS_BASE}
    degraded: list[str] = []
    llms_txt_text: str | None = None
    for key, urls, fname, timeout, required in FILES:
        try:
            result, url_used = fetch_with_fallback(
                session, key, urls, fname, timeout, {}, quiet=quiet
            )
        except AuthError as e:
            if not quiet:
                print(f"  {e}", file=sys.stderr)
            print("auth-error")
            return 2
        except NotFoundError as e:
            if key == "llms_full":
                rebuilt = try_rebuild_llms_full(
                    session, cache_dir, fname, llms_txt_text, quiet
                )
                if rebuilt is not None:
                    new_meta[key] = rebuilt
                    continue

            if required:
                if not quiet:
                    print(f"  Required file {fname} not found at any candidate URL: {e}", file=sys.stderr)
                print("network-error")
                return 2
            if not quiet:
                print(
                    f"  {fname} not served upstream (404) at any candidate; keeping cached copy",
                    file=sys.stderr,
                )
            prior_entry = prior_meta.get(key)
            if prior_entry:
                new_meta[key] = prior_entry
            degraded.append(key)
            if key == "llms_txt":
                p = cache_dir / fname
                if p.exists():
                    try:
                        llms_txt_text = p.read_text(encoding="utf-8")
                    except OSError:
                        llms_txt_text = None
            continue
        except NetworkError as e:
            if not quiet:
                print(f"  Network error fetching {fname}: {e}", file=sys.stderr)
            print("network-error")
            return 2

        # With an empty meta_entry, fetch_with_fallback always returns "changed".
        _, text, entry_meta = result
        (cache_dir / fname).write_text(text, encoding="utf-8")
        new_meta[key] = {**entry_meta, "url_used": url_used}
        if not quiet:
            print(f"  Wrote {fname} ({len(text):,} chars) from {url_used}")
        if key == "llms_txt":
            llms_txt_text = text

    if degraded:
        new_meta["degraded_endpoints"] = degraded
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
