/**
 * Nitro traces the PGLite JS module but not companion binary assets.
 * Copy every .data / .wasm from @electric-sql/pglite/dist next to the
 * bundled electric-sql chunk so runtime locateFile / import.meta.url works.
 */
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  statSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const srcDir = join(root, "node_modules", "@electric-sql", "pglite", "dist");

function listBinaryAssets(dir, base = dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      listBinaryAssets(full, base, out);
    } else if (name.endsWith(".wasm") || name.endsWith(".data")) {
      out.push({ from: full, rel: full.slice(base.length + 1) });
    }
  }
  return out;
}

function findBundledPgliteDirs(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      findBundledPgliteDirs(full, out);
    } else if (name.includes("electric-sql__pglite")) {
      out.push(dirname(full));
    }
  }
  return out;
}

const candidates = [
  join(root, ".vercel", "output", "functions", "__server.func", "_libs"),
  join(root, ".vercel", "output", "functions", "__server.func"),
];

const dirs = new Set();
for (const base of candidates) {
  if (existsSync(base)) dirs.add(base);
  for (const found of findBundledPgliteDirs(base)) dirs.add(found);
}

if (dirs.size === 0) {
  console.warn("[copy-pglite-assets] no server output dirs found — skip");
  process.exit(0);
}

const assets = listBinaryAssets(srcDir);
if (assets.length === 0) {
  console.warn("[copy-pglite-assets] no source binaries found");
  process.exit(0);
}

let copied = 0;
for (const dir of dirs) {
  mkdirSync(dir, { recursive: true });
  for (const { from, rel } of assets) {
    // Flat copy into each target dir (pglite resolve uses basename / same-dir URLs)
    const to = join(dir, rel.includes("/") ? rel.split("/").pop() : rel);
    copyFileSync(from, to);
    copied += 1;
  }
  console.log(`[copy-pglite-assets] ${assets.length} assets → ${dir}`);
}

console.log(`[copy-pglite-assets] done (${copied} files)`);
