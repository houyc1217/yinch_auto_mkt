# Reddit Batch Publisher Output Schema

## Default run root

- `./yinch-auto-mkt-output/reddit-batch-publisher/<timestamp>/`

## Files

### `input/request.json`

- normalized request payload
- canonical title
- canonical body
- image path
- target subreddits
- live target count
- strict body flag

### `analysis/canonical_post.md`

- exact canonical body for edits and reposts
- posting-mode rules
- image reference

### `analysis/subreddit_targets.json`

Each target should track:

- `subreddit`
- `preferred_mode`
- `fallback_mode`
- `status`
- `submission_url`
- `live_status`
- `editability`
- `notes`

### `tracking/post_status.json`

- aggregate live target
- number of supplied targets
- live count
- removed count
- pending count
- per-post tracking entries

### `tracking/editability.json`

- canonical body strictness
- editability rule summary
- per-post editability and replacement requirement

### `deliverables/posting_session.md`

- human-facing execution brief for the browser session
- target queue
- comment queue note when applicable

### `deliverables/posting_report.md`

- compact summary of the run
- current live target status
- pointer to the active run directory

### `deliverables/comment_queue.md`

Create only when comment follow-up is requested.

Keep the queue in draft form unless the requested reply behavior stays factual and non-deceptive.
