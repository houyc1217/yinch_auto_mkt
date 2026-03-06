#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${YINCH_AUTO_MKT_REPO_URL:-https://github.com/houyc1217/yinch_mkt_plugins.git}"
INSTALL_ROOT="${YINCH_AUTO_MKT_HOME:-$HOME/.yinch-auto-mkt}"
REPO_DIR="${INSTALL_ROOT}/repo"
SAFE_MODE=0
AGENT_MODE="both"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --safe)
      SAFE_MODE=1
      ;;
    --agent)
      AGENT_MODE="${2:-both}"
      shift
      ;;
    *)
      ;;
  esac
  shift
done

log() { printf '[yinch-auto-mkt] %s\n' "$1"; }
warn() { printf '[yinch-auto-mkt][warn] %s\n' "$1" >&2; }

ensure_repo() {
  mkdir -p "${INSTALL_ROOT}"
  if [[ -d "${REPO_DIR}/.git" ]]; then
    log "Updating existing checkout at ${REPO_DIR}"
    git -C "${REPO_DIR}" fetch --depth=1 origin main
    git -C "${REPO_DIR}" reset --hard origin/main
  else
    log "Cloning repository into ${REPO_DIR}"
    rm -rf "${REPO_DIR}"
    git clone --depth=1 "${REPO_URL}" "${REPO_DIR}"
  fi
}

main() {
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required" >&2
    exit 1
  fi

  ensure_repo

  log "Installing dependencies"
  "${REPO_DIR}/scripts/install-deps.sh" $( [[ ${SAFE_MODE} -eq 1 ]] && printf '%s' "--safe" )

  log "Installing Codex and Claude Code integrations"
  "${REPO_DIR}/scripts/install-agent-assets.sh" --agent "${AGENT_MODE}" --repo-dir "${REPO_DIR}"

  log "Running health check"
  "${REPO_DIR}/scripts/check-env.sh" --repo-dir "${REPO_DIR}"

  cat <<EOF

Installed Yinch Auto MKT.

Repo checkout:
  ${REPO_DIR}

Next use:
  - Claude Code: natural language with installed skills
  - Codex: natural language with the installed skills
EOF
}

main "$@"
