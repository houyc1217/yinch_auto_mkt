---
name: linkedin-post
description: Draft and optionally publish LinkedIn posts for NetMind products or announcements from source URLs, notes, or product context. Use when the user wants LinkedIn copy, a first comment with tracked link, a reviewable markdown draft, or headed LinkedIn publishing after explicit approval.
disable-model-invocation: false
---

# LinkedIn Post

Use this skill when the user wants a repeatable LinkedIn workflow for NetMind content.

The skill should:

- accept a source URL, product page, launch note, or manual context
- create a reviewable draft before any publish action
- save all intermediate artifacts under the user's current working directory
- publish only after explicit confirmation, and only through a headed browser flow

Never store LinkedIn credentials, cookies, tokens, auth headers, or machine-specific secret paths in repo files or output artifacts.

## Workflow

1. Normalize the request:
   - collect `source_url`, optional `product_name`, optional `product_context`, optional CTA link
   - default to draft-only unless the user explicitly asks to publish
2. Bootstrap runtime with `scripts/bootstrap_runtime.sh`
3. Run `scripts/run_linkedin_post.py`
4. Review the generated package with the user:
   - draft post
   - first comment
   - tracked link
   - source summary and extracted proof points
5. Publish only after explicit approval, using a headed browser session

## Entry Points

Draft mode:

```bash
skills/linkedin-post/scripts/bootstrap_runtime.sh \
  --source-url "https://www.netmind.ai/..." \
  --product-context "NetMind Arena"
```

Draft from a local request JSON:

```bash
skills/linkedin-post/scripts/bootstrap_runtime.sh \
  --request-file ./linkedin_request.json
```

Publish after approval:

```bash
skills/linkedin-post/scripts/bootstrap_runtime.sh \
  --source-url "https://www.netmind.ai/..." \
  --product-context "NetMind Arena" \
  --publish \
  --headed
```

## Output Contract

Each run creates:

- `input/request.json`
- `research/source_content.json`
- `research/extracted_points.json`
- `draft/post_package.json`
- `draft/linkedin_post.md`
- `deliverables/linkedin_post.md`
- `deliverables/linkedin_post.json`
- `publish/publish_attempt.json` when publish is attempted

Default output root:

- `./yinch-auto-mkt-output/linkedin-post/<timestamp>/`

## Runtime Rules

- Always show the draft package before publishing
- Use NetMind branding rules from [references/brand-rules.md](references/brand-rules.md)
- Apply copy rules from [references/copy-rules.md](references/copy-rules.md)
- Save the publishable markdown and machine-readable JSON every run
- Keep source extraction and generated copy traceable
- Prefer headed browser automation for LinkedIn publishing so the user can see and complete login if needed
- If publishing is blocked by missing login or UI changes, stop and report the exact step reached

## References

- [references/brand-rules.md](references/brand-rules.md)
- [references/copy-rules.md](references/copy-rules.md)
- [references/output-schema.md](references/output-schema.md)
