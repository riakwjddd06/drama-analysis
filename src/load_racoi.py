"""라코이(RACOI) 인터넷반응DB 엑셀 → 우리 10편의 주간 화제성 표"""
import datetime as dt
import os
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)
os.makedirs("data/processed", exist_ok=True)

COLS = ["week", "program", "channel", "day",
        "posts", "comments", "views", "news", "videos",                       # 건수
        "s_posts", "s_comments", "s_views", "s_news", "s_videos",             # 점유율(%)
        "viewers_hh", "viewers_2049", "rating_hh", "rating_2049"]

raw = pd.read_excel("data/raw/racoi/racoi_ibuzz_20251229_20260802.xlsx", header=None, skiprows=7)
raw.columns = COLS
raw = raw.dropna(subset=["week"])

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
r = raw[raw["program"].isin(dramas["title"])].rename(columns={"program": "title"}).copy()

# 주차 코드(예: 202615) = ISO 연도·주차 → 그 주 월요일
r["week_start"] = pd.to_datetime([dt.date.fromisocalendar(int(w) // 100, int(w) % 100, 1) for w in r["week"]])
first_monday = dramas.set_index("title")["first_air"].map(lambda d: d - pd.Timedelta(days=d.weekday()))
r["week_no"] = (r["week_start"] - r["title"].map(first_monday)).dt.days // 7 + 1   # 1화가 들어 있는 주 = 1주차
r["buzz"] = r["posts"] + r["comments"]                                             # 시청자 버즈 = 게시글 + 댓글

keep = ["title", "week", "week_start", "week_no", "posts", "comments", "buzz", "views", "news", "videos",
        "rating_hh", "rating_2049"]
r = r[keep].sort_values(["title", "week_no"])
r.to_csv("data/processed/racoi_weekly.csv", index=False)

# ---------- 점검 ----------
print("작품별 주 수와 주차 범위")
print(r.groupby("title")["week_no"].agg(["count", "min", "max"]).to_string())
missing = set(dramas["title"]) - set(r["title"])
print("\n없는 작품:", missing or "없음")

# 라코이 시청률(닐슨)과 우리 시청률(회차 → 주 평균) 비교
ratings = pd.read_csv("data/raw/ratings.csv", parse_dates=["air_date"])
ratings["week"] = ratings["air_date"].dt.isocalendar().year * 100 + ratings["air_date"].dt.isocalendar().week
ours = ratings.groupby(["title", "week"])["rating"].mean().rename("ours")
cmp = r.merge(ours.reset_index(), on=["title", "week"])
diff = (cmp["rating_hh"] - cmp["ours"]).abs()
print(f"\n시청률 대조: {len(cmp)}주, 차이 평균 {diff.mean():.2f}%p, 최대 {diff.max():.2f}%p")
