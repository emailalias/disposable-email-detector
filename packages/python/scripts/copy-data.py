#!/usr/bin/env python3
"""Copies the shared data/ files from the repo root into the Python
package source tree so they're included in the wheel + sdist.

PEP 517 builds run in an isolated /tmp/ directory which can't see
relative paths like ../../data/. Copying the JSON files into the
package source dir solves it for both `pip install -e .` and `python
-m build`.

Path resolution in detector.py prefers the installed-package location
and falls back to the source-checkout location, so running tests
against the source tree without this copy still works.

Wired to the publish workflow as a pre-build step; also runs from a
plain `python -m build` if you copy first.
"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT_DATA = HERE.parent.parent.parent / "data"
DEST = HERE.parent / "src" / "disposable_email_detector" / "data"

if DEST.exists():
    shutil.rmtree(DEST)
DEST.mkdir(parents=True)

for name in [
    "disposable-domains.json",
    "forwarding-alias-domains.json",
    "personally-observed-domains.json",
]:
    src = REPO_ROOT_DATA / name
    shutil.copy2(src, DEST / name)
    print(f"copied {name}")
