#!/usr/bin/env bash
set -euo pipefail

AGENT_MODE="both"
REPO_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      AGENT_MODE="${2:-both}"
      shift
      ;;
    --repo-dir)
      REPO_DIR="${2:-}"
      shift
      ;;
  esac
  shift
done

if [[ -z "${REPO_DIR}" ]]; then
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
MANIFEST_DIR="${YINCH_AUTO_MKT_HOME:-$HOME/.yinch-auto-mkt}"

link_or_copy() {
  local src="$1"
  local dest="$2"
  mkdir -p "$(dirname "${dest}")"
  if [[ -L "${dest}" || -f "${dest}" ]]; then
    rm -f "${dest}"
  elif [[ -d "${dest}" ]]; then
    python3 - <<'PY' "${dest}"
import shutil
import sys
from pathlib import Path

target = Path(sys.argv[1])
if target.exists():
    shutil.rmtree(target)
PY
  fi
  if ln -s "${src}" "${dest}" 2>/dev/null; then
    return 0
  fi
  cp -R "${src}" "${dest}"
}

install_codex() {
  mkdir -p "${CODEX_DIR}/skills"
  for skill_dir in "${REPO_DIR}"/skills/*; do
    [[ -d "${skill_dir}" ]] || continue
    link_or_copy "${skill_dir}" "${CODEX_DIR}/skills/$(basename "${skill_dir}")"
  done
}

install_claude() {
  mkdir -p "${CLAUDE_DIR}/skills" "${CLAUDE_DIR}/agents"
  for skill_dir in "${REPO_DIR}"/skills/*; do
    [[ -d "${skill_dir}" ]] || continue
    link_or_copy "${skill_dir}" "${CLAUDE_DIR}/skills/$(basename "${skill_dir}")"
  done
  for agent_file in "${REPO_DIR}"/.claude/agents/*.md; do
    [[ -f "${agent_file}" ]] || continue
    link_or_copy "${agent_file}" "${CLAUDE_DIR}/agents/$(basename "${agent_file}")"
  done
}

write_manifest() {
  mkdir -p "${MANIFEST_DIR}"
  cat > "${MANIFEST_DIR}/install-manifest.json" <<EOF
{
  "repo_dir": "${REPO_DIR}",
  "claude_dir": "${CLAUDE_DIR}",
  "codex_dir": "${CODEX_DIR}",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "agent_mode": "${AGENT_MODE}"
}
EOF
}

main() {
  case "${AGENT_MODE}" in
    claude)
      install_claude
      ;;
    codex)
      install_codex
      ;;
    both|auto)
      install_codex
      install_claude
      ;;
    *)
      echo "Unsupported --agent value: ${AGENT_MODE}" >&2
      exit 1
      ;;
  esac
  write_manifest
}

main "$@"
