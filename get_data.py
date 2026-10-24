# -*- coding: utf-8 -*-
"""
第 1 步：抓取豆瓣电影 Top250

用法（在终端里）：py get_data.py
输出文件：douban_raw.csv（250 行，每行一部电影）

只需要看懂三件事：
  1. requests.get(url, headers=...)     把网页下载下来
  2. BeautifulSoup(html, "html.parser") 把网页变成能查找的结构
  3. soup.select("div.item")            找到页面上所有"电影条目"
"""
import csv
import re
import time

import requests
from bs4 import BeautifulSoup

# 假装自己是浏览器，否则网站会拒绝你
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

OUT_FILE = "douban_raw.csv"
SLEEP = 3.0        # 每翻一页休息 3 秒，别把人家服务器打爆
FIELDS = ["排名", "片名", "评分", "评价人数", "年份", "国家", "类型"]


def parse_page(html):
    """从一页 HTML 里解析出所有电影。"""
    soup = BeautifulSoup(html, "html.parser")
    movies = []

    for item in soup.select("div.item"):
        # ---- 排名 ----
        em = item.select_one("em")
        rank = em.get_text(strip=True) if em else ""

        # ---- 片名 ----
        title_tag = item.select_one("span.title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # ---- 评分 ----
        rating_tag = item.select_one("span.rating_num")
        rating = rating_tag.get_text(strip=True) if rating_tag else ""

        # ---- 评价人数：在整条目的文字里用正则找「1234567人评价」 ----
        # 注意：豆瓣改过版，评价人数所在的那个 <span> 没有 class，
        # 靠选择器定位会拿不到（旧版的 div.star 已经不存在了），
        # 所以直接在整段文字里用正则匹配最稳。
        people = ""
        m = re.search(r"(\d+)人评价", item.get_text(" ", strip=True))
        if m:
            people = m.group(1)

        # ---- 年份 / 国家 / 类型：在 <p> 里的第二行，形如「1994 / 美国 / 犯罪 剧情」----
        year = country = genre = ""
        info_p = item.select_one("div.bd p")
        if info_p:
            raw = info_p.decode_contents()
            lines = re.split(r"<br\s*/?>", raw)
            texts = [BeautifulSoup(x, "html.parser").get_text(" ", strip=True)
                     for x in lines]
            texts = [t for t in texts if t]
            if texts:
                tail = texts[-1]           # 最后一行才是 年份/国家/类型
                parts = [p.strip() for p in tail.split("/")]
                if len(parts) >= 3:
                    ym = re.search(r"(\d{4})", parts[0])
                    year = ym.group(1) if ym else parts[0]
                    country = parts[1]
                    genre = parts[2]

        movies.append({
            "排名": rank,
            "片名": title,
            "评分": rating,
            "评价人数": people,
            "年份": year,
            "国家": country,
            "类型": genre,
        })

    return movies


def crawl():
    all_movies = []
    for start in range(0, 250, 25):      # 每页 25 部，一共 10 页
        url = "https://movie.douban.com/top250?start=%d&filter=" % start
        print("正在抓第 %d 页 ..." % (start // 25 + 1))
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except Exception as exc:
            print("  这一页失败了（%s），跳过，稍后可以重跑" % type(exc).__name__)
            time.sleep(SLEEP)
            continue

        movies = parse_page(resp.text)
        if not movies:
            print("  !! 这一页没解析出数据，可能页面结构变了，或被网站拦了")
        all_movies.extend(movies)
        print("  本页 %d 部，累计 %d 部" % (len(movies), len(all_movies)))
        time.sleep(SLEEP)

    with open(OUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_movies)

    print("完成，共 %d 部电影，已保存到 %s" % (len(all_movies), OUT_FILE))
    return all_movies


if __name__ == "__main__":
    crawl()
