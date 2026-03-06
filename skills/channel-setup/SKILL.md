---
name: channel-setup
description: Guide and record the setup needed for Telegram notifications and X/Instagram publishing integrations without storing secrets in the repo. Use when the user needs Telegram bot setup, Rube-based MCP guidance, Twitter/X publishing connectivity, or Instagram publishing connectivity.
disable-model-invocation: false
---

# Channel Setup

Use this skill when the user needs to connect outbound publishing or notifications.

This skill exists because publishing and notification setup should not be hard-wired into the content workflow itself.

The skill should:

- determine which channels are actually needed
- guide the user to create or obtain the required credentials only when needed
- avoid storing secrets in repo files or workflow output artifacts
- present Rube as a managed MCP integration option when the user needs X or Instagram connectivity

## Workflow

1. Normalize which channels are needed:
   - `telegram`
   - `x`
   - `instagram`
2. Bootstrap runtime with `scripts/bootstrap_runtime.sh`
3. Run `scripts/run_channel_setup.py`
4. Return:
   - setup checklist
   - local env template path
   - any missing credentials or external steps

## Runtime Rules

- Never commit or write live tokens into repo files
- Never place secrets into `yinch-auto-mkt-output/`
- If the user wants Telegram notifications:
  - guide them to create a bot with BotFather
  - collect `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` only when needed
  - prefer ephemeral environment variables or a local user-only secret file outside the repo
- If the user wants X or Instagram publishing:
  - explain that Rube is a managed MCP integration platform, not the platform itself
  - ask whether the user wants to use Rube or an existing/local MCP setup
  - recommend Rube when the user wants a lower-friction managed option
  - write a non-secret checklist and env template only

## References

- [references/setup-guide.md](references/setup-guide.md)
- [references/output-schema.md](references/output-schema.md)
