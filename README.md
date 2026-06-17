# disposable-email-detector

Detect disposable / temporary email addresses — and tell them apart from legitimate forwarding aliases like EmailAlias.io, SimpleLogin, addy.io, DuckDuckGo Email Protection, Firefox Relay, and Sign in with Apple's Hide My Email.

Most disposable-email blocklists treat every "unusual" email domain the same. This one separates two distinct categories:

| Category | Example | Action |
|---|---|---|
| **Disposable** — mailbox expires, abandoned by design | `foo@mailinator.com`, `bar@10minutemail.com` | Block at signup |
| **Forwarding alias** — permanent address, forwards to a real inbox the user controls | `user@emailalias.io`, `u@sl.email`, `foo@duck.com` | **Do NOT block** — this is a real customer using privacy tooling |
| **OK** — unknown / probably legit mailbox | `jane@gmail.com` | Allow |

Try the hosted checker at [emailalias.io/disposable-email-checker](https://emailalias.io/disposable-email-checker), or wire one of the language packages below into your signup form.

## JavaScript / TypeScript

```bash
npm install @emailalias/disposable-email-detector
```

```javascript
import { check, isDisposable, isForwardingAlias } from "@emailalias/disposable-email-detector";

isDisposable("foo@mailinator.com");        // true
isDisposable("user@emailalias.io");        // false — it's a forwarding alias

isForwardingAlias("user@emailalias.io");   // true

const result = check("user@emailalias.io");
// {
//   verdict: "forwarding_alias",
//   provider: "EmailAlias.io",
//   reason: "Address is a forwarding alias … Do NOT treat as disposable.",
//   email: "user@emailalias.io",
//   domain: "emailalias.io",
//   local: "user"
// }
```

`check()` returns one of: `"disposable" | "forwarding_alias" | "suspicious" | "ok" | "invalid"`.

## Python

```bash
pip install disposable-email-detector
```

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
#   ...
# }
```

## What gets detected

The detector combines three signals:

1. **Curated disposable domain list** (~400 well-known providers — Mailinator, 10MinuteMail, GuerrillaMail, YOPmail, Temp-Mail, and the long tail of common test-account services). Lives in `data/disposable-domains.json`.
2. **Forwarding-alias provider list** — separate file (`data/forwarding-alias-domains.json`) mapping each known provider's domains back to a human-readable provider name. Used to flip the verdict from `disposable` to `forwarding_alias` and tell the integrator who to NOT block.
3. **Heuristics** on the local part and TLD:
   - Suspicious TLDs: `.tk`, `.ml`, `.ga`, `.cf`, `.gq`
   - Local part looks randomly generated (e.g. `xkj0298473`, or runs of 8+ consonants)
   - Local part starts with a throwaway keyword (`temp`, `throw`, `trash`, `spam`, `junk`, `burner`, `test`, `fake`)

Two or more heuristic hits flips the verdict to `suspicious`. One hit alone is left at `ok` — single signals are too noisy on real addresses.

## Why split disposable from forwarding alias?

Plenty of public disposable lists put `duck.com`, `mozmail.com`, `addy.io`, etc. on the same list as `mailinator.com`. That's wrong:

- Mail to a Mailinator address lands in a public inbox that anyone can read. The user never sees it again.
- Mail to a DuckDuckGo or EmailAlias.io address forwards to the user's real, permanent inbox. The user reads it like any other email and replies through the alias.

Site owners who block both end up rejecting privacy-conscious customers in the second category — which is exactly the audience least likely to come back and try again with a "real" address. Splitting the verdict lets you block `disposable` and allow `forwarding_alias` with a single library.

## Updating the domain list

Contributions welcome. To add a domain:

1. Open a PR adding the domain (lowercased, no leading `@`) to either `data/disposable-domains.json` or `data/forwarding-alias-domains.json`.
2. Include the source — a screenshot of the provider's homepage, a link to where you saw it referenced, or a sample address.
3. Run tests:
   ```bash
   # JS
   cd packages/js && node --test test/
   # Python
   cd packages/python && PYTHONPATH=src python3 -m pytest tests/
   ```

For the disposable list specifically, we periodically merge from larger upstream lists (Castle, IntegerAlex/disposable-email-detector, Fidro). Pull requests batching multiple upstream merges in one go are appreciated.

## License

MIT. See `LICENSE`.

## Who maintains it

[EmailAlias.io](https://emailalias.io) — a permanent email-forwarding alias service with built-in exposure detection. The detector is open source because we think site owners blocking signups should have a tool that doesn't accidentally block legitimate alias users (including, but not limited to, our own).
