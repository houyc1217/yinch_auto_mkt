# Output Schema

All run artifacts should live under:

`./yinch-auto-mkt-output/google-review/<timestamp>/`

## Files

### `input/request.json`

Normalized request payload.

Suggested keys:

- `source_url`
- `place_name`
- `language`
- `notify_telegram`
- `telegram_chat_id`
- `headed`

### `research/page_capture.json`

Browser capture metadata.

Suggested keys:

- `source_url`
- `final_url`
- `capture_method`
- `status`
- `review_count_seen`
- `debug_notes`

### `research/extracted_review.json`

Best extracted review.

Suggested keys:

- `reviewer_name`
- `rating`
- `review_text`
- `review_date`
- `source_type`

### `draft/review_package.json`

Reusable package for downstream workflows.

Suggested keys:

- `caption`
- `caption_short`
- `review_summary`
- `asset_path`
- `asset_type`
- `channel_requirements`

### `setup/setup_needed.json`

Created only when additional setup is needed.

Suggested keys:

- `telegram_required`
- `publishing_required`
- `recommended_next_skill`
- `missing_items`
