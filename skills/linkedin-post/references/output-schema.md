# Output Schema

All run artifacts should live under:

`./yinch-auto-mkt-output/linkedin-post/<timestamp>/`

## Files

### `input/request.json`

Normalized request payload.

Suggested keys:

- `source_url`
- `product_name`
- `product_context`
- `cta_url`
- `publish`
- `headed`

### `research/source_content.json`

Captured source text and metadata.

Suggested keys:

- `source_url`
- `page_title`
- `final_url`
- `fetch_method`
- `content_excerpt`
- `raw_text_length`

### `research/extracted_points.json`

Generated extraction from the source.

Suggested keys:

- `product_name`
- `hook`
- `pain_point`
- `outcome`
- `proof_points`
- `cta_url`

### `draft/post_package.json`

Human-reviewable package for approval.

Suggested keys:

- `headline`
- `post_body`
- `first_comment`
- `cta_url`
- `approval_required`

### `deliverables/linkedin_post.md`

Readable markdown containing:

- source summary
- final post
- first comment
- CTA link

### `publish/publish_attempt.json`

Publish trace when a publish run is attempted.

Suggested keys:

- `publish_requested`
- `headed`
- `status`
- `steps_completed`
- `error`
