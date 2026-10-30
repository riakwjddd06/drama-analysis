"""구글 트렌드(주제) 국내 묶음 4개를 합쳐 일별 데이터로 만든다.
- value_level : 모든 작품을 '신이랑 법률사무소(묶음 1)' 눈금으로 환산한 값 → 작품 간 비교용
- value_shape : 작품마다 해상도가 가장 좋은 묶음의 값, 작품 최고점 = 100 → 작품 안 흐름 분석용
"""
import os
import pandas as pd

os.makedirs("data/processed", exist_ok=True)
BATCHES = ["1", "2a", "2b", "3"]
ANCHOR = "신이랑 법률사무소"

def read_trends(name):
    df = pd.read_csv(f"data/raw/google/kr_batch{name}.csv", skiprows=2, index_col=0, parse_dates=True)
    df.columns = [c.split(":")[0].strip() for c in df.columns]      # "김부장: (대한민국)" → "김부장"
    df = df.replace("<1", 0.5).apply(pd.to_numeric)                  # "<1"은 0.5로
    return df.drop(columns=["Undercover Miss Hong"], errors="ignore")  # 중복 주제(확인용)는 제외

b = {n: read_trends(n) for n in BATCHES}

# ---------- 1. 묶음 연결: 겹치는 작품의 합계 비율로 묶음 1 눈금에 맞춘다 ----------
def ratio(src, dst, title):
    """src 묶음 값을 dst 묶음 눈금으로 바꾸는 배율"""
    return b[dst][title].sum() / b[src][title].sum()

f = {"1": 1.0}
f["3"] = ratio("3", "1", ANCHOR)
f["2a"] = ratio("2a", "1", ANCHOR)
via_mosa = ratio("2b", "2a", "모두가 자신의 무가치함과 싸우고 있다") * f["2a"]
via_sold = ratio("2b", "3", "오늘도 매진했습니다") * f["3"]
f["2b"] = via_mosa

print("묶음 배율:", {k: round(float(v), 3) for k, v in f.items()})
print("\n[연결 검증] 같은 값이 나와야 정상")
print(f"  은애하는 도적님아 (묶음1 → 묶음3 환산): {b['1']['은애하는 도적님아'].sum():.0f} vs "
      f"{b['3']['은애하는 도적님아'].sum() * f['3']:.0f}")
print(f"  묶음 2b 배율 (모두가 경유 vs 오늘도 매진 경유): {via_mosa:.3f} vs {via_sold:.3f}")

# ---------- 2. 작품별로 값 고르기 ----------
rows = []
for title in pd.read_csv("data/dramas.csv")["title"]:
    have = [n for n in BATCHES if title in b[n].columns]
    best = max(have, key=lambda n: b[n][title].max())                # 최고점이 가장 큰 묶음 = 해상도 최고
    s_best = b[best][title]
    s_level = s_best * f[best]                                       # 같은 묶음 값을 공통 눈금으로
    rows.append(pd.DataFrame({
        "title": title,
        "date": s_best.index,
        "value_level": s_level.values,
        "value_shape": (s_best / s_best.max() * 100).values,
        "batch_used": best,
    }))
g = pd.concat(rows, ignore_index=True)
g.to_csv("data/processed/google_kr_daily.csv", index=False)

# ---------- 3. 점검표 ----------
dr = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
chk = g.merge(dr[["title", "first_air", "last_air"]], on="title")
def summary(x):
    run = x[(x["date"] >= x["first_air"]) & (x["date"] <= x["last_air"])]
    return pd.Series({
        "사용 묶음": x["batch_used"].iloc[0],
        "방영중 합계(공통 눈금)": round(run["value_level"].sum(), 1),
        "방영중 0인 날 비율": round((run["value_shape"] == 0).mean(), 2),
        "최고점 날짜": x.loc[x["value_shape"].idxmax(), "date"].date(),
    })
table = chk.groupby("title").apply(summary, include_groups=False)
table["저신뢰"] = table["방영중 0인 날 비율"] > 0.4
pd.set_option("display.width", 200)
print("\n", table.sort_values("방영중 합계(공통 눈금)", ascending=False))