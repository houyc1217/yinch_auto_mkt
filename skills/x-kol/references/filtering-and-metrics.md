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
- `usd_cpm = normalized_price_usd / (average_impression / 1000)`

Compute these from the final selected 20 posts only:

- average impression
- median impression
- average engagement
- median engagement
- engagement rate
- median engagement rate
- cost per impression
- USD CPM

## Price Normalization

- If a target includes a `price`, normalize it to USD at execution time.
- Use Google Finance as the FX source of truth for the run.
- Supported currencies:
  - USD / `$`
  - EUR / `€`
  - GBP / `£`
  - RMB / CNY / CNH
- `usd_cpm` should be formatted to 2 decimal places.
- When multiple prices appear in one price label, use the lowest normalized USD amount for the summary-row CPM calculation.

## Fallback Order

1. Logged-in X browser GraphQL session
2. Guest/public GraphQL collection
3. DOM discovery/search fallback when a browser is already in use

Every KOL must record which source actually supplied the selected sample.
