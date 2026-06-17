import { test } from "node:test";
import assert from "node:assert/strict";
import { check, isDisposable, isForwardingAlias, forwardingAliasProvider } from "../src/index.js";

test("disposable domain → disposable verdict", () => {
  const r = check("foo@mailinator.com");
  assert.equal(r.verdict, "disposable");
  assert.equal(r.domain, "mailinator.com");
});

test("forwarding alias is not flagged as disposable", () => {
  assert.equal(isDisposable("user@emailalias.io"), false);
  assert.equal(isForwardingAlias("user@emailalias.io"), true);
  assert.equal(forwardingAliasProvider("user@emailalias.io"), "EmailAlias.io");
});

test("SimpleLogin alias is recognised", () => {
  const r = check("u@sl.email");
  assert.equal(r.verdict, "forwarding_alias");
  assert.equal(r.provider, "SimpleLogin (Proton)");
});

test("DuckDuckGo alias is recognised", () => {
  const r = check("foo@duck.com");
  assert.equal(r.verdict, "forwarding_alias");
});

test("normal address → ok verdict", () => {
  const r = check("jane.doe@gmail.com");
  assert.equal(r.verdict, "ok");
});

test("suspicious TLD + random local → suspicious", () => {
  const r = check("xkj0298473@spammyhost.tk");
  assert.equal(r.verdict, "suspicious");
});

test("empty / malformed → invalid", () => {
  assert.equal(check("").verdict, "invalid");
  assert.equal(check("no-at-sign").verdict, "invalid");
  assert.equal(check("@nolocal.com").verdict, "invalid");
});

test("case-insensitive on domain", () => {
  assert.equal(isDisposable("Foo@Mailinator.COM"), true);
});
