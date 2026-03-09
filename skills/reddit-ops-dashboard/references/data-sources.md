# Reddit Data Sources

## Source Priority

1. `performance/posts`
   - Use for batch membership.
   - Use for post status: live, removed, pending approval, locked, unavailable.
   - Use for visible post metrics when Reddit exposes them in the row.
2. `performance/comments`
   - Use for reply queue truth.
   - Use for account comment and reply history.
   - Traverse the visible comment tree before marking a thread as actionable.
3. `performance/account`
   - Use only for account-level baseline context such as follower count or top-level account deltas.

## Reply Queue Rules

- Include only live unresolved branches.
- Exclude threads whose latest visible reply already belongs to the tracked account.
- Exclude removed, deleted, locked, or unavailable threads.
- If the queue is empty, show the empty state explicitly instead of inventing follow-up work.

## Action Log Rules

Include only Reddit account actions:

- post published
- thread removed
- comment posted
- reply posted

Do not include:

- analyst notes
- recommendations
- dashboard-generation actions
- external email or automation actions

## Status Mapping

- `live`: still visible and usable
- `pending`: awaiting moderator approval
- `removed`: removed by moderators
- `deleted`: deleted by author or unavailable as deleted content
- `locked`: visible but closed to new comments
- `unavailable`: cannot be confirmed as live/actionable

## Batch Integrity Check

If the user names or links a post that clearly belongs to the same content wave but is absent from the dashboard:

1. verify the post directly
2. re-scan the relevant `performance/posts` rows
3. rebuild the entire batch counts
4. update live/removed/pending totals before presenting conclusions
