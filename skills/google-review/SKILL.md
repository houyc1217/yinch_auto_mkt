---
name: google-review
description: Capture a public Google Maps review, generate a reusable review package, and save traceable artifacts in the current working directory. Use for Google Maps review screenshots, review-card assets, testimonial repurposing, and review-based post drafts.
disable-model-invocation: false
---

# Google Review

Use this skill when the user wants a Google Maps review turned into reusable content assets.

The skill should:

- accept a Google Maps share URL and business name
- capture a public review without requiring Google login
- prefer a real review screenshot when possible
- fall back to a rendered review card when the public page cannot be captured cleanly
- save all intermediate artifacts under the user's current working directory
- keep generated caption copy low on AI-style phrasing

Never ask for Google account credentials by default. Public Google Maps reviews should be treated as public content first.

## Workflow

1. Normalize the request:
   - collect `source_url`
   - collect `place_name`
   - collect optional `language`
   - collect whether the user wants Telegram notification or downstream publishing
2. If the user needs Telegram notification or social publishing, check whether `channel-setup` is already complete
3. Bootstrap runtime with `scripts/bootstrap_runtime.sh`
4. Run `scripts/run_google_review.py`
5. Return:
   - screenshot or fallback card path
   - extracted review text and rating
   - reusable caption draft
   - artifact directory

## Entry Points

```bash
skills/google-review/scripts/bootstrap_runtime.sh \
  --source-url "https://maps.app.goo.gl/xxxxx" \
  --place-name "NetMind Cafe"
```

Optional flags:

- `--language en|zh`
- `--headed`
- `--notify-telegram`
- `--telegram-chat-id <id>`

## Output Contract

Each run creates:

- `input/request.json`
- `research/page_capture.json`
- `research/extracted_review.json`
- `draft/review_package.json`
- `deliverables/google_review.md`
- `deliverables/google_review.json`
- `deliverables/review_card.png` or `deliverables/review_card.svg`
- `deliverables/review_screenshot.png` when a real screenshot is captured
- `setup/setup_needed.json` when Telegram or publishing requires additional configuration

Default output root:

- `./yinch-auto-mkt-output/google-review/<timestamp>/`

## Runtime Rules

- Do not ask for Google login unless the public route is clearly blocked and the user explicitly wants to try a login path
- Prefer real screenshots from the public Maps page
- If screenshot capture is blocked, generate a clean fallback review card and mark the source as fallback
- If Telegram notification or social publishing is requested but not configured, hand off to `channel-setup`
- Apply copy rules from [references/copy-rules.md](references/copy-rules.md)

## References

- [references/copy-rules.md](references/copy-rules.md)
- [references/output-schema.md](references/output-schema.md)
- [references/channel-dependencies.md](references/channel-dependencies.md)
