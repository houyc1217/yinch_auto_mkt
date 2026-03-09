#!/usr/bin/env bash
set -euo pipefail

REPO_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
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
BROWSER_RUNTIME_DIR="${YINCH_AUTO_MKT_HOME:-$HOME/.yinch-auto-mkt}/runtime/browser"
FAILURES=0
WARNINGS=0

check_path() {
  local label="$1"
  local path="$2"
  if [[ -e "${path}" ]]; then
    printf '[ok] %s: %s\n' "${label}" "${path}"
  else
    printf '[missing] %s: %s\n' "${label}" "${path}" >&2
    FAILURES=$((FAILURES + 1))
  fi
}

check_cmd() {
  local name="$1"
  if command -v "${name}" >/dev/null 2>&1; then
    printf '[ok] command: %s\n' "${name}"
  else
    printf '[missing] command: %s\n' "${name}" >&2
    FAILURES=$((FAILURES + 1))
  fi
}

warn_optional() {
  local label="$1"
  local detail="$2"
  printf '[warn] %s: %s\n' "${label}" "${detail}" >&2
  WARNINGS=$((WARNINGS + 1))
}

check_optional_path() {
  local label="$1"
  local path="$2"
  if [[ -e "${path}" ]]; then
    printf '[ok] %s: %s\n' "${label}" "${path}"
  else
    warn_optional "${label}" "${path}"
  fi
}

main() {
  check_cmd git
  check_cmd python3

  check_path "repo" "${REPO_DIR}"
  for skill_dir in "${REPO_DIR}"/skills/*; do
    [[ -d "${skill_dir}" ]] || continue
    skill_name="$(basename "${skill_dir}")"
    check_path "codex ${skill_name} skill" "${CODEX_DIR}/skills/${skill_name}/SKILL.md"
    check_path "claude ${skill_name} skill" "${CLAUDE_DIR}/skills/${skill_name}/SKILL.md"
  done
  for agent_file in "${REPO_DIR}"/.claude/agents/*.md; do
    [[ -f "${agent_file}" ]] || continue
    agent_name="$(basename "${agent_file}")"
    check_path "claude agent ${agent_name}" "${CLAUDE_DIR}/agents/${agent_name}"
  done

  check_optional_path "shared browser runtime" "${BROWSER_RUNTIME_DIR}/venv/bin/python"
  if [[ -x "${BROWSER_RUNTIME_DIR}/venv/bin/python" ]]; then
    if "${BROWSER_RUNTIME_DIR}/venv/bin/python" -c "import openpyxl, playwright, requests" >/dev/null 2>&1; then
      printf '[ok] shared browser runtime imports: requests, openpyxl, playwright\n'
    else
      warn_optional "shared browser runtime imports" "requests, openpyxl, or playwright unavailable"
    fi
  fi
  check_optional_path "codex optional playwright skill" "${CODEX_DIR}/skills/playwright"
  check_optional_path "codex optional playwright-interactive skill" "${CODEX_DIR}/skills/playwright-interactive"

  if [[ ${FAILURES} -gt 0 ]]; then
    printf '\nEnvironment check failed with %s missing item(s).\n' "${FAILURES}" >&2
    exit 1
  fi
  if [[ ${WARNINGS} -gt 0 ]]; then
    printf '\nEnvironment check passed with %s optional warning(s).\n' "${WARNINGS}"
  else
    printf '\nEnvironment check passed.\n'
  fi
}

main "$@"
