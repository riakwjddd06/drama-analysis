"""보너스: 넷플릭스 오리지널 vs TV 동시 방영작 — 한국 TOP 10 순위 곡선 비교
오리지널은 보통 전 회차를 한 번에 공개하고, 동시 방영작은 TV 방송에 맞춰 매주 공개된다.
공개 방식이 다르면 순위 곡선 모양도 다를까?"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

MAX_WEEK = 12                                   # 공개 후 12주까지만 비교
COLORS = {"오리지널": "#d1495b", "동시 방영": "#2e86ab"}

nf = pd.read_csv("data/raw/all-weeks-countries.tsv", sep="\t", parse_dates=["week"])
kr = nf[(nf["country_name"] == "South Korea") & (nf["category"] == "TV")].copy()
def norm(t):
    """대소문자·띄어쓰기·문장부호 차이 무시 (The Wonder Fools = The WONDERfools)"""
    return "".join(ch for ch in str(t).casefold() if ch.isalnum())

kr["key"] = kr["show_title"].map(norm)
kr["season_title"] = kr["season_title"].fillna("")

# 두 그룹을 같은 모양(title, nf_title, start)으로 맞춘다
sim = pd.read_csv("data/dramas.csv", parse_dates=["first_air"])
sim = sim.rename(columns={"first_air": "start"})[["title", "nf_title", "start"]]
sim["season"] = ""
sim["group"] = "동시 방영"
org = pd.read_csv("data/originals.csv", parse_dates=["release"])
org = org.rename(columns={"release": "start"})[["title", "nf_title", "start", "season"]]
org["group"] = "오리지널"
shows = pd.concat([sim, org], ignore_index=True)

# ---------- 1. 작품별 주차 순위 ----------
rows = []
for _, s in shows.iterrows():
    hit = kr[(kr["key"] == norm(s["nf_title"])) & (kr["week"] >= s["start"])]
    if isinstance(s["season"], str) and s["season"]:            # 시즌 지정(사냥개들 2) → 그 시즌 줄만
        hit = hit[hit["season_title"].str.casefold().str.contains(s["season"].casefold(), regex=False)]
    if hit.empty:
        print(f"[확인 필요] {s['title']} ({s['nf_title']}) — 한국 TOP 10에서 찾지 못함.")
        # 공개 후 3주 안에 새로 들어온 제목을 후보로 보여 줌 → originals.csv의 nf_title을 고치면 됨
        near = kr[(kr["week"] >= s["start"]) & (kr["week"] <= s["start"] + pd.Timedelta(days=21))]
        cand = sorted(set(near["show_title"]) - set(shows["nf_title"]))
        print("   같은 시기 한국 TOP 10 제목 후보:", cand)
        continue
    if hit["week"].duplicated().any():                          # 한 주에 두 줄 → 더 높은 순위 하나만
        print(f"[알림] {s['title']}: 같은 주에 여러 줄이 있어 주마다 가장 높은 순위만 사용")
        hit = hit.sort_values("weekly_rank").drop_duplicates("week").sort_values("week")
    start_monday = s["start"] - pd.Timedelta(days=s["start"].weekday())
    # 넷플릭스 week = 그 주 일요일 → 월요일로 바꿔서, 공개일이 든 월~일 주 = 1주차
    week_no = (hit["week"] - pd.Timedelta(days=6) - start_monday).dt.days // 7 + 1
    for w, r in zip(week_no, hit["weekly_rank"]):
        if w <= MAX_WEEK:
            rows.append({"group": s["group"], "title": s["title"], "week_no": w, "rank": r})
curve = pd.DataFrame(rows)

# ---------- 2. 작품별 요약 지표 ----------
def summary(d):
    d = d.sort_values("week_no")
    best = d["rank"].min()
    return pd.Series({
        "첫주_순위": d.loc[d["week_no"] == 1, "rank"].min(),           # 1주차에 없으면 빈칸
        "최고순위": best,
        "최고순위_주차": d.loc[d["rank"] == best, "week_no"].min(),
        "TOP10_주수": len(d),
        "1위_주수": (d["rank"] == 1).sum(),
        "잔존점수": (11 - d["rank"]).sum(),                            # 3장과 같은 점수
        "마지막_주차": d["week_no"].max(),
    })

table = curve.groupby(["group", "title"]).apply(summary, include_groups=False).reset_index()
table.to_csv("data/processed/bonus_original_vs_simulcast.csv", index=False, encoding="utf-8-sig")
print(table.sort_values(["group", "잔존점수"], ascending=[True, False]).to_string(index=False))

print("\n그룹별 중앙값")
cols = ["최고순위", "최고순위_주차", "TOP10_주수", "1위_주수", "잔존점수", "마지막_주차"]
print(table.groupby("group")[cols].median().round(1).to_string())

# 주차별 TOP 10 잔류율: 그 주에 TOP 10 안에 있던 작품 비율
n_shows = table.groupby("group")["title"].nunique()
stay = curve.groupby(["group", "week_no"])["title"].nunique().unstack(0).reindex(range(1, MAX_WEEK + 1)).fillna(0)
stay = stay / n_shows * 100
print("\n주차별 TOP 10 잔류율(%)")
print(stay.round(0).astype(int).T.to_string())

# ---------- 3. 그래프 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

for (grp, title), d in curve.groupby(["group", "title"]):
    d = d.set_index("week_no")["rank"].reindex(range(1, MAX_WEEK + 1))   # TOP 10 밖 = 끊어진 선
    ax1.plot(d.index, d.values, marker="o", ms=3, lw=1.3, alpha=0.75, color=COLORS[grp])
for grp, c in COLORS.items():
    ax1.plot([], [], color=c, lw=2, label=f"{grp} ({n_shows.get(grp, 0)}편)")
ax1.set_ylim(10.5, 0.5)
ax1.set_yticks(range(1, 11))
ax1.set_xticks(range(1, MAX_WEEK + 1))
ax1.set_xlabel("공개 후 주차 (1주차 = 첫 공개 주)")
ax1.set_ylabel("넷플릭스 한국 TV 순위")
ax1.set_title("작품별 순위 곡선 (끊긴 곳 = TOP 10 밖)")
ax1.grid(alpha=0.3)
ax1.legend(loc="lower left")

for grp, c in COLORS.items():
    if grp in stay:
        ax2.plot(stay.index, stay[grp], marker="o", lw=2.5, color=c, label=grp)
ax2.set_ylim(0, 105)
ax2.set_xticks(range(1, MAX_WEEK + 1))
ax2.set_xlabel("공개 후 주차")
ax2.set_ylabel("TOP 10 안에 남은 작품 비율 (%)")
ax2.set_title("주차별 TOP 10 잔류율")
ax2.grid(alpha=0.3)
ax2.legend(loc="upper right")

fig.suptitle("넷플릭스 오리지널 vs TV 동시 방영작 — 한국 TOP 10 순위 흐름", fontsize=14)
fig.tight_layout()
fig.savefig("images/09_original_vs_simulcast.png", dpi=150)
print("\n저장: images/09_original_vs_simulcast.png, data/processed/bonus_original_vs_simulcast.csv")
