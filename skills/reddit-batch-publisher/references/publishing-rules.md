# Reddit Batch Publisher Rules

## Canonical body

- If the user says the body must stay unchanged, treat the supplied body as immutable.
- Do not add summary lines, framing paragraphs, or replacement phrasing.
- Preserve requested blank lines and heading style when those formatting details are explicit.

## Submission mode selection

- Prefer `image + text` when the subreddit submission UI supports it.
- If the subreddit blocks images and the user allows fallback, submit as `text`.
- Record the actual mode used per subreddit instead of assuming uniform support.

## Live-count logic

- Count only live posts toward the requested success target.
- Do not count posts marked as removed, deleted, unavailable, or awaiting approval.
- Re-check live status before closing the run.

## Editability handling

- Text posts are normally editable.
- Reddit `image` posts may not expose a body edit entry even when the post shows body text.
- If no real edit entry exists, mark the post as `replace_required` rather than claiming it was updated.

## Comment follow-up boundary

- Draft replies only when they stay factual, contextual, and non-deceptive.
- Do not invent personal experience, hidden intent, or unverifiable claims.
- If the requested behavior depends on persona deception, stop at the draft queue.

## Credential handling

- Never write Reddit credentials, cookies, tokens, or browser exports into repo files.
- Reuse live login only inside the active headed browser session.
