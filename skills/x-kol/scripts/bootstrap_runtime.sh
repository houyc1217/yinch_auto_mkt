#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CWD="${PWD}"
RUNTIME_ROOT="${CWD}/yinch-auto-mkt-output/x-kol/.runtime"
BOOTSTRAP_REPORT="${RUNTIME_ROOT}/dependency-bootstrap.json"

mkdir -p "${RUNTIME_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[x-kol] python3 is required" >&2
  exit 1
fi

eval "$("${ROOT_DIR}/scripts/ensure-browser-runtime.sh" --report "${BOOTSTRAP_REPORT}")"

exec "${YINCH_BROWSER_PYTHON_BIN}" "${SCRIPT_DIR}/run_x_kol.py" \
  --dependency-bootstrap "${BOOTSTRAP_REPORT}" \
  "$@"
