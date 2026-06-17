# disposable-email-detector

Detect disposable / temporary email addresses, and tell them apart from legitimate forwarding aliases like EmailAlias.io, SimpleLogin, addy.io, DuckDuckGo Email Protection, Firefox Relay, and Sign in with Apple's Hide My Email.

Most disposable-email blocklists treat every "unusual" email domain the same. This one separates two distinct categories:

| Category | Example | Action |
|---|---|---|
| **Disposable** — mailbox expires, abandoned by design | `foo@mailinator.com`, `bar@10minutemail.com` | Block at signup |
| **Forwarding alias** — permanent address, forwards to a real inbox the user controls | `user@emailalias.io`, `u@sl.email`, `foo@duck.com` | **Do NOT block** — this is a real customer using privacy tooling |
| **OK** — unknown / probably legit mailbox | `jane@gmail.com` | Allow |

Try the hosted checker at [emailalias.io/tools/disposable-email-checker](https://emailalias.io/tools/disposable-email-checker).

## Install

```bash
pip install disposable-email-detector
```

Python 3.9+. No runtime dependencies.

## Usage

```python
from disposable_email_detector import check, is_disposable, is_forwarding_alias

is_disposable("foo@mailinator.com")        # True
is_disposable("user@emailalias.io")        # False — it's a forwarding alias

is_forwarding_alias("user@emailalias.io")  # True

check("user@emailalias.io")
# {
#   "verdict": "forwarding_alias",
#   "provider": "EmailAlias.io",
#   "reason": "Address is a forwarding alias … Do NOT treat as disposable.",
#   "email": "user@emailalias.io",
#   "domain": "emailalias.io",
#   "local": "user"
# }
```

`check()` returns one of: `"disposable" | "forwarding_alias" | "suspicious" | "ok" | "invalid"`.

## What gets detected

1. **Disposable domain list** (~74,000 providers — Mailinator, 10MinuteMail, GuerrillaMail, YOPmail, Temp-Mail, and the long tail of obscure throwaway services). Synced weekly from upstream MIT-licensed community lists.
2. **Personally-observed list** — domains seen directly in EmailAlias.io abuse logs, with provenance notes (Cloudflare Email Routing MX, NameSilo mail-only, etc.). Survives every upstream refresh.
3. **Forwarding-alias provider list** — used to flip the verdict from `disposable` to `forwarding_alias` and tell the integrator who NOT to block.
4. **Heuristics** on the local part and TLD:
   - Suspicious TLDs: `.tk`, `.ml`, `.ga`, `.cf`, `.gq`
   - Local part looks randomly generated
   - Local part starts with a throwaway keyword (`temp`, `throw`, `trash`, `spam`, `junk`, …)

Two or more heuristic hits flips the verdict to `suspicious`. One hit alone is left at `ok` — single signals are too noisy on real addresses.

## Why split disposable from forwarding alias?

Mail to a Mailinator address lands in a public inbox that anyone can read. Mail to a DuckDuckGo or EmailAlias.io address forwards to the user's real inbox. Site owners blocking both end up rejecting privacy-conscious customers — exactly the audience least likely to come back. Splitting the verdict lets you block `disposable` and allow `forwarding_alias` with one library.

## License

MIT. Source and bug reports: [github.com/emailalias/disposable-email-detector](https://github.com/emailalias/disposable-email-detector). The JavaScript/TypeScript sibling package is at [`@emailalias/disposable-email-detector`](https://www.npmjs.com/package/@emailalias/disposable-email-detector) on npm.
