"""보너스: 시계열 분해 — 검색 관심도 = 추세 + 주간 반복(요일 효과) + 나머지
대표작은 그래프로, 10편은 '주간 반복의 세기'를 숫자로 비교한다."""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

REP = "은애하는 도적님아"
DAYS = ["월", "화", "수", "목", "금", "토", "일"]

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"]).set_index("title")
g = pd.read_csv("data/processed/google_kr_daily.csv", parse_dates=["date"])

def decompose(title):
    """고전적 가법 분해(주기 7일): statsmodels seasonal_decompose와 같은 방식"""
    d = dramas.loc[title]
    s = g[g["title"] == title].set_index("date")["value_shape"].sort_index()[d["first_air"]:d["last_air"]]
    trend = s.rolling(7, center=True).mean()                       # ① 추세: 가운데 정렬 7일 이동평균
    detr = s - trend
    wd = detr.groupby(detr.index.weekday).mean()                   # ② 요일별 평균 편차
    wd = wd - wd.mean()                                            #    합이 0이 되도록 맞춤
    seasonal = pd.Series(s.index.weekday.map(wd), index=s.index)
    resid = s - trend - seasonal                                   # ③ 나머지 = 원값 - 추세 - 주간 반복
    return s, trend, seasonal, resid, wd

# ---------- 10편: 주간 반복의 세기 ----------
# 세기 = 1 - 나머지 분산 / (주간 반복 + 나머지) 분산. 1에 가까울수록 요일 패턴이 뚜렷함
rows = []
for t in dramas.index:
    s, trend, seasonal, resid, wd = decompose(t)
    ok = resid.notna()
    strength = max(0.0, 1 - resid[ok].var() / (seasonal[ok] + resid[ok]).var())
    top = wd.idxmax()
    rows.append({"title": t, "주간 반복 세기": round(strength, 2),
                 "가장 높은 요일": DAYS[top], "그 요일 효과": round(wd.max(), 1)})
res = pd.DataFrame(rows).sort_values("주간 반복 세기", ascending=False)
print(res.to_string(index=False))
res.to_csv("data/processed/bonus_decompose.csv", index=False)

# ---------- 대표작 그래프 ----------
s, trend, seasonal, resid, wd = decompose(REP)
INK, MUTED, C = "#2b2b2b", "#8a8a85", "#2a78d6"
fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
parts = [(s, "① 원값"), (trend, "② 추세 (7일 이동평균)"), (seasonal, "③ 주간 반복 (요일 효과)"), (resid, "④ 나머지 (노이즈)")]
for ax, (v, name) in zip(axes, parts):
    if name.startswith("①") or name.startswith("②"):
        ax.plot(v.index, v.values, color=C, lw=1.8)
    else:
        ax.bar(v.index, v.values, color=C if name.startswith("③") else "#c9c9c4", width=0.8)
        ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title(name, loc="left", fontsize=11, color=INK)
    ax.tick_params(labelsize=8, colors=MUTED)
    ax.grid(axis="y", color="#e6e6e3", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
strength = res.set_index("title").loc[REP, "주간 반복 세기"]
fig.suptitle(f"그래프 08. {REP} 검색 관심도 분해 (방영 기간, 구글 트렌드)", x=0.02, ha="left", fontsize=14, color=INK)
fig.text(0.02, 0.945, f"원값 = 추세 + 주간 반복 + 나머지 (가법 분해, 주기 7일).  주간 반복 세기 {strength:.2f} "
         f"(1에 가까울수록 요일 패턴이 뚜렷함).  가장 높은 요일: {DAYS[wd.idxmax()]} (+{wd.max():.0f})",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.88, bottom=0.05, left=0.07, right=0.98, hspace=0.45)
fig.savefig("images/08_decompose.png", dpi=150)
print("\n저장: images/08_decompose.png")
