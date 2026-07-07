const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'src');

function resolveImport(importPath, fromFile) {
  if (importPath.startsWith('@/')) {
    importPath = importPath.replace('@/', './src/');
  }
  
  const fromDir = path.dirname(fromFile);
  let resolved = path.resolve(fromDir, importPath);
  
  // Try with extensions
  const extensions = ['.js', '.vue', '.ts'];
  for (const ext of extensions) {
    if (fs.existsSync(resolved + ext)) {
      return resolved + ext;
    }
  }
  
  // Try index file in directory
  for (const ext of extensions) {
    const indexPath = path.join(resolved, 'index' + ext);
    if (fs.existsSync(indexPath)) {
      return indexPath;
    }
  }
  
  return null;
}

function extractImports(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const imports = [];
  
  // Match import ... from '...'
  const importRegex = /import\s+.*?\s+from\s+['"](.+?)['"];?/g;
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  // Match import('...')
  const dynamicImportRegex = /import\s*\(\s*['"](.+?)['"]\s*\)/g;
  while ((match = dynamicImportRegex.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  return imports;
}

const graph = {};
const allFiles = [];

function walkDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkDir(fullPath);
    } else if (entry.name.endsWith('.js') || entry.name.endsWith('.vue') || entry.name.endsWith('.ts')) {
      allFiles.push(fullPath);
    }
  }
}

walkDir(srcDir);

for (const file of allFiles) {
  const imports = extractImports(file);
  graph[file] = [];
  for (const imp of imports) {
    // Skip node_modules and non-local imports
    if (imp.startsWith('.') || imp.startsWith('@/')) {
      const resolved = resolveImport(imp, file);
      if (resolved && fs.existsSync(resolved)) {
        graph[file].push(resolved);
      }
    }
  }
}

function findCycles(start, current, visited, path, cycles) {
  if (path.includes(current)) {
    const cycleStart = path.indexOf(current);
    const cycle = path.slice(cycleStart);
    cycles.push(cycle);
    return;
  }
  
  if (visited.has(current)) return;
  visited.add(current);
  path.push(current);
  
  const deps = graph[current] || [];
  for (const dep of deps) {
    findCycles(start, dep, new Set(visited), [...path], cycles);
  }
}

const cycles = [];
const checked = new Set();

for (const file of allFiles) {
  if (!checked.has(file)) {
    findCycles(file, file, new Set(), [], cycles);
    checked.add(file);
  }
}

// Remove duplicate cycles (same cycle, different start)
const uniqueCycles = [];
const seen = new Set();

for (const cycle of cycles) {
  const normalized = cycle.sort().join('::');
  if (!seen.has(normalized)) {
    seen.add(normalized);
    uniqueCycles.push(cycle);
  }
}

if (uniqueCycles.length === 0) {
  console.log('No circular dependencies found!');
} else {
  console.log(`Found ${uniqueCycles.length} circular dependencies:\n`);
  for (const cycle of uniqueCycles) {
    console.log('Cycle:');
    for (const file of cycle) {
      console.log('  ->', path.relative(__dirname, file));
    }
    console.log('');
  }
}
