#!/usr/bin/env python3
"""Refresh data/disposable-domains.json from upstream community lists.

Pulls two well-maintained public MIT-licensed lists, merges, lowercases,
deduplicates, sorts, and writes the union to data/disposable-domains.json.

The GitHub Action at .github/workflows/refresh-domains.yml runs this
weekly and opens a PR with the diff.

Sources:
  - github.com/disposable/disposable-email-domains      (~60k+ domains)
  - github.com/disposable-email-domains/disposable-email-domains (~5k curated)

Run manually from repo root:
    python3 scripts/refresh-disposable-list.py
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "data" / "disposable-domains.json"

SOURCES = [
    "https://raw.githubusercontent.com/disposable/disposable-email-domains/master/domains.txt",
    "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/main/disposable_email_blocklist.conf",
]


def fetch(url: str) -> list[str]:
    print(f"Fetching {url} …", flush=True)
    req = urllib.request.Request(
        url, headers={"User-Agent": "disposable-email-detector-refresh/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore").splitlines()


def main() -> int:
    domains: set[str] = set()
    for url in SOURCES:
        try:
            for line in fetch(url):
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                # Reject obvious junk: must contain a dot, no whitespace,
                # max 253 chars (RFC 1035).
                if "." not in line or " " in line or len(line) > 253:
                    continue
                domains.add(line)
        except Exception as exc:
            print(f"  failed: {exc}", file=sys.stderr)
            return 1

    # Subtract the legitimate forwarding-alias providers from the
    # disposable list. Several public lists conflate them with throwaway
    # mailboxes (addy.io is on at least one), but they're permanent
    # forwarding addresses to real inboxes — wrong category.
    forwarding_path = REPO_ROOT / "data" / "forwarding-alias-domains.json"
    forwarding_data = json.loads(forwarding_path.read_text(encoding="utf-8"))
    forwarding_set: set[str] = set()
    for provider_domains in forwarding_data["providers"].values():
        for d in provider_domains:
            forwarding_set.add(d.lower())
    removed = sorted(domains & forwarding_set)
    domains -= forwarding_set

    existing = (
        json.loads(OUTPUT.read_text(encoding="utf-8"))
        if OUTPUT.exists()
        else {"_meta": {}, "domains": []}
    )

    new_list = sorted(domains)
    existing.setdefault(
        "_meta",
        {
            "description": (
                "Disposable / temporary email domains synced from upstream "
                "MIT-licensed community lists. Refreshed by "
                "scripts/refresh-disposable-list.py."
            ),
            "license": "MIT — same as the parent repo",
        },
    )
    existing["_meta"]["sources"] = SOURCES
    existing["_meta"]["count"] = len(new_list)
    existing["_meta"]["version"] = "0.2.0"
    existing["domains"] = new_list

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(new_list):,} unique domains to {OUTPUT.relative_to(REPO_ROOT)}")
    if removed:
        print(
            f"Excluded {len(removed)} forwarding-alias domain(s) that appeared "
            f"on upstream lists: {', '.join(removed)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
