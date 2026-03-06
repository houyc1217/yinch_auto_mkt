#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUTPUT_ROOT="${PWD}/yinch-auto-mkt-output/google-review"
RUNTIME_ROOT="${OUTPUT_ROOT}/.runtime"
VENV_DIR="${RUNTIME_ROOT}/venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "${RUNTIME_ROOT}"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip >/dev/null
python -m pip install requests playwright >/dev/null
python -m playwright install chromium >/dev/null

python - <<'PY' "${RUNTIME_ROOT}"
import json
import platform
import sys
from pathlib import Path

runtime_root = Path(sys.argv[1])
report = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "dependencies": ["requests", "playwright"],
}
(runtime_root / "dependency-bootstrap.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
PY

exec python "${ROOT_DIR}/skills/google-review/scripts/run_google_review.py" "$@"
