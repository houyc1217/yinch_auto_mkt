# Dashboard Layout

## Top-Level Sections

Keep the main page short. Use this order:

1. Summary
2. Report Meta
3. KPI cards
4. Visuals
5. Priority Batches
6. Reply Queue
7. Batch Map
8. Moderation & Risk
9. Action Log

## Batch-First Rule

Do not flatten the whole 72-hour feed into a wall of posts on the main page.

Start with batches:

- repeated theme
- repeated angle
- repeated title family
- repeated posting wave within the window

Then let the operator drill into the batch to inspect every tracked post.

## Batch Drilldown Fields

Each batch drilldown should show one row per tracked post:

- subreddit
- post title
- status
- views
- upvote rate
- comments
- shares
- open-post button when URL is available

## Reply Queue

Show only threads that still need action.

For each actionable row, include:

- thread title or comment context
- subreddit
- urgency or priority
- short reason
- direct open-thread button

## Risk Section

Move non-actionable but important items here:

- removed posts
- locked threads
- pending approval bottlenecks
- communities with repeated moderation friction

## Bilingual Rule

- English should remain the default operator view.
- Chinese toggle is allowed and should update labels and helper text.
- Reddit post titles can stay in their original language.

## Template Asset

Use `assets/reddit_ops_dashboard_template.html` as the starter structure when the user wants a ready HTML dashboard instead of a prose report.
