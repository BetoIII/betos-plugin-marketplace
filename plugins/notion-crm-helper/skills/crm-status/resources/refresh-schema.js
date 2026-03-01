#!/usr/bin/env node
/**
 * Refresh Schema Script
 *
 * Takes live database property data (as JSON on stdin or via --data flag)
 * and merges it into the user's crm-schema.json file.
 *
 * Usage:
 *   echo '<json>' | node refresh-schema.js <crm-schema-path>
 *   node refresh-schema.js <crm-schema-path> --data '<json>'
 *   node refresh-schema.js <crm-schema-path> --dry-run --data '<json>'
 *
 * Input JSON format (one or more databases):
 * {
 *   "contacts": {
 *     "id": "<database-uuid>",
 *     "collection_id": "<collection://url>",
 *     "name": "<display name>",
 *     "properties": {
 *       "PropertyName": { "id": "<short-id>", "type": "<type>", "options": [...] }
 *     }
 *   },
 *   ...
 * }
 *
 * Exit codes:
 *   0 = schema updated (or dry-run complete)
 *   1 = no changes needed
 *   2 = error
 */

const fs = require('fs');
const path = require('path');

function loadSchema(schemaPath) {
  if (!fs.existsSync(schemaPath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
}

function buildSelectAliases(properties) {
  const aliases = {};
  for (const [propName, propDef] of Object.entries(properties)) {
    if ((propDef.type === 'select' || propDef.type === 'multi_select') && propDef.options) {
      const propAliases = {};
      for (const option of propDef.options) {
        // Strip leading emoji characters and trim
        const stripped = option.replace(/^[\u{1F300}-\u{1FFFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{200D}\u{20E3}]+/u, '').trim();
        if (stripped !== option) {
          propAliases[stripped] = option;
        }
      }
      if (Object.keys(propAliases).length > 0) {
        aliases[propName] = propAliases;
      }
    }
  }
  return aliases;
}

function incrementVersion(version) {
  if (!version) return '1.0.1';
  const parts = version.split('.');
  parts[2] = String(Number(parts[2]) + 1);
  return parts.join('.');
}

function mergeSchemaData(schema, newData, dryRun) {
  let changesDetected = false;
  const changes = [];

  for (const [dbKey, dbData] of Object.entries(newData)) {
    if (!schema.databases[dbKey]) {
      schema.databases[dbKey] = { id: '', collection_id: '', name: '', properties: {} };
    }

    const existing = schema.databases[dbKey];

    // Check and update database ID
    if (dbData.id && dbData.id !== existing.id) {
      changes.push({ database: dbKey, field: 'id', old: existing.id, new: dbData.id });
      if (!dryRun) existing.id = dbData.id;
      changesDetected = true;
    }

    // Check and update collection ID
    if (dbData.collection_id && dbData.collection_id !== existing.collection_id) {
      changes.push({ database: dbKey, field: 'collection_id', old: existing.collection_id, new: dbData.collection_id });
      if (!dryRun) existing.collection_id = dbData.collection_id;
      changesDetected = true;
    }

    // Check and update name
    if (dbData.name && dbData.name !== existing.name) {
      changes.push({ database: dbKey, field: 'name', old: existing.name, new: dbData.name });
      if (!dryRun) existing.name = dbData.name;
      changesDetected = true;
    }

    // Check and update properties
    if (dbData.properties) {
      for (const [propName, propDef] of Object.entries(dbData.properties)) {
        const existingProp = existing.properties[propName];
        if (!existingProp) {
          changes.push({ database: dbKey, field: `property:${propName}`, old: null, new: propDef });
          if (!dryRun) existing.properties[propName] = propDef;
          changesDetected = true;
        } else {
          // Check if property definition changed
          if (JSON.stringify(existingProp) !== JSON.stringify(propDef)) {
            changes.push({ database: dbKey, field: `property:${propName}`, old: existingProp, new: propDef });
            if (!dryRun) existing.properties[propName] = propDef;
            changesDetected = true;
          }
        }
      }

      // Rebuild select_option_aliases for this database
      if (!dryRun && changesDetected) {
        const aliases = buildSelectAliases(existing.properties);
        if (!schema.select_option_aliases) schema.select_option_aliases = {};
        schema.select_option_aliases[dbKey] = aliases;
      }
    }
  }

  if (changesDetected && !dryRun) {
    schema.last_updated = new Date().toISOString();
    schema.last_validated = new Date().toISOString();
    schema.version = incrementVersion(schema.version);
  }

  return { changesDetected, changes, schema };
}

async function readStdin() {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve(null);
      return;
    }
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => data += chunk);
    process.stdin.on('end', () => resolve(data.trim() || null));
    setTimeout(() => resolve(data.trim() || null), 1000);
  });
}

async function main() {
  const args = process.argv.slice(2);
  const schemaPath = args.find(a => !a.startsWith('--'));
  const dryRun = args.includes('--dry-run');
  const dataFlag = args.indexOf('--data');
  let inputJson = dataFlag >= 0 ? args[dataFlag + 1] : null;

  if (!schemaPath) {
    console.error('Usage: node refresh-schema.js <crm-schema-path> [--dry-run] [--data \'<json>\']');
    process.exit(2);
  }

  // Try stdin if no --data flag
  if (!inputJson) {
    inputJson = await readStdin();
  }

  if (!inputJson) {
    console.error('No input data provided. Pipe JSON via stdin or use --data flag.');
    process.exit(2);
  }

  let newData;
  try {
    newData = JSON.parse(inputJson);
  } catch (e) {
    console.error(`Failed to parse input JSON: ${e.message}`);
    process.exit(2);
  }

  let schema = loadSchema(schemaPath);
  if (!schema) {
    // Load template as fallback
    const templatePath = path.join(__dirname, '../../setup/resources/crm-schema.template.json');
    if (fs.existsSync(templatePath)) {
      schema = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
    } else {
      console.error('Schema file not found and no template available.');
      process.exit(2);
    }
  }

  const result = mergeSchemaData(schema, newData, dryRun);

  if (dryRun) {
    console.log(JSON.stringify({
      dryRun: true,
      changesDetected: result.changesDetected,
      changes: result.changes,
      schema: result.schema
    }, null, 2));
    process.exit(result.changesDetected ? 0 : 1);
  }

  if (result.changesDetected) {
    fs.writeFileSync(schemaPath, JSON.stringify(result.schema, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({
      status: 'updated',
      changesDetected: true,
      changes: result.changes,
      version: result.schema.version,
      lastValidated: result.schema.last_validated
    }, null, 2));
    process.exit(0);
  } else {
    console.log(JSON.stringify({
      status: 'no_changes',
      changesDetected: false,
      message: 'All database properties are current — no changes needed'
    }, null, 2));
    process.exit(1);
  }
}

main().catch(err => {
  console.error(`Unexpected error: ${err.message}`);
  process.exit(2);
});
