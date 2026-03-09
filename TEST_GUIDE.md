# Test Guide

Use this guide to verify the current Claude Code + Codex installation model.

## 1. Fresh-home integration test

Run the installer against a temporary home directory:

```bash
TMP_HOME="$(mktemp -d)"
export HOME="$TMP_HOME"
export CLAUDE_HOME="$TMP_HOME/.claude"
export CODEX_HOME="$TMP_HOME/.codex"
export YINCH_AUTO_MKT_HOME="$TMP_HOME/.yinch-auto-mkt"

./scripts/install-agent-assets.sh --repo-dir "$(pwd)"
./scripts/check-env.sh --repo-dir "$(pwd)"
```

Expected result:

- Claude Code assets exist in:
  - `~/.claude/skills`
  - `~/.claude/agents`
- Codex assets exist in:
  - `${CODEX_HOME:-~/.codex}/skills`

## 2. Shell validation

```bash
bash -n install.sh update.sh scripts/*.sh \
  skills/google-review/scripts/bootstrap_runtime.sh \
  skills/linkedin-post/scripts/bootstrap_runtime.sh \
  skills/reddit-batch-publisher/scripts/bootstrap_runtime.sh \
  skills/x-kol/scripts/bootstrap_runtime.sh
python3 -m py_compile \
  skills/google-review/scripts/run_google_review.py \
  skills/linkedin-post/scripts/run_linkedin_post.py \
  skills/reddit-batch-publisher/scripts/run_reddit_batch_publisher.py \
  skills/x-kol/scripts/run_x_kol.py
```

## 3. Runtime smoke tests

Shared browser runtime bootstrap:

```bash
./scripts/ensure-browser-runtime.sh --output json >/tmp/yinch-auto-mkt-browser-runtime.json
```

LinkedIn draft:

```bash
python3 skills/linkedin-post/scripts/run_linkedin_post.py \
  --product-name "NetMind Arena" \
  --product-context "Multi-agent AI collaboration for operators"
```

X KOL flow:

Use the skill bootstrap wrapper so the shared browser runtime is reused:

```bash
skills/x-kol/scripts/bootstrap_runtime.sh \
  --mode account_list \
  --targets @DataChaz \
  --product-context "NetMind Arena"
```

Reddit batch publisher scaffold:

```bash
skills/reddit-batch-publisher/scripts/bootstrap_runtime.sh \
  --title "Smoke Test Reddit Batch" \
  --body "Smoke test body." \
  --subreddit testingground4bots \
  --target-count 1
```
