"""1장: TV 시청률 곡선 vs 넷플릭스 한국 순위 곡선 유형 나누기"""
import os
import pandas as pd

os.makedirs("data/processed", exist_ok=True)

# ---------- 0. 불러오기 ----------
dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
ratings = pd.read_csv("data/raw/ratings.csv", parse_dates=["air_date"])
nf = pd.read_csv("data/raw/all-weeks-countries.tsv", sep="\t", parse_dates=["week"])

def monday(d):
    """그 날짜가 속한 주(월~일)의 월요일"""
    return d - pd.to_timedelta(d.dt.weekday, unit="D")

# ---------- 1. TV: 방영 주차별 평균 시청률 ----------
tv = ratings.merge(dramas[["title", "first_air"]], on="title")
# 1화가 들어 있는 월~일 주 = 1주차 (넷플릭스 주간과 같은 기준)
tv["week_no"] = (monday(tv["air_date"]) - monday(tv["first_air"])).dt.days // 7 + 1
tv_weekly = tv.groupby(["title", "week_no"], as_index=False)["rating"].mean()
first_week = tv_weekly.groupby("title")["rating"].transform("first")
tv_weekly["rating_idx"] = tv_weekly["rating"] / first_week * 100   # 1주차 = 100

# ---------- 2. 넷플릭스: 한국 TOP 10 주차별 순위 ----------
kr = nf[(nf["country_name"] == "South Korea") & (nf["category"] == "TV")]
kr = kr.merge(dramas[["title", "nf_title", "first_air"]],
              left_on="show_title", right_on="nf_title")
# 넷플릭스 week 값은 그 주 일요일 → 월요일로 바꿔 TV와 같은 주차 계산
kr["week_no"] = (kr["week"] - pd.Timedelta(days=6) - monday(kr["first_air"])).dt.days // 7 + 1
nf_weekly = kr[["title", "week_no", "week", "weekly_rank"]].sort_values(["title", "week_no"])

# ---------- 3. 유형 판정 ----------
def tv_type(title, up=1.1):
    r = ratings[ratings["title"] == title].sort_values("episode")["rating"]
    n = max(len(r) // 3, 1)
    ratio = r.iloc[-n:].mean() / r.iloc[:n].mean()
    if ratio >= up:
        return "상승", ratio
    if ratio <= 2 - up:                       # 1.1배 ↔ 0.9배처럼 대칭
        return "하락", ratio
    return "유지", ratio

def nf_type(title, step=2):
    last_week = tv_weekly.loc[tv_weekly["title"] == title, "week_no"].max()
    weeks = pd.Series(range(1, last_week + 1))                     # 방영 기간 주차
    ranks = nf_weekly[nf_weekly["title"] == title].set_index("week_no")["weekly_rank"]
    ranks = ranks.reindex(weeks)                                   # TOP 10 밖 = 빈칸(NaN)
    if ranks.isna().all():
        return "미진입", None
    n = max(len(weeks) // 3, 1)
    early, late = ranks.iloc[:n], ranks.iloc[-n:]
    if late.isna().any():                                          # 후반부 이탈
        return "하락", None
    if early.isna().all():                                         # 초반엔 밖, 후반엔 안
        return "상승", None
    change = late.mean() - early.mean()                            # +면 순위가 내려감
    if change >= step:
        return "하락", change
    if change <= -step:
        return "상승", change
    return "유지", change

def quadrant(tv_t, nf_t):
    if nf_t == "미진입":
        return "넷플릭스 미진입"
    tv_good, nf_good = tv_t != "하락", nf_t != "하락"
    return {(True, True): "동반 흥행형", (True, False): "TV 뒷심형",
            (False, True): "넷플릭스 강세형", (False, False): "동반 하락형"}[(tv_good, nf_good)]

rows = []
for t in dramas["title"]:
    tt, ratio = tv_type(t)
    nt, change = nf_type(t)
    r = nf_weekly[nf_weekly["title"] == t]
    best = r.loc[r["weekly_rank"].idxmin()] if len(r) else None
    rows.append({
        "title": t,
        "tv_ratio": round(ratio, 2), "tv_type": tt,
        "nf_rank_change": None if change is None else round(change, 1), "nf_type": nt,
        "nf_best_rank": None if best is None else int(best["weekly_rank"]),
        "nf_best_week": None if best is None else int(best["week_no"]),
        "nf_weeks_in_top10": len(r),
        "quadrant": quadrant(tt, nt),
    })
types = pd.DataFrame(rows)

# ---------- 4. 민감도 분석: 기준을 바꿔도 유형이 유지되나 ----------
keep = []
for t in dramas["title"]:
    base = types.loc[types["title"] == t, "quadrant"].item()
    results = [quadrant(tv_type(t, up)[0], nf_type(t, s)[0])
               for up in [1.05, 1.1, 1.15] for s in [1, 2, 3]]
    keep.append(f"{sum(q == base for q in results)}/9")
types["sensitivity"] = keep   # 9가지 기준 조합 중 기본 유형이 나온 횟수

# ---------- 5. 저장 ----------
tv_weekly.to_csv("data/processed/tv_weekly.csv", index=False)
nf_weekly.to_csv("data/processed/nf_kr_weekly.csv", index=False)
types.to_csv("data/processed/ch1_types.csv", index=False)

pd.set_option("display.width", 200)
print(types.to_string(index=False))
missing = set(dramas["title"]) - set(nf_weekly["title"])
if missing:
    print("\n⚠️ 넷플릭스 데이터에서 못 찾은 작품(nf_title 철자 확인):", missing)