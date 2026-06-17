from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
# In a built wheel the data files are colocated under .../data/. In a source
# checkout (running from packages/python/src) they live three levels up at
# repo-root/data/. Try the installed location first, then fall back.
_CANDIDATES = [
    _HERE / "data",
    _HERE.parent.parent.parent.parent / "data",
]


def _load(name: str) -> dict:
    for candidate in _CANDIDATES:
        path = candidate / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Could not locate {name} in any of: {_CANDIDATES}")


_DISPOSABLE = _load("disposable-domains.json")
_FORWARDING = _load("forwarding-alias-domains.json")
_PERSONALLY_OBSERVED = _load("personally-observed-domains.json")

DISPOSABLE_DOMAINS: frozenset[str] = frozenset(
    {d.lower() for d in _DISPOSABLE["domains"]}
    | {e["domain"].lower() for e in _PERSONALLY_OBSERVED["entries"]}
)

FORWARDING_ALIAS_DOMAINS: dict[str, str] = {
    domain.lower(): provider
    for provider, domains in _FORWARDING["providers"].items()
    for domain in domains
}

_SUSPICIOUS_TLDS = frozenset({"tk", "ml", "ga", "cf", "gq"})
_RANDOM_LOCAL_RE = re.compile(
    r"^[a-z]{1,3}[0-9]{4,}$|^[bcdfghjklmnpqrstvwxyz]{8,}$", re.I
)
_TEMP_LOCAL_RE = re.compile(
    r"^(temp|throw|trash|spam|junk|burner|test|fake|noreply|donotreply)[a-z0-9._-]*",
    re.I,
)


def _normalize(email: str) -> Optional[tuple[str, str]]:
    if not isinstance(email, str):
        return None
    trimmed = email.strip().lower()
    if not trimmed or "@" not in trimmed:
        return None
    local, _, domain = trimmed.rpartition("@")
    if not local or not domain:
        return None
    return local, domain


def is_disposable(email: str) -> bool:
    parts = _normalize(email)
    if not parts:
        return False
    _, domain = parts
    return domain in DISPOSABLE_DOMAINS


def is_forwarding_alias(email: str) -> bool:
    parts = _normalize(email)
    if not parts:
        return False
    _, domain = parts
    return domain in FORWARDING_ALIAS_DOMAINS


def forwarding_alias_provider(email: str) -> Optional[str]:
    parts = _normalize(email)
    if not parts:
        return None
    _, domain = parts
    return FORWARDING_ALIAS_DOMAINS.get(domain)


def check(email: str) -> dict:
    parts = _normalize(email)
    if not parts:
        return {
            "verdict": "invalid",
            "reason": "Email is empty or has no domain.",
            "email": email if isinstance(email, str) else None,
            "domain": None,
        }
    local, domain = parts
    tld = domain.rsplit(".", 1)[-1]

    if domain in FORWARDING_ALIAS_DOMAINS:
        return {
            "verdict": "forwarding_alias",
            "provider": FORWARDING_ALIAS_DOMAINS[domain],
            "reason": (
                "Address is a forwarding alias from a known provider — mail "
                "forwards to a real, permanent inbox the user controls. Do "
                "NOT treat as disposable."
            ),
            "email": email,
            "domain": domain,
            "local": local,
        }

    if domain in DISPOSABLE_DOMAINS:
        return {
            "verdict": "disposable",
            "reason": f"Domain {domain} is on the curated disposable list.",
            "email": email,
            "domain": domain,
            "local": local,
        }

    heuristics: list[str] = []
    if tld in _SUSPICIOUS_TLDS:
        heuristics.append(f"Suspicious TLD .{tld}")
    if _RANDOM_LOCAL_RE.search(local):
        heuristics.append("Local part looks randomly generated.")
    if _TEMP_LOCAL_RE.search(local):
        heuristics.append("Local part starts with a throwaway keyword.")

    if len(heuristics) >= 2:
        return {
            "verdict": "suspicious",
            "reason": " ".join(heuristics),
            "email": email,
            "domain": domain,
            "local": local,
            "heuristics": heuristics,
        }

    return {
        "verdict": "ok",
        "reason": (
            "Domain is not on any known disposable list and the address "
            "shape looks normal."
        ),
        "email": email,
        "domain": domain,
        "local": local,
    }
