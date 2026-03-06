#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import shorten
from typing import Any


DEFAULT_OUTPUT_ROOT = "yinch-auto-mkt-output/google-review"
REVIEW_CARD_SVG = """<svg width="1200" height="630" viewBox="0 0 1200 630" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="1200" height="630" rx="32" fill="#F8FAFC"/>
<rect x="48" y="48" width="1104" height="534" rx="28" fill="white" stroke="#E2E8F0"/>
<text x="96" y="130" fill="#111827" font-family="ui-sans-serif, system-ui, sans-serif" font-size="34" font-weight="700">{place_name}</text>
<text x="96" y="176" fill="#6B7280" font-family="ui-sans-serif, system-ui, sans-serif" font-size="22">Posted on Google Maps</text>
<text x="96" y="238" fill="#F59E0B" font-family="ui-sans-serif, system-ui, sans-serif" font-size="28" font-weight="700">{stars}</text>
<text x="96" y="290" fill="#111827" font-family="ui-sans-serif, system-ui, sans-serif" font-size="28" font-weight="600">{reviewer_name}</text>
<text x="96" y="330" fill="#6B7280" font-family="ui-sans-serif, system-ui, sans-serif" font-size="22">{review_date}</text>
<foreignObject x="96" y="372" width="1008" height="150">
  <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: ui-sans-serif,system-ui,sans-serif; font-size: 32px; line-height: 1.45; color: #111827;">{review_text}</div>
</foreignObject>
</svg>
"""


@dataclass
class RequestPayload:
    source_url: str
    place_name: str
    language: str
    headed: bool
    notify_telegram: bool
    telegram_chat_id: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a Google Maps review into a reusable package.")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--place-name", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--notify-telegram", action="store_true")
    parser.add_argument("--telegram-chat-id")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def capture_review(payload: RequestPayload, run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], Path | None]:
    screenshot_path = run_dir / "deliverables" / "review_screenshot.png"
    debug_path = run_dir / "research" / "debug_page.png"
    page_capture = {
        "source_url": payload.source_url,
        "final_url": payload.source_url,
        "capture_method": "playwright_public_page",
        "status": "fallback",
        "review_count_seen": 0,
        "debug_notes": [],
    }
    extracted = {
        "reviewer_name": "Unknown reviewer",
        "rating": 5,
        "review_text": "Unable to capture a public review card from Google Maps. A fallback review card was created instead.",
        "review_date": "",
        "source_type": "fallback",
    }
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not payload.headed)
            page = browser.new_page(viewport={"width": 1440, "height": 1600})
            page.goto(payload.source_url, wait_until="domcontentloaded", timeout=45000)
            page.screenshot(path=str(debug_path), full_page=True)

            try:
                page.locator('button[role="tab"]').filter(has_text=re.compile("reviews", re.I)).first.click(timeout=8000)
            except Exception:
                page_capture["debug_notes"].append("Reviews tab was not clicked explicitly; continuing on current view.")

            try:
                scroll_container = page.locator(".DxyBCb").first
                for _ in range(4):
                    scroll_container.evaluate("(el) => el.scrollBy(0, 1200)")
                    page.wait_for_timeout(800)
            except Exception:
                page_capture["debug_notes"].append("Could not scroll review container.")

            reviews = page.locator("div.jftiEf")
            count = reviews.count()
            page_capture["review_count_seen"] = count

            best_review = None
            best_len = -1
            for i in range(min(count, 12)):
                review = reviews.nth(i)
                try:
                    text = review.locator(".wiI7pd").first.inner_text(timeout=1000).strip()
                except Exception:
                    text = ""
                try:
                    reviewer_name = review.locator(".d4r55").first.inner_text(timeout=1000).strip()
                except Exception:
                    reviewer_name = "Unknown reviewer"
                try:
                    rating_label = review.locator(".kvMYJc").first.get_attribute("aria-label", timeout=1000) or ""
                except Exception:
                    rating_label = ""
                rating_match = re.search(r"(\d)", rating_label)
                rating = int(rating_match.group(1)) if rating_match else 5
                try:
                    review_date = review.locator(".rsqaWe").first.inner_text(timeout=1000).strip()
                except Exception:
                    review_date = ""
                if rating >= 4 and len(text) > best_len:
                    best_len = len(text)
                    best_review = {
                        "locator": review,
                        "reviewer_name": reviewer_name,
                        "rating": rating,
                        "review_text": text,
                        "review_date": review_date,
                    }

            if best_review:
                best_review["locator"].screenshot(path=str(screenshot_path))
                extracted = {
                    "reviewer_name": best_review["reviewer_name"],
                    "rating": best_review["rating"],
                    "review_text": best_review["review_text"],
                    "review_date": best_review["review_date"],
                    "source_type": "real_screenshot",
                }
                page_capture["status"] = "success"
            browser.close()
    except Exception as exc:
        page_capture["debug_notes"].append(str(exc))

    return page_capture, extracted, screenshot_path if screenshot_path.exists() else None


def render_svg_card(run_dir: Path, payload: RequestPayload, extracted: dict[str, Any]) -> Path:
    svg_path = run_dir / "deliverables" / "review_card.svg"
    stars = "★" * max(1, int(extracted.get("rating", 5)))
    content = REVIEW_CARD_SVG.format(
        place_name=escape_xml(payload.place_name),
        stars=escape_xml(stars),
        reviewer_name=escape_xml(extracted.get("reviewer_name") or "Unknown reviewer"),
        review_date=escape_xml(extracted.get("review_date") or ""),
        review_text=escape_xml(shorten(extracted.get("review_text") or "", width=280, placeholder="...")),
    )
    write_text(svg_path, content)
    return svg_path


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_caption(extracted: dict[str, Any], payload: RequestPayload) -> dict[str, str]:
    excerpt = shorten(extracted["review_text"], width=160, placeholder="...")
    if payload.language == "zh":
        caption = f"Google Maps 用户评价摘录：\n\n“{excerpt}”\n\n这条评论已整理为可复用素材。"
        summary = f"{payload.place_name} 的 Google Maps 评论素材包"
    else:
        caption = f"From a Google Maps review:\n\n\"{excerpt}\"\n\nThis review has been packaged as a reusable asset."
        summary = f"Reusable Google Maps review package for {payload.place_name}"
    return {"caption": caption, "summary": summary}


def maybe_write_setup_needed(run_dir: Path, payload: RequestPayload) -> dict[str, Any] | None:
    missing_items = []
    if payload.notify_telegram:
        if not payload.telegram_chat_id:
            missing_items.append("telegram_chat_id")
        if not (Path.home() / ".yinch-auto-mkt" / "config" / "channels.env.example").exists():
            missing_items.append("telegram_channel_setup")
        if "TELEGRAM_BOT_TOKEN" not in __import__("os").environ:
            missing_items.append("TELEGRAM_BOT_TOKEN")
    if not missing_items:
        return None
    setup_needed = {
        "telegram_required": payload.notify_telegram,
        "publishing_required": False,
        "recommended_next_skill": "channel-setup",
        "missing_items": missing_items,
    }
    write_json(run_dir / "setup" / "setup_needed.json", setup_needed)
    return setup_needed


def main() -> int:
    args = parse_args()
    payload = RequestPayload(
        source_url=args.source_url,
        place_name=args.place_name,
        language=args.language,
        headed=args.headed,
        notify_telegram=args.notify_telegram,
        telegram_chat_id=args.telegram_chat_id,
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path.cwd() / args.output_root / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "input" / "request.json", asdict(payload))

    page_capture, extracted, real_screenshot = capture_review(payload, run_dir)
    write_json(run_dir / "research" / "page_capture.json", page_capture)
    write_json(run_dir / "research" / "extracted_review.json", extracted)

    fallback_svg = None
    if real_screenshot is None:
        fallback_svg = render_svg_card(run_dir, payload, extracted)

    caption = build_caption(extracted, payload)
    asset_path = str(real_screenshot or fallback_svg)
    review_package = {
        "caption": caption["caption"],
        "caption_short": shorten(caption["caption"], width=110, placeholder="..."),
        "review_summary": caption["summary"],
        "asset_path": asset_path,
        "asset_type": "real_screenshot" if real_screenshot else "fallback_svg",
        "channel_requirements": {
            "telegram": payload.notify_telegram,
            "social_publishing": False,
        },
    }
    write_json(run_dir / "draft" / "review_package.json", review_package)

    markdown = "\n".join(
        [
            f"# Google Review Package - {payload.place_name}",
            "",
            f"- Source URL: {payload.source_url}",
            f"- Reviewer: {extracted['reviewer_name']}",
            f"- Rating: {extracted['rating']}",
            f"- Asset: {asset_path}",
            "",
            "## Review Text",
            "",
            extracted["review_text"],
            "",
            "## Caption Draft",
            "",
            review_package["caption"],
            "",
        ]
    )
    write_text(run_dir / "deliverables" / "google_review.md", markdown)
    write_json(run_dir / "deliverables" / "google_review.json", {"review": extracted, "package": review_package})

    setup_needed = maybe_write_setup_needed(run_dir, payload)
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "asset_path": asset_path,
                "source_type": extracted["source_type"],
                "setup_needed": setup_needed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
