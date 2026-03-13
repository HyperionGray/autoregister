#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
PYTHON_VERSION="2.7.18"
VENV_DIR="$REPO_ROOT/.venv"

export PYENV_ROOT
export PATH="$PYENV_ROOT/bin:$PATH"

if [ ! -d "$PYENV_ROOT" ]; then
  git clone --depth 1 https://github.com/pyenv/pyenv.git "$PYENV_ROOT"
fi

PYENV_BIN="$PYENV_ROOT/bin/pyenv"
if ! "$PYENV_BIN" install -s "$PYTHON_VERSION"; then
  printf '%s\n' \
    "Python $PYTHON_VERSION failed to build." \
    "This bootstrap expects the system packages from .cursor/Dockerfile, or an" \
    "equivalent host setup that provides OpenSSL, SQLite, bzip2, readline, and" \
    "other Python 2 build headers." \
    "For Cursor cloud agents, run the repo through .cursor/environment.json so" \
    "the image is built before install runs." >&2
  exit 1
fi

PYTHON_BIN="$("$PYENV_BIN" prefix "$PYTHON_VERSION")/bin/python2.7"
"$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true

"$PYTHON_BIN" -m pip install --upgrade \
  "pip<21" \
  "setuptools<45" \
  "virtualenv<20.22" \
  "wheel<1"

recreate_venv=0
if [ ! -x "$VENV_DIR/bin/python" ]; then
  recreate_venv=1
else
  version_output="$("$VENV_DIR/bin/python" -V 2>&1 || true)"
  case "$version_output" in
    "Python 2.7."*)
      ;;
    *)
      recreate_venv=1
      ;;
  esac
fi

if [ "$recreate_venv" -eq 1 ]; then
  rm -rf "$VENV_DIR"
  "$PYTHON_BIN" -m virtualenv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade \
  "pip<21" \
  "setuptools<45" \
  "wheel<1"
"$VENV_DIR/bin/pip" install -r "$REPO_ROOT/requirements.txt"

PROFILE_FILE="$HOME/.autoregister-agent-env"
cat > "$PROFILE_FILE" <<EOF
export PYENV_ROOT="$PYENV_ROOT"
export PATH="$VENV_DIR/bin:\$PYENV_ROOT/bin:\$PYENV_ROOT/shims:\$PATH"
if command -v pyenv >/dev/null 2>&1; then
  eval "\$(pyenv init - 2>/dev/null || true)"
fi
EOF

if [ -f "$HOME/.bashrc" ]; then
  bashrc_contents="$(<"$HOME/.bashrc")"
  case "$bashrc_contents" in
    *autoregister-agent-env*)
      ;;
    *)
      printf '\n[ -f "%s" ] && . "%s"\n' "$PROFILE_FILE" "$PROFILE_FILE" >> "$HOME/.bashrc"
      ;;
  esac
fi
