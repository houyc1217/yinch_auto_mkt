# Channel Dependencies

The `google-review` skill itself should work without external publishing integrations.

## Telegram

Only required when the user explicitly wants a Telegram notification.

Required runtime environment variables:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Do not persist Telegram secrets into repo files or output artifacts.

If these are missing, direct the user to the `channel-setup` skill.

## X / Instagram

Not required for review capture itself.

If the user wants to repurpose the review into a publishable post:

- suggest the `linkedin-post` skill for LinkedIn
- suggest `channel-setup` before any X or Instagram publishing workflow
- recommend Rube when the user needs a durable MCP-based integration for X or Instagram
