#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_ROOT = "yinch-auto-mkt-output/reddit-batch-publisher"


@dataclass
class RequestPayload:
    title: str
    body: str
    image_path: str | None
    target_subreddits: list[str]
    target_count: int | None
    allow_text_fallback: bool
    strict_body: bool
    comment_queue: bool
    request_file: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a traceable Reddit batch publishing run.")
    parser.add_argument("--title")
    parser.add_argument("--body")
    parser.add_argument("--body-file")
    parser.add_argument("--image-path")
    parser.add_argument("--subreddit", action="append", default=[])
    parser.add_argument("--target-count", type=int)
    parser.add_argument("--request-file")
    parser.add_argument("--allow-text-fallback", action="store_true")
    parser.add_argument("--strict-body", action="store_true")
    parser.add_argument("--comment-queue", action="store_true")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_body(args: argparse.Namespace, request_payload: dict[str, Any]) -> str:
    if args.body is not None:
        return args.body
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if request_payload.get("body_file"):
        return Path(request_payload["body_file"]).read_text(encoding="utf-8")
    if request_payload.get("body") is not None:
        return str(request_payload["body"])
    raise ValueError("A Reddit post body is required.")


def normalize_subreddit(raw: str) -> str:
    cleaned = raw.strip()
    cleaned = re.sub(r"^https?://(www\.)?reddit\.com/r/", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^/?r/", "", cleaned, flags=re.I)
    cleaned = cleaned.split("/")[0]
    return cleaned.strip().lower()


def load_request(args: argparse.Namespace) -> RequestPayload:
    request_payload: dict[str, Any] = {}
    if args.request_file:
        request_payload = json.loads(Path(args.request_file).read_text(encoding="utf-8"))

    title = args.title or request_payload.get("title")
    if not title:
        raise ValueError("A Reddit post title is required.")

    body = load_body(args, request_payload)
    subreddits = args.subreddit or request_payload.get("target_subreddits") or []
    normalized_targets = []
    seen = set()
    for raw in subreddits:
        normalized = normalize_subreddit(str(raw))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        normalized_targets.append(normalized)

    target_count = args.target_count if args.target_count is not None else request_payload.get("target_count")
    allow_text_fallback = bool(args.allow_text_fallback or request_payload.get("allow_text_fallback", True))
    strict_body = bool(args.strict_body or request_payload.get("strict_body", True))
    comment_queue = bool(args.comment_queue or request_payload.get("comment_queue", False))
    image_path = args.image_path or request_payload.get("image_path")
    if image_path and not Path(image_path).exists():
        raise ValueError(f"Image path does not exist: {image_path}")

    return RequestPayload(
        title=str(title),
        body=body,
        image_path=str(image_path) if image_path else None,
        target_subreddits=normalized_targets,
        target_count=int(target_count) if target_count is not None else None,
        allow_text_fallback=allow_text_fallback,
        strict_body=strict_body,
        comment_queue=comment_queue,
        request_file=args.request_file,
    )


def build_canonical_post(payload: RequestPayload) -> str:
    lines = [
        f"# {payload.title}",
        "",
        "## Canonical Body",
        "",
        payload.body,
        "",
        "## Posting Rules",
        "",
        f"- strict_body: {str(payload.strict_body).lower()}",
        f"- allow_text_fallback: {str(payload.allow_text_fallback).lower()}",
        f"- image_path: {payload.image_path or 'none'}",
        f"- target_count: {payload.target_count if payload.target_count is not None else 'not set'}",
    ]
    return "\n".join(lines) + "\n"


def build_target_plan(payload: RequestPayload) -> list[dict[str, Any]]:
    plan = []
    for subreddit in payload.target_subreddits:
        plan.append(
            {
                "subreddit": subreddit,
                "preferred_mode": "image_and_text" if payload.image_path else "text",
                "fallback_mode": "text" if payload.allow_text_fallback else None,
                "status": "planned",
                "submission_url": None,
                "live_status": "unknown",
                "editability": "unknown",
                "notes": [],
            }
        )
    return plan


def build_posting_session(payload: RequestPayload, plan: list[dict[str, Any]]) -> str:
    lines = [
        f"# Reddit Batch Posting Session - {payload.title}",
        "",
        "## Session Goals",
        "",
        f"- Requested live target: {payload.target_count if payload.target_count is not None else 'not set'}",
        f"- Requested target list size: {len(plan)}",
        f"- Image path: {payload.image_path or 'none'}",
        "",
        "## Execution Rules",
        "",
        "- Keep the canonical body exact when strict_body is true.",
        "- Prefer image + text when the subreddit accepts it.",
        "- Fall back to text only when images are blocked and allow_text_fallback is true.",
        "- Re-check live status before counting a post toward the target.",
        "- Mark image posts that cannot be edited as replace_required.",
        "",
        "## Target Queue",
        "",
    ]
    if not plan:
        lines.append("- No subreddit targets were supplied. Add targets before live posting.")
    else:
        lines.extend(f"- r/{item['subreddit']} ({item['preferred_mode']})" for item in plan)
    if payload.comment_queue:
        lines.extend(
            [
                "",
                "## Comment Queue",
                "",
                "- Build draft replies only when they stay factual and non-deceptive.",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    payload = load_request(args)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path.cwd() / args.output_root / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "input" / "request.json", asdict(payload))
    write_text(run_dir / "analysis" / "canonical_post.md", build_canonical_post(payload))

    target_plan = build_target_plan(payload)
    write_json(run_dir / "analysis" / "subreddit_targets.json", target_plan)

    post_status = {
        "live_target": payload.target_count,
        "targets_supplied": len(target_plan),
        "targets_live": 0,
        "targets_removed": 0,
        "targets_pending": len(target_plan),
        "posts": target_plan,
    }
    write_json(run_dir / "tracking" / "post_status.json", post_status)

    editability = {
        "canonical_body_strict": payload.strict_body,
        "rule": "If Reddit stores a post as post-type=image and no body edit entry exists, mark replace_required.",
        "posts": [
            {
                "subreddit": item["subreddit"],
                "submission_url": None,
                "editability": "unknown",
                "replacement_required": False,
            }
            for item in target_plan
        ],
    }
    write_json(run_dir / "tracking" / "editability.json", editability)

    if payload.comment_queue:
        write_text(
            run_dir / "deliverables" / "comment_queue.md",
            "\n".join(
                [
                    "# Reddit Comment Queue",
                    "",
                    "- Status: draft_only",
                    "- Rule: Keep replies factual, non-deceptive, and tied to the post context.",
                    "",
                    "No queued comments have been recorded yet.",
                ]
            )
            + "\n",
        )

    write_text(run_dir / "deliverables" / "posting_session.md", build_posting_session(payload, target_plan))
    write_text(
        run_dir / "deliverables" / "posting_report.md",
        "\n".join(
            [
                f"# Reddit Batch Posting Report - {payload.title}",
                "",
                f"- Run directory: {run_dir}",
                f"- Target count: {payload.target_count if payload.target_count is not None else 'not set'}",
                f"- Target list size: {len(target_plan)}",
                f"- Strict body: {str(payload.strict_body).lower()}",
                "",
                "Use this run folder as the single source of truth while the browser posting session is in progress.",
            ]
        )
        + "\n",
    )

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
