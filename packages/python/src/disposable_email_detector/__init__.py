"""Detect disposable / temporary email addresses, and distinguish them from
legitimate forwarding aliases.

>>> from disposable_email_detector import check, is_disposable
>>> is_disposable("foo@mailinator.com")
True
>>> check("user@emailalias.io")
{'verdict': 'forwarding_alias', 'provider': 'EmailAlias.io', ...}
"""
from .detector import (
    check,
    is_disposable,
    is_forwarding_alias,
    forwarding_alias_provider,
    DISPOSABLE_DOMAINS,
    FORWARDING_ALIAS_DOMAINS,
)

__all__ = [
    "check",
    "is_disposable",
    "is_forwarding_alias",
    "forwarding_alias_provider",
    "DISPOSABLE_DOMAINS",
    "FORWARDING_ALIAS_DOMAINS",
]

__version__ = "0.1.0"
