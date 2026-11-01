"""3장 보완: 종영 전 관심은 종영 후 넷플릭스 잔존과 관계가 있을까?
1장 유형(넷플릭스 순위가 들어감) 대신, 넷플릭스를 전혀 쓰지 않은 '종영 전 지표'로 비교해 순환성을 없앤다.
먼저 load_racoi.py, ch3_netflix.py를 실행해 둘 것"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

racoi = pd.read_csv("data/processed/racoi_weekly.csv").sort_values(["title", "week_no"])
ratings = pd.read_csv("data/raw/ratings.csv").sort_values(["title", "episode"])
after = pd.read_csv("data/processed/ch3_netflix.csv")[["title", "종영 후 잔존(주)", "잔존 점수"]]

# ---------- 1. 종영 전 지표 (넷플릭스 미사용) ----------
rows = []
for title, g in racoi.groupby("title"):
    b = g["buzz"].reset_index(drop=True)              # 라코이 시청자 버즈(게시글+댓글), 방영 주만
    r = ratings.loc[ratings["title"] == title, "rating"].reset_index(drop=True)
    n3 = max(len(b) // 3, 1)
    rows.append({
        "title": title,
        # 메인: 마지막 2주 평균 ÷ 방영 기간 중앙값 (중앙값을 써서 한 주 급등에 덜 흔들리게)
        "버즈 유지율": b.iloc[-2:].mean() / b.median(),
        # 민감도용 다른 정의 4가지
        "마지막2주÷최고주": b.iloc[-2:].mean() / b.max(),
        "최종주 빼고 2주÷중앙값": b.iloc[-3:-1].mean() / b.median(),
        "후반1/3÷앞2/3": b.iloc[-n3:].mean() / b.iloc[:-n3].mean(),
        "최종주÷중앙값": b.iloc[-1] / b.median(),
        "시청률 유지율": r.iloc[-1] / r.max(),           # 최종화 ÷ 최고 회차
        "버즈 규모": b.median(),                         # 작품 크기 (주 버즈 중앙값)
    })
pre = pd.DataFrame(rows).merge(after, on="title")
pre = pre.sort_values(["종영 후 잔존(주)", "잔존 점수"], ascending=False).reset_index(drop=True)

def spearman(a, b):
    """스피어만 = 순위끼리의 상관 (scipy 없이 계산, 동점은 평균 순위)"""
    return a.rank().corr(b.rank())

def rho(col):
    return spearman(pre[col], pre["잔존 점수"])

print(pre.round(2).to_string(index=False))

print("\n종영 후 넷플릭스 잔존 점수와의 순위 일치도 (스피어만, 10편)")
sens = pd.DataFrame({"지표": c, "일치도": round(rho(c), 2)} for c in
                    ["버즈 유지율", "마지막2주÷최고주", "최종주 빼고 2주÷중앙값", "후반1/3÷앞2/3",
                     "최종주÷중앙값", "시청률 유지율", "버즈 규모"])
print(sens.to_string(index=False))
print(f"\n버즈 유지율 vs 버즈 규모 일치도: {spearman(pre['버즈 유지율'], pre['버즈 규모']):.2f}")
pre.round(3).to_csv("data/processed/ch3_prefinale.csv", index=False, encoding="utf-8-sig")
sens.to_csv("data/processed/ch3_prefinale_sensitivity.csv", index=False, encoding="utf-8-sig")

# ---------- 2. 그래프 10 ----------
SHORT = {"모두가 자신의 무가치함과 싸우고 있다": "모두가 자신의…", "오늘부터 인간입니다만": "오늘부터 인간입니다만",
         "오늘도 매진했습니다": "오늘도 매진했습니다"}
OFFSET = {"오늘부터 인간입니다만": (0, 16), "오늘도 매진했습니다": (0, -20),       # 0점 근처 글자 겹침 방지
          "아기가 생겼어요": (-10, 16), "샤이닝": (8, -20)}
fig, ax = plt.subplots(figsize=(10, 6.5))
size = pre["버즈 규모"] / pre["버즈 규모"].max() * 1500 + 60     # 점 크기 = 작품 규모
ax.scatter(pre["버즈 유지율"], pre["잔존 점수"], s=size, color="#2e86ab", alpha=0.6,
           edgecolor="black", linewidth=0.6)
for _, p in pre.iterrows():
    dx, dy = OFFSET.get(p["title"], (10, 6))
    ax.annotate(f"{SHORT.get(p['title'], p['title'])} ({int(p['종영 후 잔존(주)'])}주)",
                (p["버즈 유지율"], p["잔존 점수"]), xytext=(dx, dy), textcoords="offset points", fontsize=9)
ax.axvline(1.0, color="gray", lw=1, ls="--")
ax.set_xlim(0.42, 1.32)
ax.set_ylim(-2.5, 17)
ax.text(0.97, 16.3, "← 종영 전에 식음", ha="right", fontsize=9, color="gray")
ax.text(1.03, 16.3, "끝까지 유지 →", ha="left", fontsize=9, color="gray")
ax.set_xlabel("종영 전 버즈 유지율 (마지막 2주 평균 ÷ 방영 기간 중앙값, 라코이)")
ax.set_ylabel("종영 후 넷플릭스 잔존 점수 (Σ(11 - 순위))")
ax.set_title(f"그래프 10. 종영 전 온라인 관심 vs 종영 후 넷플릭스 잔존 (일치도 {rho('버즈 유지율'):.2f}, 10편)\n"
             "점 크기 = 작품 규모(주 버즈 중앙값), 괄호 = 종영 후 TOP 10 잔존 주 수", fontsize=11)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("images/10_prefinale_retention.png", dpi=150)
print("\n저장: images/10_prefinale_retention.png, data/processed/ch3_prefinale.csv, ch3_prefinale_sensitivity.csv")
