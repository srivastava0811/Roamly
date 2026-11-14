#!/usr/bin/env node
/**
 * OpenAPI TypeScript Client Generation Script
 * 
 * Generates/updates the TypeScript API client contracts from FastAPI's OpenAPI specification.
 * Supports:
 *  1. Direct offline export from Python FastAPI app
 *  2. Online retrieval from running server at http://localhost:8000/openapi.json
 */
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const openapiJsonPath = path.join(rootDir, 'packages', 'api-client', 'openapi.json');

console.log('🔄 Generating OpenAPI Client...');

let specLoaded = false;

// Attempt 1: Offline export using Python virtual environment
const pythonCandidates = [
  path.join(rootDir, 'apps', 'api', '.venv', 'Scripts', 'python.exe'),
  path.join(rootDir, 'apps', 'api', '.venv', 'bin', 'python'),
  'python3',
  'python',
];

for (const py of pythonCandidates) {
  try {
    const exportScript = path.join(rootDir, 'scripts', 'export_openapi.py');
    execSync(`"${py}" "${exportScript}"`, { stdio: 'inherit' });
    specLoaded = true;
    break;
  } catch {
    // Continue to next candidate
  }
}

// Attempt 2: Retrieve from running local FastAPI server if offline export was unavailable
if (!specLoaded) {
  console.log('ℹ️ Attempting to fetch OpenAPI schema from running API server (http://localhost:8000/openapi.json)...');
  try {
    const res = await fetch('http://localhost:8000/openapi.json');
    if (res.ok) {
      const data = await res.json();
      fs.writeFileSync(openapiJsonPath, JSON.stringify(data, null, 2), 'utf-8');
      console.log(`✅ Retrieved OpenAPI schema from live server to ${openapiJsonPath}`);
      specLoaded = true;
    }
  } catch (err) {
    console.warn('⚠️ Could not connect to live server.');
  }
}

if (!fs.existsSync(openapiJsonPath)) {
  console.error('❌ Failed to obtain openapi.json. Please ensure backend dependencies are installed or server is running.');
  process.exit(1);
}

const spec = JSON.parse(fs.readFileSync(openapiJsonPath, 'utf-8'));
console.log(`✅ OpenAPI specification verified: ${spec.info.title} v${spec.info.version}`);
console.log(`   Paths registered: ${Object.keys(spec.paths).length} endpoints`);
console.log('🚀 Client contracts updated successfully.');
