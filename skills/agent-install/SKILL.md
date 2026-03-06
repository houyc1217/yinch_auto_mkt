---
name: agent-install
description: Install, update, or repair Yinch Auto MKT for Codex and Claude Code using their default user-level integration layouts. Use when the user wants one-shot setup, default-path compatibility, environment repair, or verification that the toolkit is ready to use.
disable-model-invocation: false
---

# Agent Install

Use this skill for Yinch Auto MKT installation and compatibility repair.

The goal is simple:

- make the toolkit usable in freshly installed Codex and Claude Code
- install into each agent's default user-level locations
- keep the setup idempotent
- solve environment issues with scripts, not manual prose

## Workflow

1. Run `install.sh` for first-time setup or `update.sh` for refresh
2. Verify with `scripts/check-env.sh`
3. Confirm these locations exist:
   - Codex: `${CODEX_HOME:-~/.codex}/skills`
   - Claude Code: `~/.claude/skills`, `~/.claude/commands`, `~/.claude/agents`
4. Report the installed paths and any missing system prerequisites

## Rules

- Never write credentials into repo files or install manifests
- Prefer symlinks to the repo checkout when possible; fall back to copies only if symlinks fail
- Keep both Codex and Claude Code integrations in sync
