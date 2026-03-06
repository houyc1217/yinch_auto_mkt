#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUTPUT_ROOT="${PWD}/yinch-auto-mkt-output/channel-setup"
RUNTIME_ROOT="${OUTPUT_ROOT}/.runtime"
VENV_DIR="${RUNTIME_ROOT}/venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "${RUNTIME_ROOT}"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip >/dev/null

exec python "${ROOT_DIR}/skills/channel-setup/scripts/run_channel_setup.py" "$@"
