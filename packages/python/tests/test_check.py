import pytest
from disposable_email_detector import (
    check, is_disposable, is_forwarding_alias, forwarding_alias_provider,
)


def test_disposable_domain_disposable_verdict():
    r = check("foo@mailinator.com")
    assert r["verdict"] == "disposable"
    assert r["domain"] == "mailinator.com"


def test_forwarding_alias_not_disposable():
    assert is_disposable("user@emailalias.io") is False
    assert is_forwarding_alias("user@emailalias.io") is True
    assert forwarding_alias_provider("user@emailalias.io") == "EmailAlias.io"


def test_simplelogin_alias_recognised():
    r = check("u@sl.email")
    assert r["verdict"] == "forwarding_alias"
    assert r["provider"] == "SimpleLogin (Proton)"


def test_duckduckgo_alias_recognised():
    r = check("foo@duck.com")
    assert r["verdict"] == "forwarding_alias"


def test_normal_address_ok():
    r = check("jane.doe@gmail.com")
    assert r["verdict"] == "ok"


def test_suspicious_tld_plus_random_local():
    r = check("xkj0298473@spammyhost.tk")
    assert r["verdict"] == "suspicious"


@pytest.mark.parametrize("bad", ["", "no-at-sign", "@nolocal.com"])
def test_invalid_inputs(bad):
    assert check(bad)["verdict"] == "invalid"


def test_case_insensitive_domain():
    assert is_disposable("Foo@Mailinator.COM") is True
