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
MANIFEST_PATH="${MANIFEST_DIR}/install-manifest.json"
REPO_SKILLS=()
REPO_AGENTS=()

remove_path() {
  local target="$1"
  if [[ -L "${target}" || -f "${target}" ]]; then
    rm -f "${target}"
  elif [[ -d "${target}" ]]; then
    python3 - <<'PY' "${target}"
import shutil
import sys
from pathlib import Path

target = Path(sys.argv[1])
if target.exists():
    shutil.rmtree(target)
PY
  fi
}

link_or_copy() {
  local src="$1"
  local dest="$2"
  mkdir -p "$(dirname "${dest}")"
  remove_path "${dest}"
  if ln -s "${src}" "${dest}" 2>/dev/null; then
    return 0
  fi
  cp -R "${src}" "${dest}"
}

collect_repo_assets() {
  REPO_SKILLS=()
  REPO_AGENTS=()
  for skill_dir in "${REPO_DIR}"/skills/*; do
    [[ -d "${skill_dir}" ]] || continue
    REPO_SKILLS+=("$(basename "${skill_dir}")")
  done
  for agent_file in "${REPO_DIR}"/.claude/agents/*.md; do
    [[ -f "${agent_file}" ]] || continue
    REPO_AGENTS+=("$(basename "${agent_file}")")
  done
}

manifest_items() {
  local key="$1"
  python3 - <<'PY' "${MANIFEST_PATH}" "${key}"
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
key = sys.argv[2]
if not manifest_path.exists():
    raise SystemExit(0)
data = json.loads(manifest_path.read_text(encoding="utf-8"))
for item in data.get(key, []):
    print(item)
PY
}

contains_name() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    if [[ "${item}" == "${needle}" ]]; then
      return 0
    fi
  done
  return 1
}

prune_removed_assets() {
  local previous_skill
  local previous_agent

  if [[ "${AGENT_MODE}" == "codex" || "${AGENT_MODE}" == "both" || "${AGENT_MODE}" == "auto" ]]; then
    while IFS= read -r previous_skill; do
      [[ -n "${previous_skill}" ]] || continue
      if ! contains_name "${previous_skill}" "${REPO_SKILLS[@]}"; then
        remove_path "${CODEX_DIR}/skills/${previous_skill}"
      fi
    done < <(manifest_items codex_skills)
  fi

  if [[ "${AGENT_MODE}" == "claude" || "${AGENT_MODE}" == "both" || "${AGENT_MODE}" == "auto" ]]; then
    while IFS= read -r previous_skill; do
      [[ -n "${previous_skill}" ]] || continue
      if ! contains_name "${previous_skill}" "${REPO_SKILLS[@]}"; then
        remove_path "${CLAUDE_DIR}/skills/${previous_skill}"
      fi
    done < <(manifest_items claude_skills)

    while IFS= read -r previous_agent; do
      [[ -n "${previous_agent}" ]] || continue
      if ! contains_name "${previous_agent}" "${REPO_AGENTS[@]}"; then
        remove_path "${CLAUDE_DIR}/agents/${previous_agent}"
      fi
    done < <(manifest_items claude_agents)
  fi
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
  python3 - <<'PY' "${MANIFEST_PATH}" "${REPO_DIR}" "${CLAUDE_DIR}" "${CODEX_DIR}" "${AGENT_MODE}" "${REPO_SKILLS[@]}" --agents "${REPO_AGENTS[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

manifest_path = Path(sys.argv[1])
repo_dir = sys.argv[2]
claude_dir = sys.argv[3]
codex_dir = sys.argv[4]
agent_mode = sys.argv[5]

raw_items = sys.argv[6:]
split_at = raw_items.index("--agents") if "--agents" in raw_items else len(raw_items)
skills = raw_items[:split_at]
agents = raw_items[split_at + 1 :] if split_at < len(raw_items) else []

payload = {
    "repo_dir": repo_dir,
    "claude_dir": claude_dir,
    "codex_dir": codex_dir,
    "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "agent_mode": agent_mode,
    "claude_skills": skills,
    "codex_skills": skills,
    "claude_agents": agents,
}
manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY
}

main() {
  collect_repo_assets
  prune_removed_assets
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
