#!/usr/bin/env node
// Gather the evidence needed to identify a customer's Slack channel.
//
// Deterministic data-fetch only — no judgment, no LLM, and it NEVER posts.
// It prints three sections in one run (project anchor, time-window candidates,
// name cross-check) so the caller can apply the confidence rules in SKILL.md
// without further round-trips.
//
//   node scripts/fetch-candidates.mjs --project 123456
//   node scripts/fetch-candidates.mjs --name "Acme Corp" --created-at 2026-03-04T18:22:00Z
//   node scripts/fetch-candidates.mjs --all
//   node scripts/fetch-candidates.mjs --project 123456 --json
//
// Requires SLACK_BOT_TOKEN (channels:read, ideally groups:read) and, for
// --project, ROCKETLANE_API_KEY. See "Credentials" in SKILL.md.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

// ── Credentials ─────────────────────────────────────────────────────
// Never takes a token on the command line. Reads the same config location the
// rocketlane-api skill writes, so ROCKETLANE_API_KEY is shared rather than
// duplicated. First file to define a key wins; the real environment beats all.

const CONFIG_DIR = path.join(os.homedir(), '.config/rain-claude');
const ENV_CANDIDATES = [
  path.join(CONFIG_DIR, 'slack.env'),
  path.join(CONFIG_DIR, 'rocketlane.env'),
  // Local convenience for the card-art-checker maintainer; absent elsewhere.
  path.join(os.homedir(), 'Applications/card-art-checker/.env.local'),
];

function parseEnvFile(file) {
  const out = {};
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch {
    return out;
  }
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (value) out[key] = value;
  }
  return out;
}

function loadEnv(explicitFile) {
  const files = explicitFile ? [explicitFile, ...ENV_CANDIDATES] : ENV_CANDIDATES;
  const merged = {};
  for (const file of files) {
    for (const [k, v] of Object.entries(parseEnvFile(file))) {
      if (merged[k] === undefined) merged[k] = v;
    }
  }
  for (const key of ['SLACK_BOT_TOKEN', 'ROCKETLANE_API_KEY', 'ROCKETLANE_SLACK_BOT_ID']) {
    if (process.env[key]) merged[key] = process.env[key];
  }
  return merged;
}

// ── Args ────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = { windowAfterHours: 48, windowBeforeHours: 1 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    switch (a) {
      case '--project': args.project = next(); break;
      case '--name': args.name = next(); break;
      case '--created-at': args.createdAt = next(); break;
      case '--name-contains': args.nameContains = next(); break;
      case '--window': args.windowAfterHours = Number(next()); break;
      case '--window-before': args.windowBeforeHours = Number(next()); break;
      case '--bot': args.botId = next(); break;
      case '--env-file': args.envFile = next(); break;
      case '--all': args.all = true; break;
      case '--json': args.json = true; break;
      case '-h': case '--help': args.help = true; break;
      default:
        if (a.startsWith('--')) throw new Error(`Unknown flag: ${a}`);
        if (!args.project) args.project = a;
    }
  }
  return args;
}

const USAGE = `Usage:
  fetch-candidates.mjs --project <rocketlaneProjectId> [options]
  fetch-candidates.mjs --name "<project name>" --created-at <iso|epochMs> [options]
  fetch-candidates.mjs --all

Options:
  --window <hours>         Upper bound after createdAt (default 48)
  --window-before <hours>  Lower bound before createdAt (default 1)
  --name-contains <frag>   Override the auto-derived cross-check fragment
  --bot <slackUserId>      Creator to filter on (default ROCKETLANE_SLACK_BOT_ID or U07DS8F9STS)
  --env-file <path>        Extra env file to consult first
  --all                    Dump every bot-created channel, newest first
  --json                   Machine-readable output`;

// ── Slack ───────────────────────────────────────────────────────────

async function slackCall(token, method, params) {
  const url = new URL(`https://slack.com/api/${method}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }
  for (let attempt = 0; attempt < 6; attempt++) {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (res.status === 429) {
      const wait = Number(res.headers.get('retry-after') || 5);
      await new Promise((r) => setTimeout(r, (wait + 1) * 1000));
      continue;
    }
    const body = await res.json();
    if (!body.ok) {
      throw Object.assign(new Error(`slack ${method} failed: ${body.error}`), {
        slackError: body.error,
        needed: body.needed,
      });
    }
    return body;
  }
  throw new Error(`slack ${method} failed: rate limited after 6 attempts`);
}

// Paginate conversations.list once and keep only channels the integration bot
// created. Falls back to public-only when the token lacks groups:read.
async function fetchBotChannels(token, botId) {
  let types = 'public_channel,private_channel';
  let privateScopeMissing = false;
  let channels = [];
  let pages = 0;
  let cursor;

  // while(true) rather than do-while: `continue` in a do-while jumps to the
  // cursor check, ending the loop exactly when the scope fallback resets it.
  while (true) {
    let body;
    try {
      body = await slackCall(token, 'conversations.list', {
        types,
        exclude_archived: false,
        limit: 200,
        cursor,
      });
    } catch (err) {
      if (err.slackError === 'missing_scope' && types.includes('private_channel')) {
        types = 'public_channel';
        privateScopeMissing = true;
        cursor = undefined;
        channels = [];
        pages = 0;
        continue;
      }
      throw err;
    }
    pages++;
    channels.push(...(body.channels ?? []));
    cursor = body.response_metadata?.next_cursor;
    if (!cursor) break;
  }

  return {
    privateScopeMissing,
    pages,
    totalChannels: channels.length,
    botChannels: channels
      .filter((c) => c.creator === botId)
      .map((c) => ({
        id: c.id,
        name: c.name,
        created: c.created,
        created_iso: new Date(c.created * 1000).toISOString(),
        is_archived: !!c.is_archived,
        is_private: !!c.is_private,
      }))
      .sort((a, b) => b.created - a.created),
  };
}

// ── Rocketlane ──────────────────────────────────────────────────────

async function getProject(apiKey, projectId) {
  const res = await fetch(`https://api.rocketlane.com/api/1.0/projects/${projectId}`, {
    headers: { 'api-key': apiKey },
  });
  if (!res.ok) throw new Error(`Rocketlane project lookup failed: ${res.status}`);
  const data = await res.json();
  const createdAt = data.createdAt;
  return {
    projectId: String(projectId),
    projectName: data.projectName || data.name,
    createdAt,
    createdAtIso: createdAt ? new Date(createdAt).toISOString() : undefined,
  };
}

// ── Formatting ──────────────────────────────────────────────────────

const squash = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

// Longest word of the project name is the most distinctive cross-check needle;
// fall back to the fully squashed name for single-word projects.
function deriveNeedle(projectName) {
  const words = (projectName || '')
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((w) => w.length >= 3 && !['the', 'inc', 'llc', 'ltd', 'corp', 'labs'].includes(w));
  if (words.length === 0) return squash(projectName).slice(0, 6);
  return words.sort((a, b) => b.length - a.length)[0];
}

function fmtDelta(seconds) {
  const sign = seconds < 0 ? '-' : '+';
  const s = Math.abs(seconds);
  if (s < 90) return `${sign}${s}s`;
  if (s < 5400) return `${sign}${(s / 60).toFixed(1)}m`;
  if (s < 172800) return `${sign}${(s / 3600).toFixed(1)}h`;
  return `${sign}${(s / 86400).toFixed(1)}d`;
}

function flags(c) {
  const f = [];
  if (c.is_archived) f.push('ARCHIVED');
  if (c.is_private) f.push('private');
  return f.length ? `  [${f.join(', ')}]` : '';
}

function printRows(rows, anchorSec) {
  if (rows.length === 0) {
    console.log('  (none)');
    return;
  }
  for (const c of rows) {
    const delta = anchorSec != null ? `  Δ${fmtDelta(c.created - anchorSec).padEnd(8)}` : '  ';
    console.log(`  ${c.created_iso.slice(0, 16).replace('T', ' ')}${delta}#${c.name}  (${c.id})${flags(c)}`);
  }
}

// ── Main ────────────────────────────────────────────────────────────

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || (!args.project && !args.all && !args.name)) {
    console.log(USAGE);
    process.exit(args.help ? 0 : 1);
  }

  const env = loadEnv(args.envFile);
  if (!env.SLACK_BOT_TOKEN) {
    console.error(
      'SLACK_BOT_TOKEN not found. Run the first-time setup in SKILL.md, which stores it at\n' +
      `${path.join(CONFIG_DIR, 'slack.env')} (chmod 600, outside any repo).`
    );
    process.exit(2);
  }
  const botId = args.botId || env.ROCKETLANE_SLACK_BOT_ID || 'U07DS8F9STS';

  // Anchor: either a Rocketlane project or a name/time supplied directly.
  let project = null;
  if (args.project) {
    if (!env.ROCKETLANE_API_KEY) {
      console.error(
        'ROCKETLANE_API_KEY not found — needed to resolve --project. Set it up via the\n' +
        'rocketlane-api skill, or anchor manually with --name and --created-at.'
      );
      process.exit(2);
    }
    project = await getProject(env.ROCKETLANE_API_KEY, args.project);
  } else if (args.name) {
    const ms = args.createdAt
      ? (/^\d+$/.test(args.createdAt) ? Number(args.createdAt) : Date.parse(args.createdAt))
      : undefined;
    project = {
      projectId: '(none)',
      projectName: args.name,
      createdAt: ms,
      createdAtIso: ms ? new Date(ms).toISOString() : undefined,
    };
  }

  const { botChannels, privateScopeMissing, pages, totalChannels } = await fetchBotChannels(
    env.SLACK_BOT_TOKEN,
    botId
  );

  const anchorSec = project?.createdAt ? Math.floor(project.createdAt / 1000) : null;
  const needle = (args.nameContains || (project ? deriveNeedle(project.projectName) : '')).toLowerCase();

  const after = anchorSec != null ? anchorSec - args.windowBeforeHours * 3600 : null;
  const before = anchorSec != null ? anchorSec + args.windowAfterHours * 3600 : null;

  const inWindow = anchorSec == null ? [] : botChannels
    .filter((c) => c.created >= after && c.created <= before)
    .sort((a, b) => a.created - b.created);

  const nameMatches = needle ? botChannels.filter((c) => c.name?.toLowerCase().includes(needle)) : [];

  if (args.json) {
    console.log(JSON.stringify({
      project, botId, privateScopeMissing, totalBotChannels: botChannels.length,
      window: { after, before, afterIso: after && new Date(after * 1000).toISOString(), beforeIso: before && new Date(before * 1000).toISOString() },
      needle, inWindow, nameMatches,
      ...(args.all ? { allBotChannels: botChannels } : {}),
    }, null, 2));
    return;
  }

  console.log(`Scanned ${totalChannels} channels over ${pages} page(s); ${botChannels.length} created by ${botId}.`);
  if (privateScopeMissing) {
    console.log('WARNING: token lacks groups:read — private channels are invisible. A "no candidates" result is not conclusive.');
  }
  console.log('');

  if (args.all && !project) {
    console.log(`All ${botChannels.length} bot-created channels (newest first):`);
    printRows(botChannels, null);
    return;
  }

  console.log(`Project: ${project.projectName}  (${project.projectId})`);
  console.log(`Created: ${project.createdAtIso ?? '(unknown — no time signal available)'}`);
  console.log('');

  if (anchorSec != null) {
    console.log(`── Time window [-${args.windowBeforeHours}h, +${args.windowAfterHours}h] → ${inWindow.length} candidate(s)`);
    printRows(inWindow, anchorSec);
    console.log('');
  } else {
    console.log('── Time window: skipped (no createdAt)\n');
  }

  console.log(`── Name cross-check, all time, name contains "${needle}" → ${nameMatches.length} match(es)`);
  printRows(nameMatches, anchorSec);
  console.log('');

  const windowIds = new Set(inWindow.map((c) => c.id));
  const conflicts = nameMatches.filter((c) => !windowIds.has(c.id));
  if (conflicts.length > 0) {
    console.log('!! REVIEW: name match(es) OUTSIDE the time window — adjudicate before concluding:');
    printRows(conflicts, anchorSec);
    console.log('');
  }

  if (args.all) {
    console.log(`── All ${botChannels.length} bot-created channels (newest first):`);
    printRows(botChannels, anchorSec);
  }
}

main().catch((err) => {
  console.error(String(err?.message || err));
  process.exit(1);
});
