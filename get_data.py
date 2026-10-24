# -*- coding: utf-8 -*-
"""抓取豆瓣电影 Top250 榜单，输出 douban_raw.csv"""

import csv
import re
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://movie.douban.com/top250"
PAGE_SIZE = 25
TOTAL = 250
DELAY = 3
OUT_FILE = "douban_raw.csv"
FIELDS = ["排名", "片名", "评分", "评价人数", "年份", "国家", "类型"]


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    movies = []

    for item in soup.select("div.item"):
        em = item.select_one("em")
        title = item.select_one("span.title")
        rating = item.select_one("span.rating_num")

        # 评价人数所在节点没有 class，直接从条目文本里正则提取
        people = re.search(r"(\d+)人评价", item.get_text(" ", strip=True))

        year = country = genre = ""
        info = item.select_one("div.bd p")
        if info:
            lines = re.split(r"<br\s*/?>", info.decode_contents())
            texts = [BeautifulSoup(x, "html.parser").get_text(" ", strip=True)
                     for x in lines]
            texts = [t for t in texts if t]
            # 末行格式：1994 / 美国 / 犯罪 剧情
            if texts:
                parts = [p.strip() for p in texts[-1].split("/")]
                if len(parts) >= 3:
                    ym = re.search(r"\d{4}", parts[0])
                    year = ym.group() if ym else parts[0]
                    country = parts[1]
                    genre = parts[2]

        movies.append({
            "排名": em.get_text(strip=True) if em else "",
            "片名": title.get_text(strip=True) if title else "",
            "评分": rating.get_text(strip=True) if rating else "",
            "评价人数": people.group(1) if people else "",
            "年份": year,
            "国家": country,
            "类型": genre,
        })

    return movies


def main():
    movies = []

    for start in range(0, TOTAL, PAGE_SIZE):
        url = "%s?start=%d&filter=" % (BASE_URL, start)
        page = start // PAGE_SIZE + 1
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            movies.extend(parse_page(resp.text))
            print("第 %d 页，累计 %d 条" % (page, len(movies)))
        except Exception as exc:
            print("第 %d 页失败：%s" % (page, exc))
        time.sleep(DELAY)

    with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(movies)

    print("共 %d 条，已写入 %s" % (len(movies), OUT_FILE))


if __name__ == "__main__":
    main()
