# -*- coding: utf-8 -*-
"""排查解析失败用的临时脚本：打印一条电影记录里所有 span 的文本"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

url = "https://movie.douban.com/top250?start=0&filter="
resp = requests.get(url, headers=HEADERS, timeout=20)
print("状态码:", resp.status_code, "长度:", len(resp.text))

soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("div.item")
print("条目数:", len(items))

item = items[0]
for i, s in enumerate(item.find_all("span"), 1):
    print("%2d. [class=%s] %s" % (i, " ".join(s.get("class") or []),
                                  s.get_text(strip=True)))

print("含『人评价』:", "人评价" in item.get_text(" ", strip=True))
