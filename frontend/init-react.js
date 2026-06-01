#!/usr/bin/env node

/**
 * React Frontend Initialization Script
 * Creates all necessary directories and starter files for Crop Zen React dashboard
 */

const fs = require('fs');
const path = require('path');

const dirs = [
  'src/components/Auth',
  'src/components/Dashboard',
  'src/components/Farms',
  'src/components/Predictions',
  'src/components/Common',
  'src/pages',
  'src/services',
  'src/redux/slices',
  'src/hooks',
  'src/utils',
  'public'
];

// Create directories
console.log('📁 Creating directories...');
dirs.forEach(dir => {
  const fullPath = path.join(__dirname, dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`  ✅ ${dir}`);
  }
});

console.log('\n✅ Frontend structure created successfully!');
console.log('\nNext steps:');
console.log('1. npm install');
console.log('2. cp .env.example .env');
console.log('3. npm run dev');
