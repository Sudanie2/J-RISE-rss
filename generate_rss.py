import requests
from bs4 import BeautifulSoup
import datetime
import hashlib

BASE_URL = "https://pitmc.go.jp/"
RSS_FILE = "rss.xml"

def fetch_articles():
    res = requests.get(BASE_URL)
    res.encoding = res.apparent_encoding  # 文字化け対策
    soup = BeautifulSoup(res.text, "html.parser")

    # J-RISE NEWS の記事と思われるブロックを抽出
    articles = soup.select("div.sd.text.sd.appear")

    rss_items = ""
    seen = set()

    for article in articles:
        text = article.get_text(strip=True)
        if not text or len(text) < 10:
            continue

        # 重複排除（同じテキストが複数箇所にあるため）
        if text in seen:
            continue
        seen.add(text)

        title = text[:40] + "…" if len(text) > 40 else text
        pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        guid = hashlib.md5(text.encode("utf-8")).hexdigest()
        link = BASE_URL  # 固有リンクがあればここに入れる

        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid isPermaLink="false">{guid}</guid>
            <pubDate>{pub_date}</pubDate>
            <description>{text}</description>
        </item>
        """

    return rss_items

def generate_rss():
    rss_items = fetch_articles()

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
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
        f.write(rss_feed)

if __name__ == "__main__":
    generate_rss()
