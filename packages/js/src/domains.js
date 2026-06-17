import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));

// Resolve the data directory across two layouts:
//   1. Published npm package — data/ lives next to src/ (one level up).
//   2. Source checkout — data/ lives at the repo root (three levels up
//      from packages/js/src/).
// prepublishOnly copies data/ into layout #1 before `npm publish`, so
// installed users hit candidate 0; running tests / npm link in the dev
// tree hits candidate 1.
const CANDIDATE_DATA_DIRS = [
  join(here, "..", "data"),
  join(here, "..", "..", "..", "data"),
];

const dataDir = CANDIDATE_DATA_DIRS.find((d) =>
  existsSync(join(d, "disposable-domains.json"))
);

if (!dataDir) {
  throw new Error(
    `Could not locate disposable-domains.json. Tried: ${CANDIDATE_DATA_DIRS.join(", ")}`
  );
}

function loadJson(name) {
  return JSON.parse(readFileSync(join(dataDir, name), "utf8"));
}

const disposableJson = loadJson("disposable-domains.json");
const forwardingJson = loadJson("forwarding-alias-domains.json");

export const DISPOSABLE_DOMAINS = new Set(
  disposableJson.domains.map((d) => d.toLowerCase())
);

export const FORWARDING_ALIAS_DOMAINS = new Map();
for (const [provider, domains] of Object.entries(forwardingJson.providers)) {
  for (const d of domains) {
    FORWARDING_ALIAS_DOMAINS.set(d.toLowerCase(), provider);
  }
}
