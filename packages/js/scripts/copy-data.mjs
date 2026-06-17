// Copies the shared data/ files from the repo root into packages/js/data/
// so they're included in the npm tarball. Wired to `prepublishOnly` in
// package.json — runs automatically before `npm publish`.
//
// Path resolution in src/domains.js prefers the local copy (published
// layout) and falls back to ../../../data (source-checkout layout), so
// running tests in the dev tree doesn't require this copy to exist.

import { copyFileSync, mkdirSync, existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRootData = join(here, "..", "..", "..", "data");
const dest = join(here, "..", "data");

if (existsSync(dest)) rmSync(dest, { recursive: true });
mkdirSync(dest, { recursive: true });

const files = [
  "disposable-domains.json",
  "forwarding-alias-domains.json",
  "personally-observed-domains.json",
];
for (const f of files) {
  copyFileSync(join(repoRootData, f), join(dest, f));
  console.log(`copied ${f}`);
}
