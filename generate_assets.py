#!/usr/bin/env python3
"""
Generates the static SVG assets for the inigo99/inigo99 profile README:
  assets/banner-dark.svg / banner-light.svg
  assets/radar-dark.svg / radar-light.svg           (self-rated skills)
  assets/radar-langs-dark.svg / radar-langs-light.svg (language mix)
  assets/card-stats-dark.svg / card-stats-light.svg  (GitHub stats card)
  assets/metrics.languages.svg                       (language bar chart)

Data lives in skills.json / langmix.json / stats.json next to this script --
edit those and re-run `python3 generate_assets.py` to redraw everything.
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

THEMES = {
    "dark": dict(bg="#0D1117", card="#161B22", text="#C9D1D9", grid="#30363D", accent="#58A6FF", accent2="#AA9BEF"),
    "light": dict(bg="#FFFFFF", card="#F6F8FA", text="#24292F", grid="#D0D7DE", accent="#0969DA", accent2="#8250DF"),
}


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


# ---------------------------------------------------------------- banner ----
def make_banner(theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(12, 2.4), dpi=200)
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    ax.set_facecolor(t["bg"])

    # terminal window chrome
    ax.add_patch(plt.Rectangle((0.3, 0.3), 11.4, 1.8, facecolor=t["card"], edgecolor=t["grid"], linewidth=1.2, zorder=1))
    for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
        ax.add_patch(plt.Circle((0.65 + i * 0.28, 1.85), 0.07, facecolor=c, edgecolor="none", zorder=2))

    mono = {"family": "monospace"}
    ax.text(0.55, 1.45, ">>> print(f\"Hi, I'm Íñigo\")", fontsize=15, color=t["accent"], fontdict=mono, va="center")
    ax.text(0.55, 1.08, "AI / ML Engineer  ·  Full Stack Developer", fontsize=13.5, color=t["text"], fontdict=mono, va="center")
    ax.text(0.55, 0.70, "Currently open to GenAI / ML / Data Science / Full Stack roles", fontsize=11, color=t["accent2"], fontdict=mono, va="center")

    fig.savefig(os.path.join(OUT, f"banner-{theme}.svg"), transparent=False)
    plt.close(fig)


# ----------------------------------------------------------------- radar ----
def make_radar(data, out_name, theme, title):
    t = THEMES[theme]
    labels = list(data.keys())
    values = list(data.values())
    n = len(labels)
    angles = [i / n * 2 * math.pi for i in range(n)]
    values_c = values + values[:1]
    angles_c = angles + angles[:1]

    fig = plt.figure(figsize=(4.6, 4.2), dpi=200)
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor(t["bg"])

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=t["text"], fontsize=10)
    ax.set_rlabel_position(0)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], color=t["grid"], fontsize=7)
    ax.set_ylim(0, 10)
    ax.spines["polar"].set_color(t["grid"])
    ax.grid(color=t["grid"], linewidth=0.8)

    ax.plot(angles_c, values_c, color=t["accent"], linewidth=2)
    ax.fill(angles_c, values_c, color=t["accent"], alpha=0.28)

    ax.set_title(title, color=t["text"], fontsize=12, pad=18, fontweight="bold")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, out_name), transparent=False)
    plt.close(fig)


# ------------------------------------------------------------ stats card ----
def make_stats_card(stats, theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(5.4, 2.2), dpi=200)
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 5.4)
    ax.set_ylim(0, 2.2)
    ax.axis("off")

    ax.add_patch(plt.Rectangle((0.15, 0.15), 5.1, 1.9, facecolor=t["card"], edgecolor=t["grid"], linewidth=1.2))
    ax.text(0.4, 1.75, "Íñigo's GitHub stats", fontsize=13, color=t["text"], fontweight="bold", va="center")

    items = [
        ("Public repos", stats["public_repos"]),
        ("Stars", stats["stars"]),
        ("Followers", stats["followers"]),
        ("Contribs (1y)", stats["contributions_last_year"]),
    ]
    col_w = 5.1 / len(items)
    for i, (label, val) in enumerate(items):
        cx = 0.4 + col_w * i + col_w / 2 - 0.15
        ax.text(cx, 1.0, str(val), fontsize=20, color=t["accent"], fontweight="bold", ha="center", va="center")
        ax.text(cx, 0.55, label, fontsize=9, color=t["text"], ha="center", va="center")

    fig.savefig(os.path.join(OUT, f"card-stats-{theme}.svg"), transparent=False)
    plt.close(fig)


# --------------------------------------------------------- language bars ----
def make_lang_bars(bars, theme):
    t = THEMES[theme]
    labels = list(bars.keys())
    values = list(bars.values())
    colors = [t["accent"], t["accent2"], "#3572A5", "#F1E05A", t["grid"]]

    fig = plt.figure(figsize=(6.2, 2.6), dpi=200)
    fig.patch.set_facecolor(t["bg"])
    ax = fig.add_axes([0.28, 0.08, 0.68, 0.86])
    ax.set_facecolor(t["bg"])

    y = np.arange(len(labels))[::-1]
    ax.barh(y, values, color=colors[: len(values)], height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, color=t["text"], fontsize=10)
    ax.set_xlim(0, max(values) * 1.25)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    for yi, v in zip(y, values):
        ax.text(v + 1, yi, f"{v}%", va="center", color=t["text"], fontsize=9)

    fig.savefig(os.path.join(OUT, "metrics.languages.svg"), transparent=False)
    plt.close(fig)


def main():
    skills = load("skills.json")["skills"]
    langmix = load("langmix.json")
    stats = load("stats.json")

    for theme in ("dark", "light"):
        make_banner(theme)
        make_radar(skills, f"radar-{theme}.svg", theme, "Self-rated skills")
        make_radar(langmix["radar"], f"radar-langs-{theme}.svg", theme, "Language mix")
        make_stats_card(stats, theme)

    # single themed version is enough for the language bar chart
    make_lang_bars(langmix["bars"], "dark")

    print("Assets written to", OUT)


if __name__ == "__main__":
    main()
