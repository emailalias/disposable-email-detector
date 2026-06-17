import { DISPOSABLE_DOMAINS, FORWARDING_ALIAS_DOMAINS } from "./domains.js";

const SUSPICIOUS_TLDS = new Set([
  "tk", "ml", "ga", "cf", "gq",
]);

const RANDOM_LOCAL_RE = /^[a-z]{1,3}[0-9]{4,}$|^[bcdfghjklmnpqrstvwxyz]{8,}$/i;
const TEMP_LOCAL_RE = /^(temp|throw|trash|spam|junk|burner|test|fake|noreply|donotreply)[a-z0-9._-]*/i;

function normalize(email) {
  if (typeof email !== "string") return null;
  const trimmed = email.trim().toLowerCase();
  if (!trimmed || trimmed.indexOf("@") === -1) return null;
  const at = trimmed.lastIndexOf("@");
  const local = trimmed.slice(0, at);
  const domain = trimmed.slice(at + 1);
  if (!local || !domain) return null;
  return { local, domain };
}

export function isDisposable(email) {
  const parts = normalize(email);
  if (!parts) return false;
  return DISPOSABLE_DOMAINS.has(parts.domain);
}

export function isForwardingAlias(email) {
  const parts = normalize(email);
  if (!parts) return false;
  return FORWARDING_ALIAS_DOMAINS.has(parts.domain);
}

export function forwardingAliasProvider(email) {
  const parts = normalize(email);
  if (!parts) return null;
  return FORWARDING_ALIAS_DOMAINS.get(parts.domain) || null;
}

export function check(email) {
  const parts = normalize(email);
  if (!parts) {
    return {
      verdict: "invalid",
      reason: "Email is empty or has no domain.",
      email: typeof email === "string" ? email : null,
      domain: null,
    };
  }

  const { local, domain } = parts;
  const tld = domain.split(".").pop();

  if (FORWARDING_ALIAS_DOMAINS.has(domain)) {
    return {
      verdict: "forwarding_alias",
      provider: FORWARDING_ALIAS_DOMAINS.get(domain),
      reason: "Address is a forwarding alias from a known provider — mail forwards to a real, permanent inbox the user controls. Do NOT treat as disposable.",
      email,
      domain,
      local,
    };
  }

  if (DISPOSABLE_DOMAINS.has(domain)) {
    return {
      verdict: "disposable",
      reason: `Domain ${domain} is on the curated disposable list.`,
      email,
      domain,
      local,
    };
  }

  const heuristics = [];
  if (SUSPICIOUS_TLDS.has(tld)) heuristics.push(`Suspicious TLD .${tld}`);
  if (RANDOM_LOCAL_RE.test(local)) heuristics.push("Local part looks randomly generated.");
  if (TEMP_LOCAL_RE.test(local)) heuristics.push(`Local part starts with a throwaway keyword.`);

  if (heuristics.length >= 2) {
    return {
      verdict: "suspicious",
      reason: heuristics.join(" "),
      email,
      domain,
      local,
      heuristics,
    };
  }

  return {
    verdict: "ok",
    reason: "Domain is not on any known disposable list and the address shape looks normal.",
    email,
    domain,
    local,
  };
}

export { DISPOSABLE_DOMAINS, FORWARDING_ALIAS_DOMAINS };
