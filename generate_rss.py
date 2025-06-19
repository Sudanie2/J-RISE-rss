import hashlib
import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://pitmc.go.jp"
RSS_FILE = "rss.xml"

def fetch_articles():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    articles = []

    # aタグで/news/〜形式のリンクを探す
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/news/"):
            link = BASE_URL + href
            title_tag = a.find("h3")
            desc_tag = a.find_next("p")

            if title_tag and desc_tag:
                title = title_tag.get_text(strip=True)
                description = desc_tag.get_text(strip=True)
                if len(title) < 5 or len(description) < 10:
                    continue

                guid = hashlib.md5(link.encode()).hexdigest()
                pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

                articles.append({
                    "title": title,
                    "description": description,
                    "link": link,
                    "guid": guid,
                    "pubDate": pub_date,
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
    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"[OK] RSS書き出し完了 → {RSS_FILE}")

if __name__ == "__main__":
    generate_rss()
