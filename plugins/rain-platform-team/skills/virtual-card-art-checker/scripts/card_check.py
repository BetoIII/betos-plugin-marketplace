#!/usr/bin/env python3
"""Client for Rain's Card Art Checker service (card-art-checker.vercel.app).

Hands one virtual card image to the service and waits for its result. The
service runs every check; this script only uploads, waits, and formats.

Usage:
  card_check.py start --file PATH (--tenant-id UUID | --project-id DIGITS)
                      [--product NAME] [--base-url URL]
  card_check.py wait  --job JOB [--max-seconds 85] [--out-dir DIR]

`start` returns at once. An anonymous check only runs while its caller holds
the connection open, so a detached curl holds the service's event stream and
writes it to /tmp/card-art-check/<job>/. `wait` reads that stream for up to
--max-seconds at a time, which keeps each call under Cowork's per-command
time limit (about 180s; a check takes about 2 minutes).

wait exit codes:
  0   complete: report printed, result.json saved in the job folder
  2   the service reported an error
  3   the stream ended without a result (connection lost or blocked)
  10  still running: call wait again
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

DEFAULT_BASE_URL = "https://card-art-checker.vercel.app"
JOBS_DIR = "/tmp/card-art-check"

# Vercel caps a request body at 4.5 MB; leave room for the multipart framing.
MAX_FILE_BYTES = 4_400_000

# Same shapes as lib/partner-id.js in the service.
PROJECT_ID_RE = re.compile(r"^\d{1,12}$")
TENANT_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

# Same list and matching as normalizeDeclaredProduct in lib/pipeline.js:
# longest names first, so "Signature Corporate" wins over "Signature".
PRODUCTS = sorted(
    [
        "Debit", "Business Debit", "Corporate",
        "Platinum", "Platinum Business", "Platinum Corporate",
        "Signature", "Signature Business", "Signature Corporate",
        "Infinite", "Infinite Business", "Infinite Corporate",
        "Business", "Classic",
    ],
    key=len,
    reverse=True,
)

STATUS_MARK = "\n__CARD_CHECK_HTTP_STATUS__ "

EXIT_COMPLETE, EXIT_ERROR, EXIT_LOST, EXIT_RUNNING = 0, 2, 3, 10

# Labels from the "Technical checks" table on /reference.
TECH_LABELS = {
    "dimensions": "Canvas size",
    "file_format": "File type",
    "dpi": "Declared density",
    "bleed_zone": "Brand Mark distance from the edges",
    "mark_position": "Brand Mark corner",
    "mark_size": "Brand Mark height",
    "identifier_alignment": "Identifier placement",
    "mark_color": "Brand Mark ink",
    "lockup_match": "Mark + identifier artwork",
    "identifier_clearance": "Pixels touching the identifier",
    "issuer_logo_border": "Partner logo distance from the edges",
    "square_corners": "Canvas corners",
    "border_frame": "Lines along the edges",
}

OUTCOME_LABELS = {
    "approved": "✅ Approved",
    "approved_with_notes": "⚠️ Approved with notes",
    "requires_changes": "❌ Requires changes",
}

STATUS_LABELS = {
    "pass": "✅ Pass",
    "fail": "❌ Fail",
    "warning": "⚠️ Warning",
    "unverified": "❔ Unverified",
    "not_submitted": "– Not submitted",
    "estimated": "≈ Estimated",
}

# What to tell the user for each error code the service can send.
ERROR_HINTS = {
    "missing_project_id": "The partner id was missing, malformed, or not a Rocketlane project. Check the id and run again.",
    "card_art_missing": "The service received no file. Check the file and run again.",
    "card_type_indeterminate": "The service could not tell the card type from the file. Send a PNG.",
    "visual_budget_exhausted": "The service ran short on time. Retry once.",
    "function_timeout": "The service ran out of time. Retry once.",
    "abandoned": "The run stopped before finishing. Retry once.",
    "agent_output_unparseable": "The review produced unreadable output. Retry once.",
    "spec_check_failed": "The automated measurements failed. Retry once; if it fails again, report the run id.",
    "internal_error": "Unexpected service error. Retry once; if it fails again, report the run id.",
}


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def job_dir(job):
    if not re.fullmatch(r"[A-Za-z0-9._-]+", job or ""):
        fail(f"Invalid job id: {job!r}")
    return os.path.join(JOBS_DIR, job)


def normalize_product(value):
    text = " " + re.sub(r"[^a-z]+", " ", value.lower()).strip() + " "
    return next((p for p in PRODUCTS if f" {p.lower()} " in text), None)


def curl_form_file(path):
    # curl's -F treats ; and , in a bare path as separators; quote it.
    escaped = path.replace("\\", "\\\\").replace('"', '\\"')
    return f'file=@"{escaped}"'


# ── start ────────────────────────────────────────────────────────────


def cmd_start(args):
    if not shutil.which("curl"):
        fail("curl is not installed in this environment.")

    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        fail(f"No file at {path}. Attach the image with the file picker so it is on disk.")
    size = os.path.getsize(path)
    if size == 0:
        fail(f"{os.path.basename(path)} is empty.")
    if size > MAX_FILE_BYTES:
        fail(
            f"{os.path.basename(path)} is {size / 1_000_000:.1f} MB; the service accepts up to "
            f"{MAX_FILE_BYTES / 1_000_000:.1f} MB. A standard 1536x969 PNG is well under this, "
            "so the file is probably not the final export."
        )

    project_id = (args.project_id or "").strip()
    tenant_id = (args.tenant_id or "").strip().lower()
    if not project_id and not tenant_id:
        fail("A partner id is required: --project-id (Rocketlane Project ID) or --tenant-id (Production Tenant ID).")
    if project_id and not PROJECT_ID_RE.match(project_id):
        fail(f"Invalid Rocketlane Project ID {project_id!r}: expected digits only.")
    if tenant_id and not TENANT_ID_RE.match(tenant_id):
        fail(f"Invalid Production Tenant ID {tenant_id!r}: expected a UUID.")

    product = None
    if args.product:
        product = normalize_product(args.product)
        if not product:
            fail(f"Unknown Visa product {args.product!r}. Use one of: {', '.join(sorted(PRODUCTS))}.")

    file_name = os.path.basename(path)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", os.path.splitext(file_name)[0]).strip("-").lower()
    job = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{stem[:40] or 'card'}"
    folder = job_dir(job)
    os.makedirs(folder, exist_ok=True)

    url = args.base_url.rstrip("/") + "/api/card-check"
    cmd = [
        "curl", "-sS", "-N", "--max-time", "300",
        "-X", "POST", url,
        "-H", "Accept: text/event-stream",
        "-w", STATUS_MARK + "%{http_code}\n",
        "-F", curl_form_file(path),
        "-F", "cardType=virtual",
        "-F", f"reference=cowork-{job}",
    ]
    if project_id:
        cmd += ["-F", f"projectId={project_id}"]
    if tenant_id:
        cmd += ["-F", f"tenantId={tenant_id}"]
    if product:
        cmd += ["-F", f"declaredProduct={product}"]

    with open(os.path.join(folder, "stream.sse"), "wb") as out, \
            open(os.path.join(folder, "curl.err"), "wb") as err:
        proc = subprocess.Popen(
            cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
            start_new_session=True, close_fds=True,
        )

    meta = {
        "job": job,
        "pid": proc.pid,
        "file": path,
        "file_name": file_name,
        "project_id": project_id or None,
        "tenant_id": tenant_id or None,
        "product": product,
        "base_url": args.base_url,
        "started_at": time.time(),
    }
    with open(os.path.join(folder, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    if not file_name.lower().endswith(".png"):
        print(f"Note: {file_name} is not a PNG; the service will fail the file-format check.")
    print(f"Started check {job} for {file_name}.")
    print(f"Next: card_check.py wait --job {job}")


# ── wait ─────────────────────────────────────────────────────────────


def read_stream(folder):
    """Return (frames, http_status). Only frames whose blank-line terminator
    has arrived are returned; http_status is set once curl has finished."""
    try:
        with open(os.path.join(folder, "stream.sse"), "rb") as f:
            text = f.read().decode("utf-8", errors="replace")
    except OSError:
        return [], None

    http_status = None
    if STATUS_MARK in text:
        text, _, tail = text.rpartition(STATUS_MARK)
        http_status = tail.strip()[:3]
        text += "\n\n"

    frames = []
    body = text[: text.rfind("\n\n") + 2] if "\n\n" in text else ""
    for block in body.split("\n\n"):
        event, data = None, []
        for line in block.split("\n"):
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data.append(line[5:].lstrip())
        if not event:
            continue
        try:
            payload = json.loads("\n".join(data)) if data else {}
        except ValueError:
            payload = {"raw": "\n".join(data)}
        frames.append((event, payload))
    return frames, http_status


def process_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().split(") ", 1)[1][:1] != "Z"
    except (OSError, IndexError):
        return True


def lost_stream(folder, frames, http_status):
    try:
        with open(os.path.join(folder, "curl.err"), errors="replace") as f:
            err = f.read().strip()
    except OSError:
        err = ""
    with open(os.path.join(folder, "stream.sse"), errors="replace") as f:
        body = f.read().split(STATUS_MARK)[0].strip()

    print("The check ended without a result.")
    if "403" in err or "blocked-by-allowlist" in err or "CONNECT" in err:
        print(
            "Cowork's network allowlist blocked the request. An Org Owner needs to add "
            "card-art-checker.vercel.app under Organization settings > Capabilities > "
            "Code execution > Additional allowed domains."
        )
    elif http_status and http_status != "200":
        print(f"The service answered HTTP {http_status}.")
        if body:
            print(body[:600])
    else:
        print("The connection closed before the result arrived. Running the check again starts a new run.")
    if err:
        print(f"curl: {err[-600:]}")
    return EXIT_LOST


def fmt_value(value):
    if value is None:
        return "–"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, separators=(",", ":"))
    text = str(value).replace("|", "/").replace("\n", " ")
    return text if len(text) <= 90 else text[:87] + "…"


def check_link(base_url, check):
    return f"[{check.get('name') or check['id']}]({base_url.rstrip('/')}/reference#check-{check['id']})"


def download_pdf(url, out_dir, file_name):
    if not url or not out_dir:
        return None
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(file_name)[0]
    dest = os.path.join(out_dir, f"{stem}_card_art_report.pdf")
    done = subprocess.run(
        ["curl", "-fsSL", "--max-time", "60", "-o", dest, url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if done.returncode == 0 and os.path.getsize(dest) > 0:
        return dest
    try:
        os.remove(dest)
    except OSError:
        pass
    return None


def render_report(meta, data, pdf_path):
    result = data.get("result") or {}
    base = meta["base_url"]
    lines = []

    file_name = (result.get("submission") or {}).get("file_name") or meta["file_name"]
    outcome = result.get("outcome") or data.get("outcome")
    lines.append(f"## Card art check: {file_name}")
    lines.append("")
    lines.append(f"**{OUTCOME_LABELS.get(outcome, outcome or 'Unknown')}**: {result.get('summary') or data.get('summary') or ''}".rstrip(": "))
    lines.append("")

    project = result.get("project") or {}
    tenant = result.get("tenant") or {}
    submission = result.get("submission") or {}
    facts = []
    if project.get("id"):
        facts.append(f"Rocketlane project: {project.get('name') or project['id']} ({project['id']})")
    if tenant.get("id"):
        facts.append(f"Production tenant: {tenant['id']}")
    if submission.get("detected_product"):
        facts.append(f"Product on card: {submission['detected_product']}")
    if submission.get("declared_product"):
        facts.append(f"Declared product: {submission['declared_product']}")
    facts.append(f"Run: {result.get('run_id') or data.get('runId')}")
    lines.append(" · ".join(facts))

    checks = result.get("checks") or []
    tech = result.get("tech_checks") or []
    failed = [c for c in checks if c.get("status") == "fail"]
    tech_failed = [t for t in tech if t.get("status") == "fail"]
    warned = [c for c in checks if c.get("status") == "warning"]
    tech_warned = [t for t in tech if t.get("status") == "warning"]
    unverified = [c for c in checks if c.get("status") == "unverified"]

    if failed or tech_failed:
        lines += ["", "### Must fix"]
        for c in failed:
            tag = " (blocking)" if c.get("severity") == "blocker" else ""
            lines.append(f"- ❌ {check_link(base, c)}{tag}: {c.get('notes') or c.get('reason_code') or ''}".rstrip(": "))
        for t in tech_failed:
            label = TECH_LABELS.get(t["id"], t["id"])
            note = f" {t['note']}" if t.get("note") else ""
            lines.append(f"- ❌ {label} (`{t['id']}`): measured {fmt_value(t.get('actual'))}, required {fmt_value(t.get('required'))}.{note}")

    if warned or tech_warned:
        lines += ["", "### Warnings"]
        for c in warned:
            lines.append(f"- ⚠️ {check_link(base, c)}: {c.get('notes') or c.get('reason_code') or ''}".rstrip(": "))
        for t in tech_warned:
            label = TECH_LABELS.get(t["id"], t["id"])
            note = f" {t['note']}" if t.get("note") else ""
            lines.append(f"- ⚠️ {label} (`{t['id']}`): measured {fmt_value(t.get('actual'))}, required {fmt_value(t.get('required'))}.{note}")

    if unverified:
        names = ", ".join(c.get("name") or c["id"] for c in unverified)
        lines += ["", f"**Not assessed by the service:** {names}. A person should look at these before approving."]

    if tech:
        lines += ["", "### Technical checks", "", "| Check | Result | Measured | Required |", "|---|---|---|---|"]
        for t in tech:
            label = TECH_LABELS.get(t["id"], t["id"])
            status = STATUS_LABELS.get(t.get("status"), t.get("status"))
            lines.append(f"| {label} | {status} | {fmt_value(t.get('actual'))} | {fmt_value(t.get('required'))} |")

    colors = result.get("colors") or {}
    if colors:
        lines += ["", "### Suggested fallback colors", "", "| Role | RGB | Hex |", "|---|---|---|"]
        for role, color in colors.items():
            rgb = color.get("rgb")
            rgb_text = f"rgb({', '.join(str(v) for v in rgb)})" if isinstance(rgb, list) else fmt_value(rgb)
            lines.append(f"| {role.replace('_', ' ').capitalize()} | `{rgb_text}` | `{color.get('hex') or '–'}` |")
        lines += ["", "These are suggestions from the art; the designer should confirm them."]

    passed = sum(1 for c in checks if c.get("status") == "pass")
    tech_passed = sum(1 for t in tech if t.get("status") == "pass")
    lines += ["", f"Passed {passed} of {len(checks)} visual checks and {tech_passed} of {len(tech)} technical checks."]

    pdf_url = (result.get("report") or {}).get("pdf_url") or data.get("pdfUrl")
    if pdf_path:
        lines.append(f"Annotated report saved: {pdf_path}")
    if pdf_url:
        lines.append(f"Annotated report link: {pdf_url}")
    return "\n".join(lines)


def cmd_wait(args):
    folder = job_dir(args.job)
    try:
        with open(os.path.join(folder, "meta.json")) as f:
            meta = json.load(f)
    except OSError:
        fail(f"No job {args.job!r} in {JOBS_DIR}. Start it again with card_check.py start.")

    state_path = os.path.join(folder, "seen.json")
    try:
        with open(state_path) as f:
            seen = json.load(f).get("progress", 0)
    except (OSError, ValueError):
        seen = 0

    deadline = time.time() + max(5, args.max_seconds)
    last_step = None
    while True:
        frames, http_status = read_stream(folder)

        progress = [p for e, p in frames if e == "progress"]
        for p in progress[seen:]:
            print(f"• {p.get('message') or p.get('step')}")
        seen = max(seen, len(progress))
        with open(state_path, "w") as f:
            json.dump({"progress": seen}, f)
        if progress:
            last_step = progress[-1].get("message") or progress[-1].get("step")

        for event, payload in frames:
            if event == "complete":
                with open(os.path.join(folder, "result.json"), "w") as f:
                    json.dump(payload.get("result") or payload, f, indent=2)
                pdf_url = ((payload.get("result") or {}).get("report") or {}).get("pdf_url") or payload.get("pdfUrl")
                pdf_path = download_pdf(pdf_url, args.out_dir, meta["file_name"])
                print()
                print(render_report(meta, payload, pdf_path))
                return EXIT_COMPLETE
            if event == "error":
                code = payload.get("code") or "internal_error"
                print(f"The service could not finish the check: {code}: {payload.get('message') or ''}".rstrip(": "))
                if payload.get("step"):
                    print(f"Step: {payload['step']}")
                print(ERROR_HINTS.get(code, ERROR_HINTS["internal_error"]))
                return EXIT_ERROR

        if http_status is not None or not process_alive(meta["pid"]):
            return lost_stream(folder, frames, http_status)

        if time.time() >= deadline:
            elapsed = int(time.time() - meta["started_at"])
            print(f"Still running ({elapsed}s since start). Last step: {last_step or 'waiting for the service'}")
            print(f"Next: card_check.py wait --job {meta['job']}")
            return EXIT_RUNNING
        time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="upload one image and start a check")
    start.add_argument("--file", required=True)
    start.add_argument("--project-id", help="Rocketlane Project ID (digits)")
    start.add_argument("--tenant-id", help="Production Tenant ID (UUID)")
    start.add_argument("--product", help="Visa product the program is provisioned as, e.g. Signature")
    start.add_argument("--base-url", default=DEFAULT_BASE_URL)

    wait = sub.add_parser("wait", help="wait for a started check")
    wait.add_argument("--job", required=True)
    wait.add_argument("--max-seconds", type=int, default=85)
    wait.add_argument("--out-dir", help="folder to save the annotated PDF into")

    args = parser.parse_args()
    if args.command == "start":
        cmd_start(args)
        return 0
    return cmd_wait(args)


if __name__ == "__main__":
    sys.exit(main())
