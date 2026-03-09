---
name: reddit-batch-publisher
description: Publish one Reddit post across a chosen batch of subreddits, adapt between image+text and text-only submission modes, keep an exact canonical body across edits and reposts, and track live-vs-removed outcomes plus editability. Use when the user wants Reddit batch posting, success-quota backfilling, post-body correction across already-published threads, or a traceable comment queue draft for recent Reddit posts.
disable-model-invocation: false
---

# Reddit Batch Publisher

Use this skill when the user wants a repeatable Reddit posting workflow, not a one-off browser session.

The workflow should:

- preserve the requested title and body exactly when the user says not to rewrite
- post in batches across selected subreddits
- prefer `image + text` when the subreddit allows it
- fall back to `text` when the subreddit disables images
- track which posts are live, removed, or non-editable
- backfill replacements until the requested success count is met

Never store Reddit credentials, cookies, auth headers, or browser session exports in repo files or output artifacts.

## Workflow

1. Normalize the request:
   - collect `title`
   - collect the canonical `body`
   - collect optional `image_path`
   - collect target subreddits or a success-count target
   - collect body-formatting rules such as required blank lines or heading style
2. Bootstrap the runtime with `scripts/bootstrap_runtime.sh`
3. Prepare the run directory and canonical posting package with `scripts/run_reddit_batch_publisher.py`
4. Execute the headed Reddit browser flow:
   - submit to the selected subreddits
   - record the actual submission mode per subreddit
   - save direct URLs for successful posts
5. Re-check post status:
   - live
   - removed
   - awaiting approval
   - deleted
6. If the user asked for a target number of live posts, backfill until that live count is met.
7. If the body changes later, edit every editable post to match the canonical body exactly.
8. If a post is not editable because Reddit stored it as an `image` post, mark it as `replace_required` instead of pretending it was updated.
9. If the user also wants comment follow-up, build a traceable reply queue and keep responses factual, non-deceptive, and consistent with the post context.

## Entry Points

Prepare a run from direct arguments:

```bash
skills/reddit-batch-publisher/scripts/bootstrap_runtime.sh \
  --title '$70 house-call OpenClaw installs are taking off in China' \
  --body-file ./post_body.md \
  --image-path ./image2.png \
  --subreddit agi \
  --subreddit aiagents \
  --target-count 15
```

Prepare a run from a request JSON:

```bash
skills/reddit-batch-publisher/scripts/bootstrap_runtime.sh \
  --request-file ./reddit_batch_request.json
```

## Output Contract

Each run creates:

- `input/request.json`
- `analysis/canonical_post.md`
- `analysis/subreddit_targets.json`
- `tracking/post_status.json`
- `tracking/editability.json`
- `deliverables/posting_session.md`
- `deliverables/posting_report.md`
- `deliverables/comment_queue.md` when comment follow-up is requested

Default output root:

- `./yinch-auto-mkt-output/reddit-batch-publisher/<timestamp>/`

## Runtime Rules

- Treat the canonical body as the single source of truth for all edits and reposts.
- When the user says not to modify the body, do not add intros, summaries, or replacement phrasing.
- Keep heading style only when it matches the user's instruction.
- Prefer live status re-checks before claiming a quota was met.
- Do not count removed or approval-blocked posts toward a live target.
- Record subreddit-specific submission constraints instead of assuming one mode works everywhere.
- For comment follow-up, do not invent personal experience, hidden intent, or unverifiable claims.
- If a requested reply would rely on persona deception, stop at a draft queue instead of auto-posting.

## References

- Use [references/publishing-rules.md](references/publishing-rules.md) for mode selection, live-count rules, editability handling, and comment follow-up boundaries.
- Use [references/output-schema.md](references/output-schema.md) for artifact names and field expectations.
