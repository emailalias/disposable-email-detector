import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const dataDir = join(here, "..", "..", "..", "data");

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
