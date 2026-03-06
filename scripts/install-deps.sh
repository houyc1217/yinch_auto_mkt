#!/usr/bin/env bash
set -euo pipefail

SAFE_MODE=0
OS="$(uname -s)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --safe)
      SAFE_MODE=1
      ;;
  esac
  shift
done

log() { printf '[yinch-auto-mkt][deps] %s\n' "$1"; }
warn() { printf '[yinch-auto-mkt][deps][warn] %s\n' "$1" >&2; }

maybe_install_with_brew() {
  local package="$1"
  if command -v brew >/dev/null 2>&1; then
    brew install "${package}"
    return 0
  fi
  return 1
}

maybe_install_with_apt() {
  shift 0
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y "$@"
    return 0
  fi
  return 1
}

ensure_python() {
  if command -v python3 >/dev/null 2>&1; then
    log "python3 detected: $(python3 --version 2>&1)"
  elif [[ ${SAFE_MODE} -eq 0 ]]; then
    log "python3 missing, attempting install"
    if [[ "${OS}" == "Darwin" ]]; then
      maybe_install_with_brew python || warn "Install Python manually if needed."
    else
      maybe_install_with_apt python3 python3-venv python3-pip || warn "Install Python manually if needed."
    fi
  else
    warn "python3 missing"
  fi

  if command -v python3 >/dev/null 2>&1 && ! python3 -m venv --help >/dev/null 2>&1 && [[ ${SAFE_MODE} -eq 0 ]]; then
    log "python3-venv missing, attempting install"
    maybe_install_with_apt python3-venv || warn "Install python3-venv manually if needed."
  fi
}

ensure_git() {
  if command -v git >/dev/null 2>&1; then
    log "git detected: $(git --version 2>&1)"
  elif [[ ${SAFE_MODE} -eq 0 ]]; then
    log "git missing, attempting install"
    if [[ "${OS}" == "Darwin" ]]; then
      maybe_install_with_brew git || warn "Install git manually if needed."
    else
      maybe_install_with_apt git || warn "Install git manually if needed."
    fi
  else
    warn "git missing"
  fi
}

main() {
  ensure_git
  ensure_python
  log "Dependency bootstrap complete"
}

main "$@"
