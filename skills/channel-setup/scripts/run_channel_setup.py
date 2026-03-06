#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_OUTPUT_ROOT = "yinch-auto-mkt-output/channel-setup"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare non-secret channel setup files for Yinch Auto MKT.")
    parser.add_argument("--channels", required=True, help="Comma-separated list: telegram,x,instagram")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    channels = [item.strip() for item in args.channels.split(",") if item.strip()]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path.cwd() / args.output_root / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "input" / "request.json", {"channels": channels})

    plan = {
        "channels": channels,
        "telegram": {
            "required": "telegram" in channels,
            "missing_items": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"] if "telegram" in channels else [],
            "creation_flow": ["Open BotFather", "Create bot", "Get bot token", "Get target chat id"],
        },
        "x": {
            "required": "x" in channels,
            "recommended_tool": "Rube (managed MCP option)" if "x" in channels else None,
            "missing_items": ["RUBE_TWITTER_CONNECTION"] if "x" in channels else [],
        },
        "instagram": {
            "required": "instagram" in channels,
            "recommended_tool": "Rube (managed MCP option)" if "instagram" in channels else None,
            "missing_items": ["RUBE_INSTAGRAM_CONNECTION"] if "instagram" in channels else [],
        },
        "recommended_tools": ["Rube (managed MCP option)"] if any(c in channels for c in ["x", "instagram"]) else [],
        "missing_items": [],
    }
    plan["missing_items"] = []
    for section in ("telegram", "x", "instagram"):
        plan["missing_items"].extend(plan[section]["missing_items"])
    write_json(run_dir / "analysis" / "setup_plan.json", plan)

    env_lines = [
        "# Yinch Auto MKT channel setup template",
        "# Fill these outside the repo or export them in your shell.",
        "TELEGRAM_BOT_TOKEN=" if "telegram" in channels else "# TELEGRAM_BOT_TOKEN=",
        "TELEGRAM_CHAT_ID=" if "telegram" in channels else "# TELEGRAM_CHAT_ID=",
        "RUBE_TWITTER_CONNECTION=" if "x" in channels else "# RUBE_TWITTER_CONNECTION=",
        "RUBE_INSTAGRAM_CONNECTION=" if "instagram" in channels else "# RUBE_INSTAGRAM_CONNECTION=",
    ]
    write_text(run_dir / "deliverables" / "channels.env.example", "\n".join(env_lines) + "\n")

    markdown = [
        "# Channel Setup Checklist",
        "",
        f"Requested channels: {', '.join(channels) or 'none'}",
        "",
    ]
    if "telegram" in channels:
        markdown.extend(
            [
                "## Telegram",
                "",
                "1. Open BotFather",
                "2. Create a bot",
                "3. Collect `TELEGRAM_BOT_TOKEN`",
                "4. Identify the destination `TELEGRAM_CHAT_ID`",
                "5. Export them locally instead of storing them in the repo",
                "",
            ]
        )
    if "x" in channels or "instagram" in channels:
        markdown.extend(
            [
                "## Social MCP",
                "",
                "Rube is a managed MCP integration option for connecting apps like X or Instagram to AI agents.",
                "It is not the platform itself and it should not be treated as already configured until the user confirms the connection works.",
                "Ask the user whether they want to use Rube or an existing/local MCP setup they already control.",
                "",
            ]
        )
    write_text(run_dir / "deliverables" / "channel_setup.md", "\n".join(markdown))

    user_config_dir = Path.home() / ".yinch-auto-mkt" / "config"
    user_config_dir.mkdir(parents=True, exist_ok=True)
    write_text(user_config_dir / "channels.env.example", "\n".join(env_lines) + "\n")

    print(json.dumps({"run_dir": str(run_dir), "user_config": str(user_config_dir / "channels.env.example")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
