"""그래프 07: 트렌드·주간 반복(계절성)·노이즈 확인 — 대표작 일별 검색 + 7일 이동평균, 요일별 평균, 10편 방송일 효과"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

REP = "은애하는 도적님아"
DAYS = ["월", "화", "수", "목", "금", "토", "일"]

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"]).set_index("title")
ratings = pd.read_csv("data/raw/ratings.csv", parse_dates=["air_date"])
g = pd.read_csv("data/processed/google_kr_daily.csv", parse_dates=["date"])

def airing(title):
    d = dramas.loc[title]
    s = g[g["title"] == title].set_index("date")["value_shape"].sort_index()
    return s[d["first_air"]:d["last_air"]]

# ---------- 1. 대표작: 트렌드(7일 이동평균)와 노이즈(이동평균에서 벗어난 정도) ----------
d = dramas.loc[REP]
s = g[g["title"] == REP].set_index("date")["value_shape"].sort_index()
s = s[d["first_air"] - pd.Timedelta(days=14): d["last_air"] + pd.Timedelta(days=21)]
trend = s.rolling(7, min_periods=1, center=True).mean()
air_days = set(ratings.loc[ratings["title"] == REP, "air_date"])
resid = (airing(REP) - trend[d["first_air"]:d["last_air"]])

# ---------- 2. 대표작: 요일별 평균 (방영 기간) ----------
run = airing(REP)
weekday_mean = run.groupby(run.index.weekday).mean().reindex(range(7))
rep_air_wd = {day.weekday() for day in air_days}

# ---------- 3. 10편: 방송일 평균 ÷ 비방송일 평균 ----------
rows = []
for t in dramas.index:
    r = airing(t)
    ad = set(ratings.loc[ratings["title"] == t, "air_date"])
    on, off = r[r.index.isin(ad)].mean(), r[~r.index.isin(ad)].mean()
    low = (r == 0).mean() > 0.4                                    # 방영 중 0인 날 40% 초과 = 저신뢰
    rows.append((t + (" (저신뢰)" if low else ""), on / off if off > 0 else float("nan")))
eff = pd.DataFrame(rows, columns=["title", "배수"]).sort_values("배수")

print(f"[{REP}] 방영 기간 평균 {run.mean():.1f}, 이동평균에서 벗어난 정도(표준편차) {resid.std():.1f}")
print("[요일별 평균]\n", pd.Series(weekday_mean.values, index=DAYS).round(1).to_string())
print("\n[방송일 ÷ 비방송일]\n", eff.round(1).to_string(index=False))
eff.to_csv("data/processed/weekday_effect.csv", index=False)

# ---------- 그래프 ----------
BAR, LINE, AIR, INK, MUTED = "#c9c9c4", "#2a78d6", "#eb6834", "#2b2b2b", "#8a8a85"
fig = plt.figure(figsize=(13, 8.5))
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], width_ratios=[1, 1.25], hspace=0.45, wspace=0.55)
ax1, ax2, ax3 = fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

colors = [AIR if day in air_days else BAR for day in s.index]
ax1.bar(s.index, s.values, color=colors, width=0.8)
ax1.plot(trend.index, trend.values, color=LINE, lw=2.5, label="7일 이동평균 (트렌드)")
ax1.axvspan(d["first_air"], d["last_air"], color="#f3f3f0", lw=0, zorder=0)
ax1.set_title(f"① {REP} 일별 검색 관심도 — 주황 막대 = 방송일, 회색 = 비방송일", loc="left", fontsize=11, color=INK)
ax1.legend(frameon=False, fontsize=9, loc="upper right")
ax1.set_ylabel("검색 관심도\n(최고 날 = 100)", fontsize=9, color=INK)

ax2.bar(DAYS, weekday_mean.values, color=[AIR if i in rep_air_wd else BAR for i in range(7)], width=0.6)
for i, v in enumerate(weekday_mean.values):
    ax2.text(i, v + 1, f"{v:.0f}", ha="center", fontsize=9, color=INK)
ax2.set_title("② 같은 작품, 요일별 평균 (방영 기간)", loc="left", fontsize=11, color=INK)

ax3.barh(eff["title"], eff["배수"], color=LINE, height=0.6)
ax3.axvline(1, color=MUTED, lw=1, ls="--")
for i, v in enumerate(eff["배수"]):
    ax3.text(v + 0.1, i, f"{v:.1f}배", va="center", fontsize=9, color=INK)
ax3.set_title("③ 10편: 방송일 평균 ÷ 비방송일 평균", loc="left", fontsize=11, color=INK)
ax3.set_xlabel("배수 (점선 1배 = 차이 없음)", fontsize=9, color=MUTED)

for ax in (ax1, ax2, ax3):
    ax.tick_params(labelsize=8, colors=MUTED)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
ax1.grid(axis="y", color="#e6e6e3", lw=0.6)
ax3.tick_params(axis="y", labelsize=9, colors=INK)

fig.suptitle("그래프 07. 검색 관심도의 트렌드·주간 반복·노이즈 (구글 트렌드, 대한민국)", x=0.02, ha="left", fontsize=14, color=INK)
fig.text(0.02, 0.945,
         f"트렌드 = 7일 이동평균(가운데 정렬)  ·  주간 반복 = 방송 요일마다 오르는 패턴  ·  노이즈 = 이동평균에서 벗어난 정도(표준편차 {resid.std():.1f})\n"
         "검색 관심도는 구글 트렌드 상대값(작품별 최고 날 = 100)이며, 실제 검색 횟수가 아니다.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.86, bottom=0.07, left=0.08, right=0.97)
fig.savefig("images/07_trend_weekday.png", dpi=150)
print("\n저장: images/07_trend_weekday.png")