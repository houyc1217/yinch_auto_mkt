# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-03-05

### Added
- Initial release
- LinkedIn post creation skill with NetMind.AI format
- X (Twitter) KOL research and DM automation skill
- One-click installation script
- One-click update script
- Environment check script
- README in Chinese and English

## [1.2.0] - 2026-03-09

### Added
- Reddit batch publisher skill for exact-body post waves, image/text fallback, editability tracking, and live-count backfilling
- Shared browser runtime bootstrap under `~/.yinch-auto-mkt/runtime/browser`
- Claude Code agent for `reddit-batch-publisher`

### Changed
- Browser-capable workflow bootstraps now reuse the shared Playwright runtime instead of recreating Chromium per workflow
- Installer and health checks now account for the shared browser runtime and optional Codex Playwright skills
- README, README.en, and README.zh now list six workflows and the shared browser runtime layout
