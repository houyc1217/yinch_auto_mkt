---
name: x-kol
description: Research X/Twitter KOLs from a provided account list or by topic discovery, save traceable intermediate data in the current working directory, and export a strict collaboration workbook. Use for X KOL screening workflows that only count article/post content and exclude quote, note, reply, retweet, and thread continuation.
disable-model-invocation: false
---

# X KOL Research

Use this skill when the user wants a reproducible X KOL workflow that:

- accepts a list of X handles / profile URLs, or discovers KOLs by topic
- saves all intermediate data under the user's current working directory
- outputs a final XLSX with `Summary` and `Details` sheets
- adds `usd_cpm`, calculated as USD cost per 1,000 impressions when a price is provided
- uses a strict sample policy:
  - include only `article` and `post`
  - exclude `quote`, `note`, reply, retweet, and thread continuation

Never store credentials, cookies, bearer tokens, auth headers, or machine-specific secret paths in repo files or output artifacts.

## Workflow

1. Resolve mode:
   - `account_list` when the user provides handles / URLs / a JSON targets file
   - `discovery` when the user provides a topic/domain and desired count
2. Bootstrap runtime with `scripts/bootstrap_runtime.sh`
3. Run `scripts/run_x_kol.py`
4. Keep all artifacts under:
   - `./yinch-auto-mkt-output/x-kol/<timestamp>/`
5. Return:
   - workbook path
   - summary JSON path
   - any omitted KOLs and why

## Entry Points

Use the bootstrap wrapper instead of calling Python directly:

```bash
skills/x-kol/scripts/bootstrap_runtime.sh \
  --mode account_list \
  --targets @foo,https://x.com/bar \
  --product-context "NetMind Arena"
```

Discovery mode:

```bash
skills/x-kol/scripts/bootstrap_runtime.sh \
  --mode discovery \
  --topic "AI agents" \
  --count 10 \
  --product-context "NetMind Arena"
```

Optional inputs:

- `--targets-file <json>`: JSON list of strings or objects with `handle`, `profile_url`, and optional `price`
  - when `price` is present, the skill normalizes supported currencies to USD using Google Finance rates fetched at execution time
- `--count <n>`: desired KOL count in discovery mode
- `--browser-profile <path>`: reuse a local Chrome profile for logged-in fallback
- `--headed`: force headed browser flow for discovery and login fallback

## Output Contract

Each run creates:

- `input/request.json`
- `input/targets.json`
- `environment/run_context.json`
- `environment/dependency_report.json`
- `discovery/candidate_accounts.json`
- `discovery/search_queries.json`
- `collection/<handle>/profile.json`
- `collection/<handle>/raw_pages.json`
- `collection/<handle>/candidates.json`
- `collection/<handle>/selected_posts.json`
- `collection/<handle>/excluded_posts.json`
- `analysis/summary_metrics.json`
- `analysis/workbook_payload.json`
- `deliverables/x_kol_analysis.xlsx`

See references for details:

- [references/filtering-and-metrics.md](references/filtering-and-metrics.md)
- [references/output-layout.md](references/output-layout.md)

## Runtime Rules

- Prefer logged-in X collection when available
- Fall back to guest/public collection when acceptable
- Record `source_used` per KOL
- Do not silently downgrade strict filtering
- Omit KOLs with fewer than 20 valid strict posts unless the user explicitly requests partial output
- In discovery mode, continue with replacement candidates instead of putting partial KOLs into the final workbook
