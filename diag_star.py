# -*- coding: utf-8 -*-
"""
诊断脚本：评价人数为什么没抓到。

用法：py diag_star.py
它只抓第 1 页，然后打印第一个电影条目里所有 span 的文字，
用来确认「XXX人评价」这段文字到底在哪个标签里。

跑完把终端输出的内容截图发我。
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

resp = requests.get("https://movie.douban.com/top250?start=0&filter=",
                    headers=HEADERS, timeout=20)
print("状态码:", resp.status_code, " 网页长度:", len(resp.text))
print()

soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("div.item")
print("解析到条目数:", len(items))
print()

item = items[0]
star = item.select_one("div.star")
print("=== div.star 是否存在 ===")
print(star is not None)
if star is not None:
    print("div.star 的内部 HTML：")
    print(star.decode_contents())
print()

print("=== 这个条目里所有 span 的文字 ===")
for i, s in enumerate(item.find_all("span"), 1):
    cls = " ".join(s.get("class") or [])
    print("%2d. [class=%s] %s" % (i, cls, s.get_text(strip=True)))
print()

full_text = item.get_text(" ", strip=True)
print("=== 整条目文字里有没有「人评价」三个字 ===")
print("有" if "人评价" in full_text else "没有")
print()
print("=== 条目开头 300 字 ===")
print(full_text[:300])
