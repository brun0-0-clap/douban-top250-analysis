# -*- coding: utf-8 -*-
"""
第 3 步：画图

用法：py plot.py
运行完会生成 4 张图：
  chart_genre.png    类型分布 Top10
  chart_decade.png   年代分布
  chart_country.png  国家/地区分布 Top8
  chart_rating.png   评分分布
"""
import matplotlib
matplotlib.use("Agg")           # 不弹窗口，直接把图存成文件

import matplotlib.pyplot as plt
import pandas as pd

# 让图里能显示中文（Windows 一定有「微软雅黑」）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#4C78A8"
ORANGE = "#F58518"
GREEN = "#54A24B"


def load():
    clean = pd.read_csv("douban_clean.csv")
    decade = pd.read_csv("decade_count.csv")
    country = pd.read_csv("country_count.csv")
    genre = pd.read_csv("genre_count.csv")

    for d in (decade, country, genre):
        type_col = d.columns[1]
        d[type_col] = pd.to_numeric(d[type_col], errors="coerce").fillna(0).astype(int)
    clean["评分"] = pd.to_numeric(clean["评分"], errors="coerce")
    return clean, decade, country, genre


def chart_genre(genre):
    top = genre.head(10).iloc[::-1]          # 倒过来，让最多的排最上面
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(top["类型"], top["数量"], color=ORANGE, height=0.6)
    ax.set_title("豆瓣 Top250 电影类型分布 Top10", fontsize=13)
    ax.set_xlabel("影片数量")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for b, v in zip(bars, top["数量"]):
        ax.text(v, b.get_y() + b.get_height() / 2, " " + str(v),
                va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("chart_genre.png", dpi=150)
    plt.close()
    print("已生成 chart_genre.png")


def chart_decade(decade):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(decade["年代"], decade["数量"], color=BLUE, width=0.6)
    ax.set_title("豆瓣 Top250 电影年代分布", fontsize=13)
    ax.set_ylabel("影片数量")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for b, v in zip(bars, decade["数量"]):
        ax.text(b.get_x() + b.get_width() / 2, v, str(v),
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig("chart_decade.png", dpi=150)
    plt.close()
    print("已生成 chart_decade.png")


def chart_country(country):
    top = country.head(8)
    others = country["数量"].sum() - top["数量"].sum()
    labels = list(top["国家"]) + ["其他"]
    values = list(top["数量"]) + [others]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90,
           colors=plt.cm.Paired.colors[:len(values)])
    ax.set_title("豆瓣 Top250 国家/地区分布", fontsize=13)
    plt.tight_layout()
    plt.savefig("chart_country.png", dpi=150)
    plt.close()
    print("已生成 chart_country.png")


def chart_rating(clean):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(clean["评分"], bins=15, color=GREEN, edgecolor="white")
    ax.set_title("豆瓣 Top250 评分分布", fontsize=13)
    ax.set_xlabel("评分")
    ax.set_ylabel("影片数量")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig("chart_rating.png", dpi=150)
    plt.close()
    print("已生成 chart_rating.png")


if __name__ == "__main__":
    clean_df, decade_df, country_df, genre_df = load()
    chart_genre(genre_df)
    chart_decade(decade_df)
    chart_country(country_df)
    chart_rating(clean_df)
