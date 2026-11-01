"""그래프 12: 2장 보완 — 작품별 주간 시청률과 주간 화제성(라코이 버즈)
그래프 03의 순위 뒤에 있는 실제 흐름을 작품마다 보여 준다. 먼저 ch1_curves.py, ch2_gap.py를 실행해 둘 것"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

tv = pd.read_csv("data/processed/tv_weekly.csv")
rc = pd.read_csv("data/processed/racoi_weekly.csv")
gap = pd.read_csv("data/processed/ch2_gap.csv", index_col=0).sort_values("시청률")   # 시청률 1위부터

TV_C, BUZZ_C, INK, MUTED, UP, DOWN = "#2a78d6", "#9fd8bf", "#2b2b2b", "#8a8a85", "#2a78d6", "#eb6834"
fig, axes = plt.subplots(2, 5, figsize=(17, 7.6))
for ax, (title, g) in zip(axes.flat, gap.iterrows()):
    b = rc[rc["title"] == title].set_index("week_no")["buzz"]
    t = tv[tv["title"] == title].set_index("week_no")["rating"]
    ax.bar(b.index, b.values, color=BUZZ_C, width=0.7, zorder=2)              # 막대 = 주간 화제성
    top = b.max()
    if top > 3 * b.median():                      # 한 주 급등(신이랑 6주차)이 다른 주를 납작하게 만들지 않게 축을 자름
        top = b.nlargest(2).iloc[-1] * 1.6
        w = b.idxmax()
        ax.text(w, top * 0.97, f"{int(b.max()):,}↑\n댓글만 급등\n(4-2)", ha="center", va="top",
                fontsize=7, color=INK, zorder=4, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    ax.set_ylim(0, top * 1.25 if top == b.max() else top)
    ax.ticklabel_format(axis="y", style="plain")
    ax.tick_params(axis="y", labelsize=7, colors="#4f9c7a")
    ax2 = ax.twinx()
    ax2.plot(t.index, t.values, color=TV_C, lw=2.2, marker="o", ms=4, zorder=3)  # 선 = 주간 시청률
    ax2.set_ylim(0, t.max() * 1.3)
    ax2.tick_params(axis="y", labelsize=7, colors=TV_C)
    ax.set_xticks(range(1, int(max(b.index.max(), t.index.max())) + 1))
    ax.tick_params(axis="x", labelsize=7, colors=MUTED)
    for a in (ax, ax2):
        a.spines["top"].set_visible(False)
    k = int(g["갭"])
    color = UP if k >= 3 else DOWN if k <= -3 else INK
    name = title if len(title) <= 10 else title[:9] + "…"
    ax.set_title(f"{name}\n시청률 {int(g['시청률'])}위 · 화제성 {int(g['라코이_버즈'])}위 (갭 {k:+d})",
                 fontsize=10, color=color, loc="left")
fig.supxlabel("방영 주차", fontsize=9, color=MUTED)
fig.suptitle("그래프 12. 작품별 주간 시청률(선)과 주간 화제성(막대) — 그래프 03 순위의 실제 흐름",
             x=0.01, ha="left", fontsize=14, color=INK)
fig.text(0.01, 0.925, "막대 = 라코이 시청자 버즈(게시글+댓글, 건, 왼쪽 축)  ·  선 = 주간 평균 시청률(%, 오른쪽 축)  ·  "
         "축 눈금은 작품마다 다르므로 칸끼리는 크기가 아니라 모양을 비교한다(신이랑 6주차 막대는 위가 잘림).  순위는 시청률 = 회차 평균, 화제성 = 방영 주 중앙값.\n"
         "파란 제목 = 시청률보다 화제성 순위가 3계단 이상 높은 작품, 주황 제목 = 3계단 이상 낮은 작품.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.80, bottom=0.08, left=0.03, right=0.97, hspace=0.62, wspace=0.42)
fig.savefig("images/12_gap_weekly.png", dpi=150)
print("저장: images/12_gap_weekly.png")
