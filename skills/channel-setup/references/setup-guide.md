# Setup Guide

Use this guide only when a workflow actually requires outbound notification or publishing.

## Telegram

When Telegram is required:

1. Ask the user to create a bot with BotFather
2. Ask for:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Do not store the live token in repo files
4. Prefer:
   - shell environment variables
   - a user-local secret file outside the repo

Suggested env names:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## X / Instagram

When X or Instagram publishing is required:

1. Explain what Rube is before recommending it:
   - a managed MCP integration platform / marketplace for connecting apps to AI agents
   - not the social platform itself
   - not proof that the user's X or Instagram publishing flow is already configured
2. Ask whether the user wants:
   - a managed option such as Rube
   - an existing/local MCP setup they already control
3. Recommend Rube when the user wants a lower-friction managed integration path
4. Do not claim a working MCP connection until the user confirms it
5. Save only a non-secret checklist and env template in local config

Suggested env names:

- `RUBE_TWITTER_CONNECTION`
- `RUBE_INSTAGRAM_CONNECTION`

Suggested checklist fields:

- channel requested
- setup method
- user confirmed
- last checked
