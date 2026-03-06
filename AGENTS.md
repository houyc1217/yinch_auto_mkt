# Yinch Auto MKT

This repository is designed to work with both Codex and Claude Code.

## Default integration targets

- Codex: install skills into `${CODEX_HOME:-~/.codex}/skills`
- Claude Code: install skills into `~/.claude/skills` and agents into `~/.claude/agents`

## If the user asks to install or update this project

Use the repo scripts instead of manually copying files:

- `./install.sh`
- `./update.sh`
- `./scripts/check-env.sh`

## Project conventions

- Keep Codex skills under `skills/`
- Keep Claude Code skills under `skills/` and optional role agents under `.claude/agents/`
- Do not treat slash commands as the primary entrypoint
- Do not rely on the legacy plugin layout
- Do not store credentials, cookies, or tokens in the repo
