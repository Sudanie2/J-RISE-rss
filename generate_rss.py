import hashlib
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://pitmc.go.jp/"
RSS_FILE = "rss.xml"

def fetch_articles():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_timeout(3000)  # JS描画待ち（3秒）

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    articles = []

    # タイトルと概要（<h3> + <p>）のセットを探す
    h3_tags = soup.find_all("h3")
    for h3 in h3_tags:
        title = h3.get_text(strip=True)
        p = h3.find_next("p")
        description = p.get_text(strip=True) if p else ""

        if not title or len(title) < 5:
            continue

        guid = hashlib.md5((title + description).encode()).hexdigest()
        pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        articles.append({
            "title": title,
            "description": description,
            "guid": guid,
            "pubDate": pub_date,
            "link": BASE_URL
        })

    return articles

def generate_rss():
    articles = fetch_articles()

    rss_items = ""
    for a in articles:
        rss_items += f"""
        <item>
            <title>{a['title']}</title>
            <link>{a['link']}</link>
            <guid isPermaLink="false">{a['guid']}</guid>
            <pubDate>{a['pubDate']}</pubDate>
            <description>{a['description']}</description>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>J-RISE NEWS</title>
    <link>{BASE_URL}</link>
    <description>J-RISE Initiative公式のニュースフィード</description>
    <language>ja</language>
    {rss_items}
  </channel>
</rss>
"""

    Path(RSS_FILE).write_text(rss, encoding="utf-8")
    print(f"[OK] RSS生成完了 → {RSS_FILE}")

if __name__ == "__main__":
    generate_rss()
