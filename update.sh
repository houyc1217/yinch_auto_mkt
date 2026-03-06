#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${YINCH_AUTO_MKT_HOME:-$HOME/.yinch-auto-mkt}"
REPO_DIR="${INSTALL_ROOT}/repo"

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  echo "No existing installation found at ${REPO_DIR}. Run install.sh first." >&2
  exit 1
fi

"${REPO_DIR}/install.sh" "$@"
