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

import requests
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

def fetch_github_stats(username="inigo99"):
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token: headers["Authorization"] = f"token {token}"
    try:
        user_res = requests.get(f"https://api.github.com/users/{username}", headers=headers)
        repos_res = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        if user_res.status_code == 200 and repos_res.status_code == 200:
            repos_data = repos_res.json()
            
            # Actualizar stats.json
            stats_path = os.path.join(HERE, "stats.json")
            with open(stats_path, "r") as f: stats = json.load(f)
            stats["public_repos"] = user_res.json().get("public_repos", stats.get("public_repos", 0))
            stats["followers"] = user_res.json().get("followers", stats.get("followers", 0))
            stats["stars"] = sum(r.get("stargazers_count", 0) for r in repos_data)
            with open(stats_path, "w") as f: json.dump(stats, f, indent=2)
            
            # Actualizar langmix.json
            langs = {}
            for r in repos_data:
                if not r.get("fork"):
                    l_res = requests.get(r["languages_url"], headers=headers)
                    if l_res.status_code == 200:
                        for lang, bytes_cnt in l_res.json().items():
                            langs[lang] = langs.get(lang, 0) + bytes_cnt

            # Ajuste manual para Jupyter Notebook, el output era grande y altereba la cifra real
            if 'Jupyter Notebook' in langs: langs['Jupyter Notebook'] = 230400

            total = sum(langs.values())
            if total > 0:
                sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
                top = {k: int(v / total * 100) for k, v in sorted_langs[:4]}
                top["Other"] = max(0, 100 - sum(top.values()))
                langmix_path = os.path.join(HERE, "langmix.json")
                with open(langmix_path, "r") as f: langmix = json.load(f)
                langmix["bars"] = top
                with open(langmix_path, "w") as f: json.dump(langmix, f, indent=2)
                
            print("Estadísticas y lenguajes actualizados correctamente.")
    except Exception as e:
        print(f"Error actualizando datos de la API: {e}")

def main():
    fetch_github_stats("inigo99")
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
