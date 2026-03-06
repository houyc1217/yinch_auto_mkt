# Filtering And Metrics

## Strict Sample Policy

Only count posts whose normalized `post_type` is:

- `article`
- `post`

Always exclude:

- `quote`
- `note`
- reply
- retweet
- thread continuation

The target sample is exactly 20 valid posts per KOL.

## Metrics

- `engagement = likes + retweets + replies`
- `engagement_rate = engagement / impressions`
- `cost_per_impression = normalized_price / average_impression`

Compute these from the final selected 20 posts only:

- average impression
- median impression
- average engagement
- median engagement
- engagement rate
- median engagement rate
- cost per impression

## Fallback Order

1. Logged-in X browser GraphQL session
2. Guest/public GraphQL collection
3. DOM discovery/search fallback when a browser is already in use

Every KOL must record which source actually supplied the selected sample.
