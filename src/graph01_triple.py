"""그래프 01: 대표작 1편의 TV 시청률 · 넷플릭스 한국 순위 · 구글 검색 관심도 3단 그래프"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

REP = "은애하는 도적님아"          # 대표작 (I1의 TV 뒷심형 사례)

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"]).set_index("title")
tv = pd.read_csv("data/processed/tv_weekly.csv")
nf = pd.read_csv("data/processed/nf_kr_weekly.csv")
g = pd.read_csv("data/processed/google_kr_daily.csv", parse_dates=["date"])

d = dramas.loc[REP]
first_monday = d["first_air"] - pd.Timedelta(days=d["first_air"].weekday())

# 구글 일별 → 방영 주차(월~일) 평균. 1화가 들어 있는 주 = 1주차
gs = g[g["title"] == REP].copy()
gs["week_no"] = (gs["date"] - first_monday).dt.days // 7 + 1
g_week = gs.groupby("week_no")["value_shape"].mean()

t = tv[tv["title"] == REP].set_index("week_no")["rating"]
n = nf[nf["title"] == REP].set_index("week_no")["weekly_rank"]
last = int(t.index.max())
weeks = range(-1, last + 4)                       # 방영 2주 전 ~ 종영 3주 뒤
t, n, g_week = t.reindex(weeks), n.reindex(weeks), g_week.reindex(weeks)

TV_C, NF_C, G_C, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#2b2b2b", "#8a8a85"
fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
panels = [
    (axes[0], t, TV_C, "TV 시청률 (%)\n주차 평균, 닐슨 전국", t.idxmax(), "최고"),
    (axes[1], n, NF_C, "넷플릭스 한국 순위\n(위가 1위, 끊긴 곳은 TOP 10 밖)", n.idxmin() if n.notna().any() else None, "최고 순위"),
    (axes[2], g_week, G_C, "구글 검색 관심도\n(주 평균, 최고 날 = 100)", g_week.idxmax(), "최고"),
]
for ax, s, color, label, peak, word in panels:
    ax.plot(s.index, s.values, color=color, lw=2.2, marker="o", ms=5)
    if peak is not None:
        ax.plot(peak, s[peak], "o", ms=11, mfc="white", mec=color, mew=2.2)
        ax.annotate(f"{word}: {peak}주차", (peak, s[peak]), xytext=(8, 8), textcoords="offset points",
                    fontsize=9, color=INK)
    ax.set_ylabel(label, fontsize=9, color=INK)
    ax.margins(y=0.18)
    ax.axvspan(0.5, last + 0.5, color="#f3f3f0", lw=0, zorder=0)       # 방영 기간
    ax.tick_params(labelsize=8, colors=MUTED)
    ax.grid(axis="y", color="#e6e6e3", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axes[1].set_ylim(10.5, 0.5)
axes[1].set_yticks([1, 3, 5, 7, 10])
axes[2].set_ylim(bottom=0)
axes[2].set_xticks(list(weeks))
axes[2].set_xlabel("방영 주차 (1화가 들어 있는 월~일 = 1주차, 회색 = 방영 기간)", fontsize=9, color=MUTED)

fig.suptitle(f"그래프 01. {REP} — 같은 드라마, 세 지표의 정점 시기", x=0.02, ha="left", fontsize=14, color=INK)
fig.text(0.02, 0.945, "순위(서열)와 시청률·검색량(연속 수치)은 직접 비교할 수 없어, 절대 수치가 아니라 곡선의 형태(오르내리는 시점)를 비교한다.\n"
         "이중 y축 대신 x축(방영 주차)만 공유하는 3단 그래프로 그렸다. 넷플릭스가 주간 데이터라 주 단위로 맞췄다.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.87, bottom=0.07, left=0.16, right=0.97, hspace=0.18)
fig.savefig("images/01_triple_curve.png", dpi=150)
print("저장: images/01_triple_curve.png")
print(pd.DataFrame({"TV 시청률": t, "넷플릭스 순위": n, "구글 검색(주 평균)": g_week.round(1)}).to_string())