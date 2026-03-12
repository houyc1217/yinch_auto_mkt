#!/usr/bin/env python3
import argparse
import json

from playwright.sync_api import sync_playwright


def run_for_handle(page, handle: str):
    query = f"from:{handle} -filter:replies -filter:retweets"
    page.goto(f"https://x.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    rows = page.evaluate(
        """
        ({ targetHandle, scrollRounds }) => {
          const parseCount = (text) => {
            if (!text) return 0;
            const cleaned = text.replace(/,/g, '').trim().toUpperCase();
            const m = cleaned.match(/([0-9]*\\.?[0-9]+)([KMB])?/);
            if (!m) return 0;
            const n = parseFloat(m[1]);
            const mult = m[2] === 'K' ? 1000 : m[2] === 'M' ? 1000000 : m[2] === 'B' ? 1000000000 : 1;
            return Math.round(n * mult);
          };
          const collectRows = () => {
            const rows = [];
            for (const article of Array.from(document.querySelectorAll('article'))) {
              const timeLink = article.querySelector('a[href*="/status/"]');
              if (!timeLink) continue;
              const href = timeLink.getAttribute('href') || '';
              const match = href.match(/^\\/([^\\/]+)\\/status\\/(\\d+)/);
              if (!match) continue;
              const rowHandle = match[1];
              const statusId = match[2];
              if (rowHandle.toLowerCase() !== targetHandle.toLowerCase()) continue;
              const allText = article.innerText || '';
              const isQuote = /\\nQuote\\n/.test(allText) || /^Quote\\n/.test(allText) || allText.includes('Quote ');
              const isArticle = allText.includes('\\nArticle\\n') || allText.includes('Article cover image');
              const textNodes = Array.from(article.querySelectorAll('div[lang]'));
              const text = textNodes.map((n) => (n.innerText || '').trim()).filter(Boolean).join('\\n').slice(0, 2000);
              const time = article.querySelector('time');
              let replies = 0;
              let reposts = 0;
              let likes = 0;
              let views = 0;
              for (const el of Array.from(article.querySelectorAll('button, a'))) {
                const label = ((el.getAttribute('aria-label') || el.textContent || '') + '').trim();
                if (!label) continue;
                if (/Replies?\\./i.test(label) || /Replies?,/i.test(label)) replies = parseCount(label);
                if (/reposts?\\./i.test(label) || /reposts?,/i.test(label)) reposts = parseCount(label);
                if (/Likes?\\./i.test(label) || /Likes?,/i.test(label)) likes = parseCount(label);
                if (/views?\\./i.test(label) || /views?,/i.test(label) || /View post analytics/i.test(label)) views = parseCount(label);
              }
              rows.push({
                id: statusId,
                handle: rowHandle,
                url: `https://x.com/${rowHandle}/status/${statusId}`,
                created_at: time ? (time.getAttribute('datetime') || '') : '',
                text_preview: text.split('\\n')[0] ? text.split('\\n')[0].slice(0, 200) : '',
                post_type: isQuote ? 'quote' : (isArticle ? 'article' : 'post'),
                impressions: views,
                likes,
                retweets: reposts,
                replies,
                engagement: replies + reposts + likes,
                engagement_rate: views ? Number(((replies + reposts + likes) / views).toFixed(6)) : null,
                source_used: 'logged_in_x_search_dom',
                is_reply: false,
                is_retweet: false,
                is_thread_continuation: false,
              });
            }
            return rows;
          };
          return new Promise((resolve) => {
            const seen = new Map();
            let rounds = 0;
            const step = () => {
              for (const row of collectRows()) {
                if (!seen.has(row.id)) seen.set(row.id, row);
              }
              rounds += 1;
              if (seen.size >= 30 || rounds >= scrollRounds) {
                resolve(Array.from(seen.values()));
                return;
              }
              window.scrollBy(0, 2600);
              setTimeout(step, 1400);
            };
            step();
          });
        }
        """,
        {"targetHandle": handle, "scrollRounds": 14},
    )
    rows.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return rows, [{"source": "logged_in_x_search_dom", "query": query, "candidate_count": len(rows)}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", required=True)
    parser.add_argument("--auth-state", required=True)
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(storage_state=args.auth_state, viewport={"width": 1280, "height": 900}, user_agent="Mozilla/5.0")
        page = context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        rows, raw_pages = run_for_handle(page, args.handle.lstrip("@"))
        context.close()
        browser.close()
    print(json.dumps({"candidates": rows, "raw_pages": raw_pages}, ensure_ascii=False))


if __name__ == "__main__":
    main()
