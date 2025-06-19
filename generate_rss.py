import requests
from bs4 import BeautifulSoup
import datetime

BASE_URL = "https://pitmc.go.jp/"
NEWS_PATH = "/news"  # 実際のニュース一覧パスが分かれば正確に指定

def fetch_news():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 適宜変更：ニュースリンクのセレクタ特定が必要
    articles = soup.find_all("a", string=lambda s: s and "NEWS" in s)[:10]

    rss_items = ""
    for a in articles:
        title = a.text.strip()
        link = BASE_URL + a.get('href').lstrip('/')
        pub_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid>{link}</guid>
            <pubDate>{pub_date}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>J-RISE NEWS</title>
            <link>{BASE_URL}</link>
            <description>J-RISE Initiative公式のニュースフィード</description>
            {rss_items}
        </channel>
    </rss>
    """

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(rss)

if __name__ == "__main__":
    fetch_news()
