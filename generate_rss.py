import requests
from bs4 import BeautifulSoup
import datetime
import hashlib
import json
import os

BASE_URL = "https://pitmc.go.jp/"
RSS_FILE = "rss.xml"
CACHE_FILE = "seen_articles.json"
DAYS_LIMIT = 30

def fetch_articles():
    res = requests.get(BASE_URL)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    blocks = soup.select("div.sd.text.sd.appear")
    seen = set()
    articles = []

    for block in blocks:
        text = block.get_text(strip=True)
        if not text or len(text) < 10 or text in seen:
            continue
        seen.add(text)

        guid = hashlib.md5(text.encode("utf-8")).hexdigest()
        articles.append({
            "title": text[:40] + "…" if len(text) > 40 else text,
            "description": text,
            "guid": guid,
            "pubDate": datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "link": BASE_URL
        })

    return articles

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def generate_rss():
    cache = load_cache()
    all_articles = fetch_articles()

    new_articles = []
    now = datetime.datetime.utcnow()

    for article in all_articles:
        guid = article["guid"]
        if guid not in cache:
            # 新規記事をキャッシュに追加
            cache[guid] = article["timestamp"]
            new_articles.append(article)
        else:
            # 30日以内なら対象とする
            ts = datetime.datetime.fromisoformat(cache[guid])
            if (now - ts).days <= DAYS_LIMIT:
                new_articles.append(article)

    # 新規が0なら初回用として全量出力
    output_articles = new_articles if new_articles else all_articles

    rss_items = ""
    for article in output_articles:
        rss_items += f"""
        <item>
            <title>{article['title']}</title>
            <link>{article['link']}</link>
            <guid isPermaLink="false">{article['guid']}</guid>
            <pubDate>{article['pubDate']}</pubDate>
            <description>{article['description']}</description>
        </item>
        """

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

    save_cache(cache)

if __name__ == "__main__":
    generate_rss()
