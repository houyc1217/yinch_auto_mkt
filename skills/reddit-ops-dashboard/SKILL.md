---
name: reddit-ops-dashboard
description: Analyze Reddit account performance over the last 72 hours, cluster posts into batch waves, and build or update a bilingual HTML operations dashboard with live-only reply queue, per-batch drilldowns, and account action log. Use when the user wants Reddit ops reporting, subreddit-by-subreddit post triage, removed-vs-live batch analysis, or a reusable dashboard and automation template for a Reddit account.
---

# Reddit Ops Dashboard

Use this skill when the user wants a repeatable Reddit account review that ends in a usable operations dashboard rather than a loose summary.

## Workflow

1. Default to the last 72 hours unless the user asks for a different window.
2. Collect three Reddit performance surfaces:
   - `performance/posts` for batch size, post status, and visible post metrics
   - `performance/comments` for reply queue truth and recent account comment actions
   - `performance/account` for baseline account context
3. Group posts into batches before discussing individual threads.
4. Build or update the dashboard from `assets/reddit_ops_dashboard_template.html`.
5. Keep the top layer concise:
   - summary
   - meta
   - KPI cards
   - visuals
   - priority batches
   - reply queue
   - batch map
   - moderation and risk
   - action log
6. Add per-batch drilldowns that list every tracked post with:
   - subreddit
   - title
   - status
   - views
   - upvote rate
   - comments
   - shares
   - direct Reddit link when available

## Output Contract

Save artifacts under:

- `./yinch-auto-mkt-output/reddit-ops-dashboard/<timestamp>/`

Each run should produce:

- `input/request.json`
- `collection/posts_feed.json`
- `collection/comments_feed.json`
- `collection/account_snapshot.json`
- `analysis/batches.json`
- `analysis/reply_queue.json`
- `analysis/action_log.json`
- `deliverables/reddit_ops_dashboard.html`
- `deliverables/email_summary.md` when the user also wants email/automation output

## Operating Rules

- Treat `performance/posts` as the source of truth for batch size and post status.
- Treat `performance/comments` as the source of truth for whether a comment branch still needs a reply.
- Do not let removed, deleted, locked, or unavailable threads stay inside actionable panels.
- Keep `Reply Queue` limited to live unresolved comment branches only.
- Build `Action Log` from the Reddit account's own actions:
  - posts
  - removals
  - comments
  - replies
- Do not mix analyst actions into `Action Log`.
- Keep the total page concise; push per-post detail into batch drilldowns.
- If a user points to a missing post that belongs to a known batch, treat that as a data-gap bug and re-extract the batch before trusting the counts.

## Automation Rule

When the user wants recurring reporting, keep the same dashboard structure and default to every 72 hours unless they ask for another cadence.

## References

- Use [references/data-sources.md](references/data-sources.md) for source priority and queue rules.
- Use [references/dashboard-layout.md](references/dashboard-layout.md) for layout requirements and data fields.
