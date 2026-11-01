"""2장: 시청률 대비 화제성 갭(메인: 라코이)
Q2-A: 시청률과 온라인 화제성은 같은 순서인가? (출처 간 순위 일치도)
Q2-B: 갭이 큰 작품은 어떤 특징이 있나? (2049 비율, 보는 소비 vs 말하는 소비)"""
import os
import warnings
import matplotlib.pyplot as plt
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)   # 네이버 엑셀 스타일 경고
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

dramas = pd.read_csv("data/dramas.csv", parse_dates=["first_air", "last_air"])
ratings = pd.read_csv("data/raw/ratings.csv")
google = pd.read_csv("data/processed/google_kr_daily.csv", parse_dates=["date"])
fundex = pd.read_csv("data/raw/fundex.csv")
racoi = pd.read_csv("data/processed/racoi_weekly.csv")

def airing(df, value):
    """방영 기간(1화~최종화) 하루 평균"""
    d = df.merge(dramas[["title", "first_air", "last_air"]], on="title")
    d = d[(d["date"] >= d["first_air"]) & (d["date"] <= d["last_air"])]
    return d.groupby("title")[value].mean()

# ---------- 1. 출처별 지표 ----------
t = pd.DataFrame(index=dramas["title"])
t["시청률"] = ratings.groupby("title")["rating"].mean()                 # 회차 평균 시청률
# 라코이는 '방영 주 중앙값'을 쓴다: 한 주 급등(신이랑 법률사무소 6주차 댓글 25,928건,
# 다른 주의 약 10배)이 작품 전체 값을 좌우하지 않게 하려고. 평균은 민감도 확인용으로만 남긴다.
rg = racoi.groupby("title")
t["라코이_버즈"] = rg["buzz"].median()                                    # 방영 주 중앙값 게시글+댓글 (메인)
t["라코이_조회수"] = rg["views"].median()                                 # 방영 주 중앙값 동영상 조회수
t["라코이_뉴스"] = rg["news"].median()                                    # 방영 주 중앙값 뉴스 수
t["라코이_버즈_평균"] = rg["buzz"].mean()                                 # 민감도 확인용
t["구글"] = airing(google, "value_level")                                # 방영 기간 하루 평균 검색량

# 네이버(검증용): 엑셀 3개를 기준 작품(은애하는 도적님아) 합계 비율로 연결
def read_datalab(path):
    raw = pd.read_excel(path, header=None)
    parts = []
    for c in range(0, raw.shape[1], 2):
        p = raw.iloc[7:, [c, c + 1]].copy()
        p.columns = ["date", "value"]
        p["title"] = str(raw.iloc[6, c + 1]).removesuffix(" 드라마")
        parts.append(p)
    df = pd.concat(parts, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"])
    return df
nv = [read_datalab(f"data/raw/naver/batch{i}.xlsx") for i in [1, 2, 3]]
base = nv[0].query("title == '은애하는 도적님아'")["value"].sum()
for df in nv[1:]:
    df["value"] *= base / df.query("title == '은애하는 도적님아'")["value"].sum()
naver = pd.concat([nv[0]] + [df.query("title != '은애하는 도적님아'") for df in nv[1:]])
t["네이버"] = airing(naver, "value")

# 펀덱스(검증용): 확보된 주 중 최고 순위 (공개 범위가 주마다 달라 평균 대신 최고 순위 사용)
t["펀덱스_최고순위"] = fundex.groupby("title")["rank"].min()

# ---------- 2. 순위와 갭 ----------
r = pd.DataFrame(index=t.index)
for col in ["시청률", "라코이_버즈", "라코이_조회수", "라코이_뉴스", "구글", "네이버"]:
    r[col] = t[col].rank(ascending=False).astype(int)                  # 1위 = 가장 높음
r["펀덱스"] = t["펀덱스_최고순위"].rank(method="min").astype(int)       # 같은 순위면 공동
r["갭"] = r["시청률"] - r["라코이_버즈"]                                  # +면 시청률에 비해 화제성이 높음
r["갭(구글)"] = r["시청률"] - r["구글"]
r["갭(버즈 평균)"] = r["시청률"] - t["라코이_버즈_평균"].rank(ascending=False).astype(int)   # 민감도

zero_ratio = google.merge(dramas[["title", "first_air", "last_air"]], on="title")
zero_ratio = zero_ratio[(zero_ratio["date"] >= zero_ratio["first_air"]) & (zero_ratio["date"] <= zero_ratio["last_air"])]
r["구글_저신뢰"] = zero_ratio.groupby("title")["value_shape"].apply(lambda s: (s == 0).mean() > 0.4)

r = r.sort_values("시청률")
pd.set_option("display.width", 200)
print("[출처별 원값]\n", t.round(3).loc[r.index], "\n")
print("[순위와 갭]\n", r, "\n")

# ---------- 3. 검증 ⑩: 출처 간 순위 일치도 (스피어만 상관) ----------
print("[출처 간 순위 일치도: 1에 가까울수록 같은 순서]")
print(r[["시청률", "라코이_버즈", "라코이_조회수", "라코이_뉴스", "펀덱스", "구글", "네이버"]].corr(method="spearman").round(2))

# ---------- 3-2. Q2-B: 갭이 큰 작품의 특징 ----------
f = pd.DataFrame(index=t.index)
f["방송사"] = dramas.set_index("title")["broadcaster"]
f["갭"] = r["갭"]
f["2049 비율"] = rg["rating_2049"].mean() / rg["rating_hh"].mean()       # 젊은 층 쏠림의 대리 지표 (연령 구성비 아님)
f["조회÷버즈"] = t["라코이_조회수"] / t["라코이_버즈"]                     # 클수록 '보는' 소비 중심
f["뉴스÷버즈"] = t["라코이_뉴스"] / t["라코이_버즈"]                       # 클수록 언론 노출에 비해 시청자 이야기가 적음
f["댓글÷게시글"] = rg["comments"].median() / rg["posts"].median()
f = f.sort_values("갭", ascending=False)
print("\n[Q2-B 갭이 큰 작품의 특징]\n", f.round(3).to_string())
print("\n[갭과의 순위 일치도]")
for c in ["2049 비율", "조회÷버즈", "뉴스÷버즈", "댓글÷게시글"]:
    print(f"  {c}: {f[c].rank().corr(f['갭'].rank()):.2f}")
print("\n[민감도] 버즈를 평균으로 계산했을 때의 갭\n", r[["갭", "갭(버즈 평균)"]].to_string())
f.round(4).to_csv("data/processed/ch2_features.csv")

t.round(4).to_csv("data/processed/ch2_sources.csv")
r.to_csv("data/processed/ch2_gap.csv")

# ---------- 4. 그래프 03: 시청률 순위 vs 라코이 화제성 순위 ----------
INK, MUTED, UP, DOWN = "#2b2b2b", "#8a8a85", "#2a78d6", "#eb6834"
fig, ax = plt.subplots(figsize=(9, 8))
for title, row in r.iterrows():
    gap = row["갭"]
    color = UP if gap >= 3 else DOWN if gap <= -3 else "#c9c9c4"
    lw = 2.5 if abs(gap) >= 3 else 1.2
    ls = "-"
    ax.plot([0, 1], [row["시청률"], row["라코이_버즈"]], color=color, lw=lw, ls=ls, marker="o", ms=7)
    ax.text(-0.04, row["시청률"], f"{title}  {row['시청률']}", ha="right", va="center", fontsize=10,
            color=INK if abs(gap) >= 3 else MUTED)
    label = f"{row['라코이_버즈']}  {title}"
    ax.text(1.04, row["라코이_버즈"], label, ha="left", va="center", fontsize=10,
            color=INK if abs(gap) >= 3 else MUTED)
ax.set_xlim(-0.9, 1.9)
ax.set_ylim(10.6, -0.9)                                   # 1위가 위
ax.axis("off")
ax.text(0, -0.1, "시청률 순위\n(회차 평균)", ha="center", va="bottom", fontsize=11, color=INK)
ax.text(1, -0.1, "라코이 화제성 순위\n(방영 주 중앙값 게시글+댓글)", ha="center", va="bottom", fontsize=11, color=INK)
fig.suptitle("그래프 03. 시청률 순위 vs 화제성 순위 (10편 안에서)", x=0.02, ha="left", fontsize=14, color=INK)
fig.text(0.02, 0.925,
         "파란선: 시청률에 비해 화제성이 3계단 이상 높은 작품  ·  주황선: 3계단 이상 낮은 작품  ·  화제성 = 라코이(한국방송광고진흥공사) 시청자 버즈\n"
         "순위는 분석 대상 10편 안에서의 상대 순서이며, 다른 드라마보다 절대적으로 높다는 뜻이 아니다.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.88, bottom=0.03, left=0.02, right=0.98)
fig.savefig("images/03_gap_domestic.png", dpi=150)
print("\n저장: images/03_gap_domestic.png")

# ---------- 5. 그래프 11: 갭이 큰 작품의 특징 (Q2-B) ----------
SHORT = {"모두가 자신의 무가치함과 싸우고 있다": "모두가", "오늘부터 인간입니다만": "오늘부터",
         "오늘도 매진했습니다": "오늘도 매진", "은애하는 도적님아": "은애", "언더커버 미쓰홍": "언더커버",
         "신이랑 법률사무소": "신이랑", "아기가 생겼어요": "아기가"}
OFFSET = {"2049 비율": {"모두가 자신의 무가치함과 싸우고 있다": (-48, 8), "김부장": (-40, -16),
                       "아기가 생겼어요": (-20, -18), "오늘도 매진했습니다": (6, 8)},
          "조회÷버즈": {"멋진 신세계": (-70, 8), "김부장": (6, -16)}}
fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
panels = [("2049 비율", "2049 시청률 ÷ 가구 시청률 (젊은 층 쏠림의 대리 지표)", False),
          ("조회÷버즈", "동영상 조회수 ÷ 시청자 버즈 (클수록 '보는' 소비 중심, 로그 축)", True)]
for ax, (col, xlabel, logx) in zip(axes, panels):
    for title, row in f.iterrows():
        gap = row["갭"]
        color = UP if gap >= 3 else DOWN if gap <= -3 else MUTED
        ax.scatter(row[col], gap, s=90, color=color, edgecolor=INK, linewidth=0.5, zorder=3)
        ax.annotate(SHORT.get(title, title), (row[col], gap), xytext=OFFSET[col].get(title, (6, 6)),
                    textcoords="offset points", fontsize=9, color=INK)
    rho = f[col].rank().corr(f["갭"].rank())
    ax.axhline(0, color=MUTED, lw=1, ls="--")
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("갭 (시청률 순위 - 화제성 순위, +면 화제성이 높음)")
    ax.set_title(f"순위 일치도 {rho:.2f}", fontsize=11)
    ax.grid(alpha=0.3)
fig.suptitle("그래프 11. 시청률 대비 화제성이 높은 작품 vs 낮은 작품의 특징 (10편)", fontsize=14)
fig.tight_layout()
fig.savefig("images/11_gap_features.png", dpi=150)
print("저장: images/11_gap_features.png")
