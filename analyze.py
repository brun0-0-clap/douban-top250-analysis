# -*- coding: utf-8 -*-
"""清洗豆瓣 Top250 数据，统计年代、国家、类型分布"""

import collections

import pandas as pd

IN_FILE = "douban_raw.csv"


def main():
    df = pd.read_csv(IN_FILE)
    print("原始数据：%d 行" % len(df))

    df = df.dropna(subset=["片名"])
    df["片名"] = df["片名"].astype(str).str.strip()
    df = df[df["片名"] != ""].drop_duplicates(subset=["片名"])

    # 抓下来的都是文本，转成数值才能统计
    for col in ["评分", "评价人数", "年份"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["评分", "年份"]).copy()
    df["年份"] = df["年份"].astype(int)
    df["评价人数"] = df["评价人数"].fillna(0).astype("int64")
    df["年代"] = (df["年份"] // 10 * 10).astype(str) + "s"

    df.to_csv("douban_clean.csv", index=False, encoding="utf-8-sig")

    decade = df["年代"].value_counts().sort_index().reset_index()
    decade.columns = ["年代", "数量"]
    decade.to_csv("decade_count.csv", index=False, encoding="utf-8-sig")

    # 合拍片的国家是多值（如 "英国 美国"），拆开逐个计数
    country = collections.Counter()
    for text in df["国家"].fillna(""):
        country.update(str(text).split())
    country_df = pd.DataFrame(country.most_common(), columns=["国家", "数量"])
    country_df.to_csv("country_count.csv", index=False, encoding="utf-8-sig")

    genre = collections.Counter()
    for text in df["类型"].fillna(""):
        genre.update(str(text).split())
    genre_df = pd.DataFrame(genre.most_common(), columns=["类型", "数量"])
    genre_df.to_csv("genre_count.csv", index=False, encoding="utf-8-sig")

    print("清洗后 %d 行，平均评分 %.2f" % (len(df), df["评分"].mean()))
    print(decade.to_string(index=False))
    print(country_df.head(8).to_string(index=False))
    print(genre_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
