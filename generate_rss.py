import requests
from bs4 import BeautifulSoup
import datetime
import hashlib

BASE_URL = "https://pitmc.go.jp/"
RSS_FILE = "rss.xml"

def fetch_articles():
    res = requests.get(BASE_URL)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    # ニュースブロックを特定する
    blocks = soup.select("div.sd.appear")

    articles = []
    seen = set()

    for block in blocks:
        h3 = block.find("h3", class_="text sd appear")
        p = block.find("p", class_="text sd appear")

        if h3 and p:
            title = h3.get_text(strip=True)
            description = p.get_text(strip=True)

            if not title or not description:
                continue

            if title in seen:
                continue
            seen.add(title)

            guid = hashlib.md5((title + description).encode("utf-8")).hexdigest()
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
    for article in articles:
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

if __name__ == "__main__":
    generate_rss()
