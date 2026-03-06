#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD="${PWD}"
RUNTIME_ROOT="${CWD}/yinch-auto-mkt-output/x-kol/.runtime"
VENV_DIR="${RUNTIME_ROOT}/venv"
BOOTSTRAP_REPORT="${RUNTIME_ROOT}/dependency-bootstrap.json"

mkdir -p "${RUNTIME_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[x-kol] python3 is required" >&2
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
fi

PYTHON_BIN="${VENV_DIR}/bin/python"
PIP_BIN="${VENV_DIR}/bin/pip"

"${PIP_BIN}" install --quiet --upgrade pip
"${PIP_BIN}" install --quiet requests openpyxl playwright
"${PYTHON_BIN}" -m playwright install chromium >/dev/null 2>&1 || true

cat > "${BOOTSTRAP_REPORT}" <<EOF
{
  "runtime_root": "${RUNTIME_ROOT}",
  "venv": "${VENV_DIR}",
  "python": "$("${PYTHON_BIN}" --version 2>&1 | tr -d '\n')",
  "packages": ["requests", "openpyxl", "playwright"]
}
EOF

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/run_x_kol.py" \
  --dependency-bootstrap "${BOOTSTRAP_REPORT}" \
  "$@"
