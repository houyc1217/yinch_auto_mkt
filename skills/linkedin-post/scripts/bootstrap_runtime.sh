#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUTPUT_ROOT="${PWD}/yinch-auto-mkt-output/linkedin-post"
RUNTIME_ROOT="${OUTPUT_ROOT}/.runtime"
BOOTSTRAP_REPORT="${RUNTIME_ROOT}/dependency-bootstrap.json"

mkdir -p "${RUNTIME_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[linkedin-post] python3 is required" >&2
  exit 1
fi

eval "$("${ROOT_DIR}/scripts/ensure-browser-runtime.sh" --report "${BOOTSTRAP_REPORT}")"

exec "${YINCH_BROWSER_PYTHON_BIN}" "${ROOT_DIR}/skills/linkedin-post/scripts/run_linkedin_post.py" "$@"
