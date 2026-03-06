# Output Layout

Each run writes to:

```text
./yinch-auto-mkt-output/x-kol/<timestamp>/
```

## Required Files

```text
input/
  request.json
  targets.json
environment/
  run_context.json
  dependency_report.json
discovery/
  candidate_accounts.json
  search_queries.json
collection/
  <handle>/
    profile.json
    raw_pages.json
    candidates.json
    selected_posts.json
    excluded_posts.json
analysis/
  summary_metrics.json
  workbook_payload.json
deliverables/
  x_kol_analysis.xlsx
```

## Safety Rules

- Safe to share: yes
- Secrets allowed: no
- Cookies allowed: no
- Bearer/auth headers allowed: no
- Browser profile dumps allowed inside run output: no

## Workbook Shape

### `Summary`

One row per included KOL:

- handle
- display_name
- profile_url
- followers
- price
- source_used
- sample_size
- average_impression
- median_impression
- average_engagement
- median_engagement
- engagement_rate
- median_engagement_rate
- cost_per_impression
- assessment

### `Details`

One row per selected or excluded post:

- handle
- post_id
- post_url
- created_at
- post_type
- impressions
- likes
- retweets
- replies
- engagement
- engagement_rate
- selection_status
- exclusion_reason
- text_preview
