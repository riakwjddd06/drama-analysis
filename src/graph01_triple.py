"""그래프 01: 유형별 대표작의 TV 시청률 · 넷플릭스 한국 순위 · 라코이 화제성 3단 그래프
1장의 네 유형마다, 9가지 기준 모두에서 유형이 바뀌지 않은(9/9) 작품을 대표작으로 골랐다.
먼저 ch1_curves.py, load_racoi.py를 실행해 둘 것"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

# 대표작 → 저장 파일 (01 = TV 뒷심형, 01b~01d = 나머지 세 유형)
REPS = {
    "은애하는 도적님아": "images/01_triple_curve.png",
    "언더커버 미쓰홍": "images/01b_triple_undercover.png",
    "샤이닝": "images/01c_triple_shining.png",
    "신이랑 법률사무소": "images/01d_triple_phantom.png",
}
NOTES = {"신이랑 법률사무소": "6주차는 댓글만 급등한 주(REPORT 4-2). 이 주를 빼면 최고는 2주차"}   # 해석에 주의할 점

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"]).set_index("title")
types = pd.read_csv("data/processed/ch1_types.csv").set_index("title")
tv = pd.read_csv("data/processed/tv_weekly.csv")
nf = pd.read_csv("data/processed/nf_kr_weekly.csv")
rc = pd.read_csv("data/processed/racoi_weekly.csv")
TV_C, NF_C, G_C, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#2b2b2b", "#8a8a85"


def draw(rep, path, num):
    t = tv[tv["title"] == rep].set_index("week_no")["rating"]
    n = nf[nf["title"] == rep].set_index("week_no")["weekly_rank"]
    g = rc[rc["title"] == rep].set_index("week_no")["buzz"]          # 라코이 주간 게시글+댓글 (방영 주만)
    last = int(t.index.max())
    weeks = range(-1, last + 4)                                       # 방영 2주 전 ~ 종영 3주 뒤
    t, n, g = t.reindex(weeks), n.reindex(weeks), g.reindex(weeks)

    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    panels = [
        (axes[0], t, TV_C, "TV 시청률 (%)\n주차 평균, 닐슨 전국", t.idxmax(), "최고"),
        (axes[1], n, NF_C, "넷플릭스 한국 순위\n(위가 1위, 끊긴 곳은 TOP 10 밖)", n.idxmin() if n.notna().any() else None, "최고 순위"),
        (axes[2], g, G_C, "라코이 화제성\n(주간 게시글+댓글, 건)", g.idxmax(), "최고"),
    ]
    for ax, s, color, label, peak, word in panels:
        ax.plot(s.index, s.values, color=color, lw=2.2, marker="o", ms=5)
        if peak is not None:
            ax.plot(peak, s[peak], "o", ms=11, mfc="white", mec=color, mew=2.2)
            ax.annotate(f"{word}: {peak}주차", (peak, s[peak]), xytext=(8, 8), textcoords="offset points",
                        fontsize=9, color=INK)
        ax.set_ylabel(label, fontsize=9, color=INK)
        ax.margins(y=0.18)
        ax.axvspan(0.5, last + 0.5, color="#f3f3f0", lw=0, zorder=0)   # 방영 기간
        ax.tick_params(labelsize=8, colors=MUTED)
        ax.grid(axis="y", color="#e6e6e3", lw=0.6)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[1].set_ylim(10.5, 0.5)
    axes[1].set_yticks([1, 3, 5, 7, 10])
    axes[2].set_ylim(bottom=0)
    axes[2].set_xticks(list(weeks))
    axes[2].set_xlabel("방영 주차 (1화가 들어 있는 월~일 = 1주차, 회색 = 방영 기간)", fontsize=9, color=MUTED)
    if rep in NOTES:
        axes[2].text(0.99, 0.95, NOTES[rep], transform=axes[2].transAxes, ha="right", va="top", fontsize=9, color=MUTED)

    ty = types.loc[rep]
    fig.suptitle(f"그래프 {num}. {rep} ({ty['quadrant']}) — 같은 드라마, 세 지표의 정점 시기",
                 x=0.02, ha="left", fontsize=14, color=INK)
    fig.text(0.02, 0.945,
             f"유형: TV {ty['tv_type']} · 넷플릭스 {ty['nf_type']} (9가지 기준 중 {ty['sensitivity']} 같은 유형).  "
             "순위와 시청률·화제성은 단위가 달라 곡선의 형태(오르내리는 시점)만 비교한다.\n"
             "x축(방영 주차)만 공유하는 3단 그래프다. 세 지표 모두 주 단위(월~일)이며, 라코이는 방영 주만 집계한다.",
             fontsize=9, color=MUTED, va="top")
    fig.subplots_adjust(top=0.87, bottom=0.07, left=0.16, right=0.97, hspace=0.18)
    fig.savefig(path, dpi=150)
    print(f"저장: {path}  |  정점 주차 — TV {t.idxmax()}, 넷플릭스 {n.idxmin()}, 라코이 {g.idxmax()}")


for (rep, path), num in zip(REPS.items(), ["01", "01-B", "01-C", "01-D"]):
    draw(rep, path, num)
