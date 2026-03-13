# Environment setup

This repository is a legacy Python 2 automation project. The source files use
Python 2 syntax (`print` statements, `urllib2`, `StringIO`) and will not run on
the default Python 3 toolchain that ships with most modern cloud agents.

## What the repo-local Cursor environment does

- builds a Debian Bullseye image with the native libraries needed by lxml,
  Pillow, and the browser automation scripts;
- installs Firefox ESR and Xvfb for Selenium-driven flows;
- bootstraps `pyenv` and uses it to install Python 2.7.18;
- creates a repo-local virtualenv in `.venv`;
- installs the pinned Python dependencies from `requirements.txt`.

The entry point for Cursor cloud agents is `.cursor/environment.json`, which
runs `scripts/bootstrap-agent-env.sh` during environment setup.

## Manual bootstrap

If you need to reproduce the setup in a shell:

```bash
bash ./scripts/bootstrap-agent-env.sh
source .venv/bin/activate
python -V
```

Expected Python version:

```text
Python 2.7.18
```

## Notes

- `formasaurus` is included in `requirements.txt` because it is imported by
  `registration_form_filler.py` but was previously undeclared.
- The Selenium dependency is very old (`2.48.0`). Firefox is provided so the
  browser scripts have the expected runtime pieces, but the demo spiders may
  still need code modernization before they work reliably against modern sites
  and drivers.
