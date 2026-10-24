# -*- coding: utf-8 -*-
"""
第 2 步：清洗 + 统计

用法：py analyze.py
输入：douban_raw.csv
输出：douban_clean.csv、decade_count.csv、country_count.csv、genre_count.csv

做了什么：
  1. 评分、评价人数、年份 从"文字"转成"数字"
  2. 类型字段是「犯罪 剧情」这种多个类型，拆开分别统计
  3. 统计：年代分布、国家分布、类型分布
"""
import collections

import pandas as pd

IN_FILE = "douban_raw.csv"


def main():
    df = pd.read_csv(IN_FILE)
    print("原始数据：%d 行" % len(df))

    # ---------- 清洗 ----------
    df = df.dropna(subset=["片名"])
    df["片名"] = df["片名"].astype(str).str.strip()
    df = df[df["片名"] != ""]
    before = len(df)
    df = df.drop_duplicates(subset=["片名"])
    print("去掉重复后：%d 行（删掉 %d 行）" % (len(df), before - len(df)))

    # 转数字：转不了的会变成 NaN，用 dropna 丢掉
    df["评分"] = pd.to_numeric(df["评分"], errors="coerce")
    df["评价人数"] = pd.to_numeric(df["评价人数"], errors="coerce")
    df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
    df = df.dropna(subset=["评分", "年份"])
    df["年份"] = df["年份"].astype(int)
    print("转成数字并丢掉无效行后：%d 行" % len(df))

    # 评价人数字段如果有缺失，用 0 填上（不影响统计）
    df["评价人数"] = df["评价人数"].fillna(0).astype("int64")

    # ---------- 构造"年代"字段 ----------
    df["年代"] = (df["年份"] // 10 * 10).astype(str) + "s"

    df.to_csv("douban_clean.csv", index=False, encoding="utf-8-sig")
    print("清洗后的数据已保存到 douban_clean.csv")

    # ---------- 统计年代 ----------
    decade = df["年代"].value_counts().sort_index().reset_index()
    decade.columns = ["年代", "数量"]
    decade.to_csv("decade_count.csv", index=False, encoding="utf-8-sig")

    # ---------- 统计国家（合拍片的国家也要拆开，例如「美国 英国」要各算一次）----------
    country_counter = collections.Counter()
    for text in df["国家"].fillna(""):
        for name in str(text).split():
            name = name.strip()
            if name:
                country_counter[name] += 1
    country_count = pd.DataFrame(country_counter.most_common(), columns=["国家", "数量"])
    country_count.to_csv("country_count.csv", index=False, encoding="utf-8-sig")

    # ---------- 统计类型（一个电影可能有多个类型，要拆开） ----------
    counter = collections.Counter()
    for text in df["类型"].fillna(""):
        for g in str(text).split():
            g = g.strip()
            if g:
                counter[g] += 1
    genre_df = pd.DataFrame(counter.most_common(), columns=["类型", "数量"])
    genre_df.to_csv("genre_count.csv", index=False, encoding="utf-8-sig")

    # ---------- 打印结论 ----------
    print()
    print("=== 年代分布 ===")
    print(decade.to_string(index=False))
    print()
    print("=== 国家分布 Top8 ===")
    print(country_count.head(8).to_string(index=False))
    print()
    print("=== 类型分布 Top10 ===")
    print(genre_df.head(10).to_string(index=False))
    print()
    print("=== 评分最高的 5 部 ===")
    print(df.nlargest(5, "评分")[["片名", "评分", "年份"]].to_string(index=False))
    print()
    print("平均评分：%.2f" % df["评分"].mean())


if __name__ == "__main__":
    main()
