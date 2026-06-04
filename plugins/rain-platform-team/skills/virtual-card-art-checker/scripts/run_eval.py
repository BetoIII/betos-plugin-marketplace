#!/usr/bin/env python3
"""
Eval runner for virtual-card-art-checker.
Runs check_technical_specs.py against each image in the eval CSV
and compares results to expected outcomes.
"""

import csv
import json
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(SCRIPT_DIR, "check_technical_specs.py")

def run_checker(image_path):
    """Run the technical spec checker and return parsed JSON output."""
    try:
        result = subprocess.run(
            [sys.executable, CHECKER, image_path, "--output-dir", "/tmp/card_eval"],
            capture_output=True, text=True, timeout=60
        )
        # Parse JSON from stdout (script outputs JSON)
        stdout = result.stdout.strip()
        if stdout:
            # Find the JSON object in output
            start = stdout.find("{")
            if start >= 0:
                return json.loads(stdout[start:])
        return {"error": result.stderr.strip() or "No JSON output"}
    except Exception as e:
        return {"error": str(e)}


def analyze_result(record_id, expected, failure_reason, checker_output):
    """Analyze checker output against expected result."""
    if "error" in checker_output:
        return {
            "script_verdict": "ERROR",
            "match": False,
            "details": checker_output["error"]
        }

    checks = checker_output.get("checks", {})

    # Determine script verdict
    any_fail = False
    any_borderline = False
    issues = []

    for check_name, check_data in checks.items():
        if not check_data.get("passed", True):
            any_fail = True
            issues.append(f"{check_name}: FAIL - {check_data.get('note', '')[:100]}")
        if check_data.get("borderline", False):
            any_borderline = True
            issues.append(f"{check_name}: BORDERLINE - {check_data.get('note', '')[:100]}")

    if any_fail:
        script_verdict = "FAIL"
    elif any_borderline:
        script_verdict = "WARN"
    else:
        script_verdict = "PASS"

    # Determine if script caught the issue
    expected_upper = expected.upper()

    if expected_upper == "FAIL":
        # For expected failures, check if the script flagged anything
        if script_verdict in ("FAIL", "WARN"):
            match = True
            detection = "DETECTED"
        else:
            match = False
            detection = "MISSED"
    else:  # expected PASS
        if script_verdict == "PASS":
            match = True
            detection = "CORRECT"
        elif script_verdict == "WARN":
            match = False  # false positive borderline warning
            detection = "FALSE_WARN"
        else:
            match = False
            detection = "FALSE_FAIL"

    # Extract bleed zone details
    bleed = checks.get("bleed_zone", {})
    bleed_detail = ""
    if bleed.get("mark_detected"):
        bleed_detail = bleed.get("actual", "")
    else:
        bleed_detail = "Mark not detected"

    return {
        "script_verdict": script_verdict,
        "match": match,
        "detection": detection,
        "issues": issues,
        "bleed_detail": bleed_detail,
        "dimensions_pass": checks.get("dimensions", {}).get("passed"),
        "format_pass": checks.get("file_format", {}).get("passed"),
        "dpi_pass": checks.get("dpi", {}).get("passed"),
        "bleed_pass": checks.get("bleed_zone", {}).get("passed"),
        "bleed_borderline": checks.get("bleed_zone", {}).get("borderline", False),
    }


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not csv_path or not os.path.exists(csv_path):
        print(f"Usage: {sys.argv[0]} <eval_csv_path>")
        sys.exit(1)

    os.makedirs("/tmp/card_eval", exist_ok=True)

    # Read CSV
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    results = []
    skipped = []

    for row in records:
        record_id = row["Record ID"]
        partner = row["Partner"]
        image_path = row["Card Art File Path"]
        expected = row["Expected Result"]
        failure_reason = row.get("Failure Reason", "")
        failure_type = row.get("Failure Type", "")

        print(f"\n{'='*60}")
        print(f"  {record_id} | {partner}")
        print(f"  Expected: {expected}")
        if failure_reason:
            print(f"  Failure reason: {failure_reason[:80]}")

        if not os.path.exists(image_path):
            print(f"  SKIPPED — file not found: {image_path}")
            skipped.append({"record_id": record_id, "partner": partner, "path": image_path})
            continue

        print(f"  Running checker...")
        checker_output = run_checker(image_path)
        analysis = analyze_result(record_id, expected, failure_reason, checker_output)

        analysis["record_id"] = record_id
        analysis["partner"] = partner
        analysis["expected"] = expected
        analysis["failure_reason"] = failure_reason
        analysis["failure_type"] = failure_type
        results.append(analysis)

        icon = "✅" if analysis["match"] else "❌"
        print(f"  Script verdict: {analysis['script_verdict']}")
        print(f"  Bleed zone: {analysis.get('bleed_detail', 'N/A')}")
        print(f"  {icon} {analysis.get('detection', 'N/A')}")
        if analysis.get("issues"):
            for issue in analysis["issues"]:
                print(f"    ⚠ {issue}")

    # === SUMMARY ===
    print(f"\n\n{'='*60}")
    print(f"  EVAL SUMMARY")
    print(f"{'='*60}")

    total = len(results)
    matched = sum(1 for r in results if r["match"])

    # Break down by expected result
    expected_fail = [r for r in results if r["expected"].upper() == "FAIL"]
    expected_pass = [r for r in results if r["expected"].upper() == "PASS"]

    tp = sum(1 for r in expected_fail if r["detection"] == "DETECTED")  # true positive
    fn = sum(1 for r in expected_fail if r["detection"] == "MISSED")    # false negative
    tn = sum(1 for r in expected_pass if r["detection"] == "CORRECT")   # true negative
    fp_warn = sum(1 for r in expected_pass if r["detection"] == "FALSE_WARN")
    fp_fail = sum(1 for r in expected_pass if r["detection"] == "FALSE_FAIL")
    fp = fp_warn + fp_fail

    print(f"\n  Total images evaluated: {total}")
    print(f"  Skipped (file not found): {len(skipped)}")
    print(f"\n  --- Confusion Matrix ---")
    print(f"  True Positives  (expected FAIL, script flagged):  {tp}")
    print(f"  False Negatives (expected FAIL, script missed):   {fn}")
    print(f"  True Negatives  (expected PASS, script passed):   {tn}")
    print(f"  False Positives (expected PASS, script flagged):  {fp} (WARN: {fp_warn}, FAIL: {fp_fail})")

    accuracy = matched / total * 100 if total else 0
    sensitivity = tp / (tp + fn) * 100 if (tp + fn) else 0
    specificity = tn / (tn + fp) * 100 if (tn + fp) else 0

    print(f"\n  --- Metrics ---")
    print(f"  Overall accuracy:    {accuracy:.1f}% ({matched}/{total})")
    print(f"  Sensitivity (recall): {sensitivity:.1f}% ({tp}/{tp+fn}) — catches known failures")
    print(f"  Specificity:          {specificity:.1f}% ({tn}/{tn+fp}) — avoids false alarms")

    # Detail on missed failures
    if fn > 0:
        print(f"\n  --- Missed Failures (False Negatives) ---")
        for r in expected_fail:
            if r["detection"] == "MISSED":
                print(f"  {r['record_id']} ({r['partner']}): {r['failure_reason'][:80]}")
                print(f"    Failure type: {r['failure_type']}")
                print(f"    Script saw: {r['script_verdict']} | Bleed: {r.get('bleed_detail', 'N/A')}")

    # Detail on false positives
    if fp > 0:
        print(f"\n  --- False Positives ---")
        for r in expected_pass:
            if r["detection"] in ("FALSE_WARN", "FALSE_FAIL"):
                print(f"  {r['record_id']} ({r['partner']}): Script said {r['script_verdict']}")
                print(f"    Bleed: {r.get('bleed_detail', 'N/A')}")
                if r.get("issues"):
                    for issue in r["issues"]:
                        print(f"    ⚠ {issue}")

    if skipped:
        print(f"\n  --- Skipped Files ---")
        for s in skipped:
            print(f"  {s['record_id']} ({s['partner']}): {s['path']}")

    print(f"\n{'='*60}")
    print(f"  NOTES:")
    print(f"  - Script checks: dimensions, format, DPI, 56px Visa Brand Mark margin")
    print(f"  - Visual-only issues (prohibited elements, logo size, contrast,")
    print(f"    lower-left placement) require Claude vision — NOT detectable by script")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
