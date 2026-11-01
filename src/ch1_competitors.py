"""1장 보완: 넷플릭스 순위가 떨어진 주에 새 경쟁작이 들어왔을까?
넷플릭스 순위는 상대 순위라, 시청자가 그대로여도 강한 신작이 들어오면 밀린다. 이를 확인한다."""
import pandas as pd

ONE_WEEK = pd.Timedelta(days=7)
dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
nf = pd.read_csv("data/raw/all-weeks-countries.tsv", sep="\t", parse_dates=["week"])
kr = nf[(nf["country_iso2"] == "KR") & (nf["category"] == "TV")].copy()
# '새로 들어온 작품' = 지난 8주 동안 한국 TOP 10에 없다가 이번 주에 들어온 작품.
# (처음 공개된 신작 + 새 시즌 + 오래된 작품의 재진입. 경쟁 상대로는 모두 '새로 끼어든' 작품이다)
LOOKBACK = 8
seen = kr.groupby("show_title")["week"].apply(lambda s: sorted(s))
def is_new(row):
    weeks = seen[row["show_title"]]
    return not any(row["week"] - LOOKBACK * ONE_WEEK <= w < row["week"] for w in weeks)
kr["is_new"] = kr.apply(is_new, axis=1)

rows = []
for _, d in dramas.iterrows():
    mine = kr[kr["show_title"] == d["nf_title"]].set_index("week")["weekly_rank"]
    start_monday = d["first_air"] - pd.Timedelta(days=d["first_air"].weekday())
    # 방영 기간 + 종영 후 3주까지의 주(일요일 기준)만 본다
    weeks = pd.date_range(mine.index.min(), d["last_air"] + pd.Timedelta(days=27), freq="W-SUN")
    for w in weeks[1:]:
        prev, now = mine.get(w - ONE_WEEK), mine.get(w)
        if pd.isna(prev):
            continue                                            # 지난주에 TOP 10 밖이면 비교 불가
        dropped = pd.isna(now) or now - prev >= 2               # 2계단 이상 하락 또는 TOP 10 이탈
        cut = 11 if pd.isna(now) else now                       # 우리 작품보다 위에 있는 새 작품만
        new = kr[(kr["week"] == w) & kr["is_new"] & (kr["weekly_rank"] < cut)]
        new = new.sort_values("weekly_rank").drop_duplicates("show_title")   # 두 시즌이 함께 들어오면 한 번만
        rows.append({
            "title": d["title"],
            "week": w.date(),
            "week_no": (w - pd.Timedelta(days=6) - start_monday).days // 7 + 1,
            "지난주": int(prev),
            "이번주": "밖" if pd.isna(now) else int(now),
            "하락": dropped,
            "위로 새로 들어온 작품 수": len(new),
            "새로 들어온 작품(순위)": ", ".join(f"{t}({r})" for t, r in zip(new["show_title"], new["weekly_rank"])),
        })
res = pd.DataFrame(rows)
res.to_csv("data/processed/ch1_competitors.csv", index=False, encoding="utf-8-sig")

pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 80)
drops = res[res["하락"]]
print("[순위가 2계단 이상 떨어지거나 TOP 10에서 빠진 주]")
print(drops.drop(columns="하락").to_string(index=False))

def share(df):
    return (df["위로 새로 들어온 작품 수"] > 0).mean() * 100

print(f"\n하락한 주 {len(drops)}번 중 우리 작품 위로 새 작품이 들어온 주: {share(drops):.0f}%")
print(f"하락하지 않은 주 {len(res) - len(drops)}번 중 같은 경우: {share(res[~res['하락']]):.0f}%")
print("\n저장: data/processed/ch1_competitors.csv")
