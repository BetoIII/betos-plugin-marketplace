---
name: virtual-card-art-checker
description: >
  Use this skill whenever someone submits, uploads, or shares card art for a **virtual or digital
  card** and wants it reviewed against Visa Digital Card Brand Standards and Rain's requirements.
  Trigger on phrases like "check this card art", "review my virtual card design", "does this
  pass", "card submission review", "validate card art", "check the digital card image", "is this
  compliant", or when a user uploads an image and mentions virtual cards, digital cards, Visa
  brand guidelines, or card art for digital use. Also use when the user asks for the RGB fallback
  colors for a virtual card. The review runs on Rain's Card Art Checker service
  (card-art-checker.vercel.app): this skill uploads the image, waits about two minutes, and
  presents the service's result and annotated PDF report.
---

# Virtual Card Art Checker

Rain's Card Art Checker service does the whole review. It runs 13 automated measurements and a
22-check visual review against Visa Digital Card Brand Standards, then produces an annotated PDF.
This skill hands one image to the service through `scripts/card_check.py` in this skill's
directory, waits for the result, and presents it.

**The service's verdict is the answer.** Do not re-review the art yourself, add checks of your
own, or change a result. If a result looks wrong, say so separately and suggest the user report
it to the platform team with the run id.

## Step 1: Get the image file

The image must be a file on disk:
- **Attached with the file picker**: it is in the session's `mnt/uploads/` folder
  (`ls /sessions/*/mnt/uploads/`).
- **In a folder the user connected**: it is under the session's `mnt/<folder name>/`.
- **A path the user gave you**: use it as is.

An image pasted into the message is **not** saved to disk, so ask the user to attach it with the
file picker. Do the same for Slack, Drive, or other links: ask the user to download the file and
attach it.

Virtual card art should be a 1536×969 PNG. Send other image files anyway; the service fails the
file-type check and says so. With several images, run one check per file: start them all, then
wait on each.

## Step 2: Get the partner

Every check must name the partner with one of:
- **Rocketlane Project ID**: digits only, for example `412345`.
- **Production Tenant ID**: the partner's UUID from Weatherstation.

If the user names a company instead and a Rocketlane connector is available, look up the project
and confirm it with the user before starting. Do not guess an id.

If the user says which Visa product the program is (for example Signature, Platinum, or Infinite
Corporate), pass it with `--product` so the service checks that the card's identifier matches.
Otherwise leave it out.

## Step 3: Run the check

Start it (bash `timeout_ms` 30000):

```bash
python3 "<this-skill-dir>/scripts/card_check.py" start --file "<path to image>" --project-id <id>
# or --tenant-id <uuid>; add --product "<product>" when known
```

It prints a job id and returns at once. Then wait (bash `timeout_ms` 120000), saving the PDF to
the session's outputs folder (`/sessions/<session>/mnt/outputs` in Cowork):

```bash
python3 "<this-skill-dir>/scripts/card_check.py" wait --job <job id> --out-dir "<outputs folder>"
```

Each `wait` call returns within about 90 seconds. Act on its exit code:

| Exit | Meaning | What to do |
|---|---|---|
| 10 | Still running | Give the user one line of progress, then call `wait` again |
| 0 | Done | Go to Step 4 |
| 2 | The service reported an error | Relay the printed hint; retry once if it says to |
| 3 | No result: blocked, or the connection dropped | Relay the printed message; see Troubleshooting |
| 1 | Bad input | Fix what the message says (file, id, or product) and start again |

A check usually takes about 2 minutes. Each one is a real, paid run, so do not start duplicates.
If you lose track of a job id, `ls /tmp/card-art-check/` lists them.

## Step 4: Present the result

Show the report that `wait` printed, unchanged: outcome, summary, must-fix items, warnings,
technical checks, fallback colors, and the PDF. Then add one or two plain sentences on what the
designer needs to change, or that the art is ready to submit. Point to the annotated PDF in the
outputs folder; if it could not be saved, give the link instead.

How to read the outcome:
- `Requires changes`: send the art back to the designer with the must-fix list.
- `Approved with notes`: it can go to Visa; the notes are advice.
- `Approved`: ready to submit.
- Checks listed under "Not assessed by the service" need a person to look at them.

## Troubleshooting

- **"Cowork's network allowlist blocked the request"**: an Org Owner must add
  `card-art-checker.vercel.app` under Organization settings > Capabilities > Code execution >
  Additional allowed domains. Nothing else fixes this.
- **Link only, no saved PDF**: the report's storage host is not on the allowlist. The link opens
  in a browser.
- **`missing_project_id`**: the id is wrong, or Rocketlane has no such project. Confirm the id
  with the user.
- **File over 4.4 MB**: the service cannot accept it. A correct 1536×969 PNG is far smaller, so
  ask for the final export.
- **Connection dropped** (exit 3 with no other reason): offer to run the check again. That starts
  a new run.

## Not covered

Physical card art (.ai, .eps, or print PNGs) is out of scope for this skill; send people to
https://card-art-checker.vercel.app/upload for those. What each check means is documented at
https://card-art-checker.vercel.app/reference.
