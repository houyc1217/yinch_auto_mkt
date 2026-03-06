# Output Schema

All run artifacts should live under:

`./yinch-auto-mkt-output/channel-setup/<timestamp>/`

## Files

### `input/request.json`

Normalized requested channels and user choices.

### `analysis/setup_plan.json`

Suggested keys:

- `channels`
- `telegram`
- `x`
- `instagram`
- `recommended_tools`
- `missing_items`

### `deliverables/channel_setup.md`

Readable checklist for the user and the agent.

### `deliverables/channels.env.example`

Non-secret environment template only.
