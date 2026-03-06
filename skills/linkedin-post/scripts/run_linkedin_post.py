#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import shorten
from typing import Any

import requests

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
DEFAULT_OUTPUT_ROOT = "yinch-auto-mkt-output/linkedin-post"
REQUEST_TIMEOUT = 20


@dataclass
class RequestPayload:
    source_url: str | None
    product_name: str | None
    product_context: str | None
    cta_url: str | None
    publish: bool
    headed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draft and optionally publish LinkedIn posts for NetMind.")
    parser.add_argument("--source-url")
    parser.add_argument("--product-name")
    parser.add_argument("--product-context")
    parser.add_argument("--cta-url")
    parser.add_argument("--request-file")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def load_request(args: argparse.Namespace) -> RequestPayload:
    file_payload: dict[str, Any] = {}
    if args.request_file:
        file_payload = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
    return RequestPayload(
        source_url=args.source_url or file_payload.get("source_url"),
        product_name=args.product_name or file_payload.get("product_name"),
        product_context=args.product_context or file_payload.get("product_context"),
        cta_url=args.cta_url or file_payload.get("cta_url"),
        publish=bool(args.publish or file_payload.get("publish")),
        headed=bool(args.headed or file_payload.get("headed")),
    )


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "netmind"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def derive_product_name(payload: RequestPayload, source_text: str) -> str:
    if payload.product_name:
        return payload.product_name
    if payload.source_url:
        match = re.search(r"/([^/?#]+)/?$", payload.source_url)
        if match:
            candidate = match.group(1).replace("-", " ").replace("_", " ").strip()
            if candidate:
                return candidate.title()
    if payload.product_context:
        return payload.product_context
    words = source_text.split()
    return " ".join(words[:3]) if words else "NetMind Product"


def fetch_source(payload: RequestPayload) -> dict[str, Any]:
    if not payload.source_url:
        return {
            "source_url": None,
            "page_title": None,
            "final_url": None,
            "fetch_method": "manual_context_only",
            "content_excerpt": payload.product_context or "",
            "raw_text_length": len(payload.product_context or ""),
        }
    response = requests.get(
        payload.source_url,
        headers={"user-agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    html = response.text
    title_match = re.search(r"(?is)<title>(.*?)</title>", html)
    title = title_match.group(1).strip() if title_match else None
    content = strip_html(html)
    return {
        "source_url": payload.source_url,
        "page_title": title,
        "final_url": str(response.url),
        "fetch_method": "requests",
        "content_excerpt": shorten(content, width=4000, placeholder="..."),
        "raw_text_length": len(content),
    }


def extract_points(payload: RequestPayload, source: dict[str, Any]) -> dict[str, Any]:
    source_text = " ".join(
        value for value in [source.get("page_title"), source.get("content_excerpt"), payload.product_context] if value
    ).strip()
    product_name = derive_product_name(payload, source_text)
    proof_points = []
    for sentence in re.split(r"(?<=[.!?])\s+", source_text):
        sentence = sentence.strip()
        if len(sentence) < 40:
            continue
        proof_points.append(sentence)
        if len(proof_points) == 3:
            break
    if not proof_points:
        proof_points = [
            f"{product_name} is positioned around practical AI workflows.",
            "The source emphasizes concrete user outcomes over generic feature claims.",
            "The post should stay specific and operational.",
        ]
    hook = f"Shipping AI workflows is hard when the toolchain still feels stitched together by hand."
    pain_point = f"Teams evaluating {product_name} usually do not need more vague AI capability claims. They need a workflow that is easier to deploy, easier to operate, and easier to trust."
    outcome = f"{product_name} helps move from scattered tooling to a clearer operating path for real AI work."
    return {
        "product_name": product_name,
        "hook": hook,
        "pain_point": pain_point,
        "outcome": outcome,
        "proof_points": proof_points,
        "cta_url": payload.cta_url or source.get("final_url") or payload.source_url,
    }


def build_post_package(points: dict[str, Any]) -> dict[str, Any]:
    product = points["product_name"]
    post_body = "\n\n".join(
        [
            points["hook"],
            points["pain_point"],
            "What stands out:",
            "\n".join(f"• {item}" for item in points["proof_points"]),
            f"With {product} in the loop, the outcome is straightforward: {points['outcome']}",
            "Link in the comments.",
        ]
    )
    first_comment = f"More details: {points['cta_url']}" if points["cta_url"] else "More details in the source link."
    return {
        "headline": f"NetMind.AI | {product}",
        "post_body": post_body,
        "first_comment": first_comment,
        "cta_url": points["cta_url"],
        "approval_required": True,
    }


def build_markdown(source: dict[str, Any], points: dict[str, Any], package: dict[str, Any]) -> str:
    lines = [
        f"# {package['headline']}",
        "",
        "## Source Summary",
        "",
        f"- Source URL: {source.get('source_url') or 'manual context'}",
        f"- Page Title: {source.get('page_title') or 'N/A'}",
        f"- Fetch Method: {source.get('fetch_method')}",
        "",
        "## Extracted Points",
        "",
        f"- Product: {points['product_name']}",
        f"- Hook: {points['hook']}",
        f"- Pain Point: {points['pain_point']}",
        f"- Outcome: {points['outcome']}",
        "- Proof Points:",
    ]
    lines.extend(f"  - {item}" for item in points["proof_points"])
    lines.extend(
        [
            "",
            "## LinkedIn Post",
            "",
            package["post_body"],
            "",
            "## First Comment",
            "",
            package["first_comment"],
            "",
            "## Approval",
            "",
            "Publishing requires explicit user confirmation.",
        ]
    )
    return "\n".join(lines) + "\n"


def attempt_publish(run_dir: Path, package: dict[str, Any], headed: bool) -> dict[str, Any]:
    result = {
        "publish_requested": True,
        "headed": headed,
        "status": "not_started",
        "steps_completed": [],
        "error": None,
    }
    if not headed:
        result["status"] = "blocked"
        result["error"] = "Publishing requires --headed."
        return result
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        result["status"] = "blocked"
        result["error"] = f"Playwright unavailable: {exc}"
        return result

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            result["steps_completed"].append("opened_feed")
            try:
                page.get_by_role("button", name=re.compile("start a post", re.I)).click(timeout=15000)
                result["steps_completed"].append("opened_compose")
                page.locator("[role='textbox']").first.fill(package["post_body"])
                result["steps_completed"].append("filled_post")
                result["status"] = "ready_for_manual_submit"
            except PlaywrightTimeoutError:
                result["status"] = "blocked"
                result["error"] = "Could not reach compose flow. Login or UI confirmation may be required."
            finally:
                context.close()
                browser.close()
    except Exception as exc:  # pragma: no cover
        result["status"] = "failed"
        result["error"] = str(exc)
    return result


def main() -> int:
    args = parse_args()
    payload = load_request(args)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = slugify(payload.product_name or payload.product_context or "linkedin")
    run_dir = Path.cwd() / args.output_root / f"{timestamp}-{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "input/request.json", asdict(payload))
    source = fetch_source(payload)
    write_json(run_dir / "research/source_content.json", source)
    points = extract_points(payload, source)
    write_json(run_dir / "research/extracted_points.json", points)
    package = build_post_package(points)
    write_json(run_dir / "draft/post_package.json", package)
    write_json(run_dir / "deliverables/linkedin_post.json", package)

    markdown = build_markdown(source, points, package)
    for rel in ["draft/linkedin_post.md", "deliverables/linkedin_post.md"]:
        path = run_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")

    publish_result = None
    if payload.publish:
        publish_result = attempt_publish(run_dir, package, payload.headed)
        write_json(run_dir / "publish/publish_attempt.json", publish_result)

    result = {
        "run_dir": str(run_dir),
        "draft_markdown": str(run_dir / "deliverables/linkedin_post.md"),
        "draft_json": str(run_dir / "deliverables/linkedin_post.json"),
        "publish": publish_result,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
