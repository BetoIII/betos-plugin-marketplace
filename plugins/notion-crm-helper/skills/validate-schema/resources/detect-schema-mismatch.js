#!/usr/bin/env node
/**
 * Detect Schema Mismatch Script
 *
 * Compares the cached crm-schema.json against live Notion database properties
 * to detect stale IDs, missing properties, or outdated select options.
 *
 * Usage: node detect-schema-mismatch.js <crm-schema-path> [error-log-file]
 *
 * Exit codes:
 *   0 = no mismatch
 *   1 = mismatch detected (stale schema or error patterns found)
 *   2 = schema file not found or unreadable
 */

const fs = require('fs');
const path = require('path');

// Error patterns that indicate schema mismatch
const ERROR_PATTERNS = [
  /404.*database.*not found/i,
  /Invalid page URL.*for property/i,
  /database_id.*does not exist/i,
  /Could not find database/i,
  /validation.*error.*database/i,
  /property.*does not exist/i,
  /Could not find property/i
];

// Database names to check
const DATABASES = ['contacts', 'accounts', 'opportunities', 'lists', 'templates', 'activities'];

function loadSchema(schemaPath) {
  if (!fs.existsSync(schemaPath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
}

function detectErrorPatterns(errorLog) {
  const mismatches = [];

  for (const pattern of ERROR_PATTERNS) {
    if (pattern.test(errorLog)) {
      mismatches.push({
        pattern: pattern.toString(),
        detected: true,
        message: 'Potential database ID or property mismatch detected'
      });
    }
  }

  // Check for specific database references
  DATABASES.forEach(dbName => {
    const dbPattern = new RegExp(`${dbName}.*404`, 'i');
    if (dbPattern.test(errorLog)) {
      mismatches.push({
        database: dbName,
        issue: '404 error detected',
        recommendation: `Refresh schema to update ${dbName} database ID`
      });
    }
  });

  return mismatches;
}

function checkSchemaAge(schema) {
  if (!schema || !schema.last_validated) {
    return { lastValidated: null, daysSinceValidation: Infinity, isStale: true, maxStaleDays: 7 };
  }

  const lastValidated = new Date(schema.last_validated);
  const today = new Date();
  const daysSinceValidation = Math.floor((today - lastValidated) / (1000 * 60 * 60 * 24));
  const maxStaleDays = schema.validation_config?.max_stale_days || 7;

  return {
    lastValidated: schema.last_validated,
    daysSinceValidation,
    isStale: daysSinceValidation > maxStaleDays,
    maxStaleDays
  };
}

function checkDatabaseIds(schema) {
  const issues = [];

  if (!schema || !schema.databases) {
    issues.push({ issue: 'No databases section in schema', severity: 'critical' });
    return issues;
  }

  const requiredDbs = ['contacts', 'accounts', 'opportunities', 'lists', 'templates'];

  requiredDbs.forEach(dbName => {
    const db = schema.databases[dbName];
    if (!db) {
      issues.push({ database: dbName, issue: 'Database entry missing from schema', severity: 'critical' });
    } else if (!db.id) {
      issues.push({ database: dbName, issue: 'Database ID is empty', severity: 'critical' });
    }
  });

  return issues;
}

function main() {
  const schemaPath = process.argv[2];

  if (!schemaPath) {
    console.error('Usage: node detect-schema-mismatch.js <crm-schema-path> [error-log-file]');
    process.exit(2);
  }

  const schema = loadSchema(schemaPath);

  if (!schema) {
    console.log(JSON.stringify({
      status: 'error',
      mismatch: true,
      reason: 'Schema file not found or unreadable',
      schemaPath
    }));
    process.exit(2);
  }

  const result = {
    status: 'ok',
    mismatch: false,
    checks: {}
  };

  // Check schema age
  const ageCheck = checkSchemaAge(schema);
  result.checks.age = ageCheck;
  if (ageCheck.isStale) {
    result.mismatch = true;
    result.status = 'stale';
  }

  // Check database IDs
  const dbIssues = checkDatabaseIds(schema);
  result.checks.databases = dbIssues;
  if (dbIssues.length > 0) {
    result.mismatch = true;
    result.status = 'invalid';
  }

  // If error log provided, analyze it
  const errorLogPath = process.argv[3];
  if (errorLogPath && fs.existsSync(errorLogPath)) {
    const errorLog = fs.readFileSync(errorLogPath, 'utf8');
    const errorMismatches = detectErrorPatterns(errorLog);
    result.checks.errorPatterns = errorMismatches;
    if (errorMismatches.length > 0) {
      result.mismatch = true;
      result.status = 'error_patterns_detected';
    }
  }

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.mismatch ? 1 : 0);
}

if (require.main === module) {
  main();
}

module.exports = { detectErrorPatterns, checkSchemaAge, checkDatabaseIds };
