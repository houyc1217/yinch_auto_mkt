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
bash -n install.sh update.sh scripts/*.sh skills/x-kol/scripts/bootstrap_runtime.sh skills/linkedin-post/scripts/bootstrap_runtime.sh
python3 -m py_compile skills/x-kol/scripts/run_x_kol.py skills/linkedin-post/scripts/run_linkedin_post.py
```

## 3. Runtime smoke tests

LinkedIn draft:

```bash
python3 skills/linkedin-post/scripts/run_linkedin_post.py \
  --product-name "NetMind Arena" \
  --product-context "Multi-agent AI collaboration for operators"
```

X KOL flow:

Use the skill bootstrap wrapper so runtime dependencies self-heal:

```bash
skills/x-kol/scripts/bootstrap_runtime.sh \
  --mode account_list \
  --targets @DataChaz \
  --product-context "NetMind Arena"
```
