#!/usr/bin/env node

/**
 * OpenJudge NPM Wrapper
 * This script serves as the bridge allowing Node.js users to run 
 * the Python-based OpenJudge engine globally using `npx openjudge`.
 */

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const mainPyPath = path.join(__dirname, '..', 'main.py');

// Check if Python dependencies are likely installed (look for .env or requirements logic)
console.log("\x1b[36m[OpenJudge] Starting engine wrapper...\x1b[0m");

// We prefer 'python3', but fallback to 'python' (especially on Windows)
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

const result = spawnSync(pythonCmd, [mainPyPath, ...process.argv.slice(2)], {
    stdio: 'inherit'
});

if (result.error) {
    console.error(`\x1b[31m[OpenJudge Fatal Error]\x1b[0m Could not spawn Python process. Is Python installed?`);
    console.error(result.error);
    process.exit(1);
}

process.exit(result.status);
