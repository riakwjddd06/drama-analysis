"""3장 (C안): 종영 후 넷플릭스 한국 TOP 10 잔존(메인) + 구글 검색 반감기(보조) + 그래프 06
먼저 ch1_curves.py, ch3_halflife.py를 실행해 둘 것"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

tv = pd.read_csv("data/processed/tv_weekly.csv")
nf = pd.read_csv("data/processed/nf_kr_weekly.csv")
types = pd.read_csv("data/processed/ch1_types.csv")[["title", "quadrant"]]
hl = pd.read_csv("data/processed/ch3_halflife.csv")[["title", "반감기(일)", "종영 전 반감", "저신뢰"]]

last_week = tv.groupby("title")["week_no"].max()          # 최종화가 들어 있는 방영 주차

rows = []
for title, last in last_week.items():
    ranks = nf[nf["title"] == title].set_index("week_no")["weekly_rank"]
    # 종영 다음 주부터 TOP 10에 '연속으로' 남은 주 수 (한 번 빠지면 거기서 멈춤)
    stay, w = 0, last + 1
    while w in ranks.index:
        stay += 1
        w += 1
    after = ranks[(ranks.index > last) & (ranks.index <= last + stay)]
    rows.append({
        "title": title,
        "종영 주 순위": ranks.get(last),                        # 없으면 TOP 10 밖
        "종영 후 잔존(주)": stay,
        "잔존 점수": int((11 - after).sum()),                    # 잔존 주의 (11 - 순위) 합: 같은 주 수일 때 순위가 높을수록 큼
        "TOP10 체류 합계(주)": len(ranks),
    })
res = pd.DataFrame(rows).merge(types, on="title").merge(hl, on="title")
res = res.sort_values(["종영 후 잔존(주)", "잔존 점수"], ascending=False).reset_index(drop=True)

# 구글 반감기는 '종영 전 반감'이면 종영 후 속도로 볼 수 없으므로 순위 비교에서 뺌
g = res["반감기(일)"].where(~res["종영 전 반감"])
res["잔존 순위"] = (res["종영 후 잔존(주)"] * 100 + res["잔존 점수"]).rank(ascending=False, method="min").astype(int)
both = res.assign(g=g).dropna(subset=["g"])
rho = both[["종영 후 잔존(주)", "g"]].corr(method="spearman").iloc[0, 1]

pd.set_option("display.width", 220)
print("[작품별 결과]\n", res.to_string(index=False), "\n")
print("[유형별 평균]\n", res.groupby("quadrant")[["종영 후 잔존(주)", "잔존 점수"]].mean().round(2), "\n")
print(f"[교차 검증] 넷플릭스 잔존 vs 구글 반감기 순위 일치도(스피어만): {rho:.2f}  "
      f"(종영 전 반감 작품 제외, {len(both)}편)")
res.to_csv("data/processed/ch3_netflix.csv", index=False)

# ---------- 그래프 06: 종영 후 넷플릭스 한국 TOP 10에 남은 주 수 ----------
INK, MUTED, BAR = "#2b2b2b", "#8a8a85", "#2a78d6"
order = res.iloc[::-1]                                      # 그림에서 위쪽 = 오래 남은 작품
fig, ax = plt.subplots(figsize=(11, 6.2))
y = range(len(order))
ax.barh(y, order["종영 후 잔존(주)"], color=BAR, height=0.6)
for i, (_, r) in zip(y, order.iterrows()):
    title, last = r["title"], int(last_week[r["title"]])
    ranks = nf[nf["title"] == title].set_index("week_no")["weekly_rank"]
    fin = ranks.get(last)
    fin_txt = f"종영 주 {int(fin)}위" if pd.notna(fin) else "종영 주 TOP 10 밖"
    after = [f"{int(ranks[last + k])}위" for k in range(1, r["종영 후 잔존(주)"] + 1)]
    if after:
        txt = f"{r['종영 후 잔존(주)']}주   ({fin_txt} → " + " → ".join(after) + ")"
    else:
        txt = f"0주   ({fin_txt} → 다음 주 바로 TOP 10 밖)"
    ax.text(r["종영 후 잔존(주)"] + 0.06, i, txt, va="center", fontsize=9.5, color=INK)
ax.set_yticks(list(y), order["title"], fontsize=10, color=INK)
ax.set_xlim(0, res["종영 후 잔존(주)"].max() + 2.6)
ax.set_xticks(range(0, int(res["종영 후 잔존(주)"].max()) + 1))
ax.set_xlabel("종영 다음 주부터 넷플릭스 한국 TOP 10에 연속으로 남은 주 수", fontsize=9, color=MUTED)
ax.tick_params(axis="x", labelsize=9, colors=MUTED)
ax.grid(axis="x", color="#e6e6e3", lw=0.6)
ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.suptitle("그래프 06. 종영 후 넷플릭스 한국 TOP 10에 몇 주 더 남았나", x=0.02, ha="left", fontsize=14, color=INK)
fig.text(0.02, 0.905, "괄호 = 종영 주 순위 → 종영 후 주별 순위.  넷플릭스는 주간 상대 순위라 새 작품이 들어오면 밀릴 수 있다.",
         fontsize=9, color=MUTED, va="top")
fig.subplots_adjust(top=0.84, bottom=0.11, left=0.25, right=0.98)
fig.savefig("images/06_after_finale.png", dpi=150)
print("\n저장: images/06_after_finale.png")
