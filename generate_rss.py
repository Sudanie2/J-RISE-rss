import requests
from bs4 import BeautifulSoup
import datetime
import hashlib

BASE_URL = "https://pitmc.go.jp/"
RSS_FILE = "rss.xml"

def generate_rss():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    blocks = soup.select("div.sd.text.sd.appear")

    items = ""
    for block in blocks:
        text = block.get_text(strip=True)
        if not text or len(text) < 10:
            continue

        guid = hashlib.md5(text.encode("utf-8")).hexdigest()
        title = text[:40] + "…" if len(text) > 40 else text
        pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        items += f"""
        <item>
            <title>{title}</title>
            <link>{BASE_URL}</link>
            <guid isPermaLink="false">{guid}</guid>
            <pubDate>{pub_date}</pubDate>
            <description>{text}</description>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>J-RISE NEWS</title>
    <link>{BASE_URL}</link>
    <description>J-RISE Initiative公式のニュースフィード</description>
    <language>ja</language>
    {items}
  </channel>
</rss>"""

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

if __name__ == "__main__":
    generate_rss()
