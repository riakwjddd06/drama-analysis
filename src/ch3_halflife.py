"""3장: 종영 후 검색 관심도 반감기 + 민감도 분석(검증 ⑨) + 그래프 05"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
types = pd.read_csv("data/processed/ch1_types.csv")[["title", "quadrant"]]
g = pd.read_csv("data/processed/google_kr_daily.csv", parse_dates=["date"])

# ---------- 0. 정제: 확인된 이상값 처리 ----------
# 멋진 신세계 8/2~3 급등: 관련 기사 없음 + 네이버에는 변화 없음 → 드라마와 무관한 급등으로 보고 앞뒤 값으로 채움
OUTLIERS = [("멋진 신세계", "2026-08-02"), ("멋진 신세계", "2026-08-03")]
for title, day in OUTLIERS:
    g.loc[(g["title"] == title) & (g["date"] == day), "value_shape"] = None
g["value_shape"] = g.groupby("title")["value_shape"].transform(lambda s: s.interpolate())
# 종영 후 재상승 이벤트(유지하되 표시만): 김부장 8/8~9 제작사 수사 보도·종영 인터뷰
EVENTS = {"김부장": ("2026-08-08", "제작사 수사·종영 인터뷰")}

PEAK_EXTRA = 3   # 최종화 직후 반응(방송 후 3일)까지 최고점 구간에 포함

def halflife(title, window=7, cut=0.5, keep=3):
    d = dramas.set_index("title").loc[title]
    s = g[g["title"] == title].set_index("date")["value_shape"].sort_index()
    ma = s.rolling(window, min_periods=1, center=True).mean()   # 가운데 정렬: 정점이 뒤로 밀리지 않게
    run = ma[d["first_air"]:d["last_air"] + pd.Timedelta(days=PEAK_EXTRA)]
    peak, peak_day = run.max(), run.idxmax()
    after = ma[d["last_air"] + pd.Timedelta(days=1):]
    below = after < peak * cut
    hl = None
    for i in range(len(after) - keep + 1):
        if below.iloc[i:i + keep].all():
            hl = (after.index[i] - d["last_air"]).days
            break
    return {
        "최고점 도달(1화 후 일수)": (peak_day - d["first_air"]).days,
        "최고점~종영(일)": (d["last_air"] - peak_day).days,   # 음수면 종영 직후가 최고점
        "종영일 관심(최고점=100)": round(ma[d["last_air"]] / peak * 100),
        "반감기(일)": hl,                       # None = 관측 기간 내 미도달
    }

# ---------- 1. 기본 결과 (7일 이동평균, 50%, 3일 연속) ----------
rows = [{"title": t, **halflife(t)} for t in dramas["title"]]
res = pd.DataFrame(rows).merge(types, on="title")
res["반감기(일)"] = res["반감기(일)"].astype("Int64")
res["비고"] = res["title"].map(lambda t: EVENTS.get(t, ("", ""))[1])
# 종영일에 이미 최고점의 50% 아래였다면 '종영 후에 식은 속도'가 아니라 '종영 전에 이미 식은 것'
res["종영 전 반감"] = res["종영일 관심(최고점=100)"] < 50

# 저신뢰 표시 (방영 중 0인 날 40% 초과)
z = g.merge(dramas[["title", "first_air", "last_air"]], on="title")
z = z[(z["date"] >= z["first_air"]) & (z["date"] <= z["last_air"])]
res["저신뢰"] = res["title"].map(z.groupby("title")["value_shape"].apply(lambda s: (s == 0).mean() > 0.4))

# ---------- 2. 검증 ⑨ 민감도: 이동평균 기간 × 반감 기준 ----------
sens = {}
for w in [3, 7, 14]:
    for c in [0.4, 0.5, 0.6]:
        sens[f"MA{w}·{int(c*100)}%"] = [halflife(t, w, c)["반감기(일)"] for t in res["title"]]
sens = pd.DataFrame(sens, index=res["title"])
sens["최소"], sens["최대"] = sens.min(axis=1), sens.max(axis=1)
# 9가지 기준 각각에서 매긴 반감기 순위가 기본 기준(MA7·50%) 순위와 얼마나 같은지
rank_agree = sens.drop(columns=["최소", "최대"]).rank().corr(method="spearman")["MA7·50%"].round(2)

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
print("[작품별 결과]\n", res.sort_values(["quadrant", "반감기(일)"]).to_string(index=False), "\n")
print("[유형별 평균] (종영 전 반감 작품은 반감기 평균에서 제외)\n", res.assign(**{"반감기(일)": res["반감기(일)"].where(~res["종영 전 반감"])}).groupby("quadrant")[["최고점 도달(1화 후 일수)", "종영일 관심(최고점=100)", "반감기(일)"]]
      .mean().round(1), "\n")
print("[민감도: 기준을 바꿨을 때 반감기(일)]\n", sens, "\n")
print("[민감도: 기본 기준과의 순위 일치도]\n", rank_agree.to_string(), "\n")
res.to_csv("data/processed/ch3_halflife.csv", index=False)
sens.to_csv("data/processed/ch3_sensitivity.csv")

# ---------- 3. 그래프 05: 종영일 = 0 기준 감쇠 곡선 ----------
INK, MUTED, LINE = "#2b2b2b", "#8a8a85", "#2a78d6"
order = res.sort_values(["quadrant", "반감기(일)"])
fig, axes = plt.subplots(2, 5, figsize=(17, 7.5), sharey=True)
for ax, (_, r) in zip(axes.flat, order.iterrows()):
    d = dramas.set_index("title").loc[r["title"]]
    s = g[g["title"] == r["title"]].set_index("date")["value_shape"].sort_index()
    ma = s.rolling(7, min_periods=1, center=True).mean()
    peak = ma[d["first_air"]:d["last_air"] + pd.Timedelta(days=PEAK_EXTRA)].max()
    x = (ma.index - d["last_air"]).days
    m = (x >= -30) & (x <= 60)
    ax.plot(x[m], (ma / peak * 100)[m], color=LINE, lw=2)
    ax.axhline(50, color=MUTED, lw=0.8, ls=":")
    ax.axvline(0, color=MUTED, lw=1, ls="--")
    if r["종영 전 반감"]:
        ax.text(5, 56, "종영 전 이미 50% 아래", fontsize=9, color=INK)
    elif pd.notna(r["반감기(일)"]):
        ax.plot(r["반감기(일)"], 50, "o", ms=9, mfc="white", mec=LINE, mew=2)
        ax.text(r["반감기(일)"] + 2, 56, f"{r['반감기(일)']}일", fontsize=9, color=INK)
    else:
        ax.text(30, 56, "미도달", fontsize=9, color=INK)
    if r["title"] in EVENTS:
        ev = (pd.Timestamp(EVENTS[r["title"]][0]) - d["last_air"]).days
        ax.axvspan(ev - 0.5, ev + 1.5, color="#eb6834", alpha=0.15, lw=0)
        ax.text(ev + 3, 115, EVENTS[r["title"]][1], fontsize=8, color=MUTED, va="center")
    title = r["title"] + (" (저신뢰)" if r["저신뢰"] else "")
    ax.set_title(f"{title}\n{r['quadrant']}", fontsize=10, color=INK, loc="left")
    ax.set_xlim(-30, 60)
    ax.set_ylim(0, 125)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.tick_params(labelsize=8, colors=MUTED)
    ax.grid(axis="y", color="#e6e6e3", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
for ax in axes[1]:
    ax.set_xlabel("종영일로부터 일수", fontsize=9, color=MUTED)
for ax in axes[:, 0]:
    ax.set_ylabel("검색 관심도\n(방영 중 최고점=100)", fontsize=9, color=INK)
fig.suptitle("그래프 05. 종영 후 검색 관심도가 식는 속도 (구글 트렌드, 대한민국)", x=0.01, ha="left", fontsize=14, color=INK)
fig.text(0.01, 0.935, "점선(가로): 최고점의 50%  ·  점선(세로): 종영일  ·  흰 원: 반감기(7일 이동평균이 최고점의 50% 아래로 3일 연속 내려간 첫날)  ·  최고점 구간: 1화 ~ 최종화 3일 뒤\n"
         "검색 관심이 줄어드는 속도이며, 실제 시청자가 절반으로 줄어든 시점을 뜻하지 않는다. 일별 검색량의 요일 변동을 없애려고 7일 이동평균(가운데 정렬)을 썼다.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.80, bottom=0.08, left=0.07, right=0.99, hspace=0.55, wspace=0.12)
fig.savefig("images/05_decay_curves.png", dpi=150)
print("저장: images/05_decay_curves.png")