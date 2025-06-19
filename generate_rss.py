import requests
from bs4 import BeautifulSoup

url = "https://pitmc.go.jp/"
res = requests.get(url)
res.encoding = res.apparent_encoding
soup = BeautifulSoup(res.text, "html.parser")

print("=== タグとクラスの一覧 ===\n")

# 出現頻度が高そうなタグを対象にする
target_tags = ["div", "section", "h1", "h2", "h3", "p", "a", "ul", "li", "span"]

for tag in target_tags:
    elements = soup.find_all(tag)
    print(f"\n▼ <{tag}> タグ（{len(elements)}件）")
    for i, el in enumerate(elements[:10]):  # 多すぎるときは最初の10件のみ表示
        classes = el.get("class")
        text = el.get_text(strip=True)
        print(f"  [{i+1}] class={classes} text='{text[:60]}{'…' if len(text) > 60 else ''}'")
