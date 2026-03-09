#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${YINCH_AUTO_MKT_HOME:-$HOME/.yinch-auto-mkt}"
RUNTIME_ROOT="${INSTALL_ROOT}/runtime/browser"
VENV_DIR="${RUNTIME_ROOT}/venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
READY_REPORT="${RUNTIME_ROOT}/dependency-bootstrap.json"
REPORT_PATH=""
OUTPUT_MODE="shell"
REFRESH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report)
      REPORT_PATH="${2:-}"
      shift
      ;;
    --output)
      OUTPUT_MODE="${2:-shell}"
      shift
      ;;
    --refresh)
      REFRESH=1
      ;;
  esac
  shift
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "[yinch-auto-mkt][runtime] python3 is required" >&2
  exit 1
fi

mkdir -p "${RUNTIME_ROOT}"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
elif [[ ! -x "${PYTHON_BIN}" ]]; then
  python3 -m venv --clear "${VENV_DIR}"
fi

if ! "${PYTHON_BIN}" -m pip --version >/dev/null 2>&1; then
  python3 -m venv --clear "${VENV_DIR}"
fi

needs_bootstrap() {
  if [[ ${REFRESH} -eq 1 || ! -f "${READY_REPORT}" ]]; then
    return 0
  fi
  if ! "${PYTHON_BIN}" -c "import openpyxl, playwright, requests" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

if needs_bootstrap; then
  "${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
  "${PYTHON_BIN}" -m pip install requests openpyxl playwright >/dev/null
  "${PYTHON_BIN}" -m playwright install chromium >/dev/null

  "${PYTHON_BIN}" - <<'PY' "${READY_REPORT}" "${RUNTIME_ROOT}" "${VENV_DIR}"
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
runtime_root = Path(sys.argv[2])
venv_dir = Path(sys.argv[3])
report = {
    "runtime_root": str(runtime_root),
    "venv": str(venv_dir),
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "dependencies": ["requests", "openpyxl", "playwright"],
    "browser": "chromium",
    "bootstrapped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
PY
fi

if [[ -n "${REPORT_PATH}" ]]; then
  mkdir -p "$(dirname "${REPORT_PATH}")"
  cp "${READY_REPORT}" "${REPORT_PATH}"
fi

case "${OUTPUT_MODE}" in
  shell)
    cat <<EOF
export YINCH_BROWSER_RUNTIME_ROOT="${RUNTIME_ROOT}"
export YINCH_BROWSER_VENV="${VENV_DIR}"
export YINCH_BROWSER_PYTHON_BIN="${PYTHON_BIN}"
export YINCH_BROWSER_REPORT="${REPORT_PATH:-${READY_REPORT}}"
EOF
    ;;
  json)
    cat "${REPORT_PATH:-${READY_REPORT}}"
    ;;
  *)
    echo "Unsupported --output value: ${OUTPUT_MODE}" >&2
    exit 1
    ;;
esac
