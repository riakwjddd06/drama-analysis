"""그래프 02: 작품별 TV 곡선 + 넷플릭스 순위 곡선 모음 (유형별 정렬)"""
import os
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
os.makedirs("images", exist_ok=True)

TV_COLOR, NF_COLOR, INK, MUTED = "#2a78d6", "#eb6834", "#2b2b2b", "#8a8a85"
ORDER = ["동반 흥행형", "TV 뒷심형", "넷플릭스 강세형", "동반 하락형", "넷플릭스 미진입"]

tv = pd.read_csv("data/processed/tv_weekly.csv")
nf = pd.read_csv("data/processed/nf_kr_weekly.csv")
types = pd.read_csv("data/processed/ch1_types.csv")
types["order"] = types["quadrant"].map(ORDER.index)
types = types.sort_values(["order", "tv_ratio"], ascending=[True, False]).reset_index(drop=True)

fig = plt.figure(figsize=(17, 11))
top, bottom = fig.subfigures(2, 1, hspace=0.04)
grids = [sf.subplots(2, 5, gridspec_kw={"height_ratios": [1.3, 1], "hspace": 0.08})
         for sf in (top, bottom)]
for i, row in types.iterrows():
    axes, c = grids[i // 5], i % 5
    ax_tv, ax_nf = axes[0, c], axes[1, c]
    t = tv[tv["title"] == row["title"]]
    last = t["week_no"].max()
    weeks = range(1, last + 3)                       # 종영 후 2주까지
    n = nf[nf["title"] == row["title"]].set_index("week_no")["weekly_rank"].reindex(weeks)

    # 위: TV 시청률 (1주차 = 100)
    t_full = t.set_index("week_no")["rating_idx"].reindex(range(1, last + 1))  # 결방 주는 끊김
    ax_tv.plot(t_full.index, t_full.values, color=TV_COLOR, lw=2, marker="o", ms=4)
    pk = t_full.idxmax()
    ax_tv.plot(pk, t_full.max(), "o", ms=9, mfc="white", mec=TV_COLOR, mew=2)
    ax_tv.axhline(100, color=MUTED, lw=0.8, ls=":")
    ax_tv.set_title(f"{row['title']}\n{row['quadrant']}  ·  민감도 {row['sensitivity']}",
                    fontsize=10, color=INK, loc="left")

    # 아래: 넷플릭스 한국 순위 (TOP 10 밖은 빈칸 → 선이 끊김)
    ax_nf.plot(n.index, n.values, color=NF_COLOR, lw=2, marker="o", ms=4)
    if n.notna().any():
        b = n.idxmin()
        ax_nf.plot(b, n.min(), "o", ms=9, mfc="white", mec=NF_COLOR, mew=2)
    ax_nf.set_ylim(10.5, 0.5)                        # 순위는 뒤집어서 1위가 위
    ax_nf.set_yticks([1, 5, 10])

    for ax in (ax_tv, ax_nf):
        ax.axvline(last + 0.5, color=MUTED, lw=1, ls="--")   # 종영
        ax.set_xlim(0.5, last + 2.5)
        ax.set_xticks(list(weeks))
        ax.tick_params(labelsize=8, colors=MUTED)
        ax.grid(axis="y", color="#e6e6e3", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    ax_tv.tick_params(labelbottom=False)
    if c == 0:
        ax_tv.set_ylabel("TV 시청률\n(1주차=100)", fontsize=9, color=INK)
        ax_nf.set_ylabel("넷플릭스\n한국 순위", fontsize=9, color=INK)
    ax_nf.set_xlabel("방영 주차", fontsize=8, color=MUTED)

top.subplots_adjust(top=0.74, bottom=0.08, left=0.06, right=0.99, wspace=0.25)
bottom.subplots_adjust(top=0.84, bottom=0.08, left=0.06, right=0.99, wspace=0.25)
fig.suptitle("그래프 02. TV 시청률 곡선과 넷플릭스 한국 순위 곡선의 유형", fontsize=14, color=INK, x=0.01, ha="left")
fig.text(0.01, 0.955,
         "파란선: TV 시청률(1주차=100)  ·  주황선: 넷플릭스 한국 TOP 10 순위(위가 1위, 끊긴 곳은 TOP 10 밖)  ·  "
         "흰 원: 각 지표의 최고점  ·  점선: 종영\n"
         "순위(서열)와 시청률(비율)은 직접 비교할 수 없어, 절대 수치가 아니라 오르내리는 시점과 곡선 모양을 비교한다. "
         "넷플릭스가 주간 데이터라 주 단위로 집계했다.",
         fontsize=9, color=MUTED, va="top")
fig.savefig("images/02_curve_types.png", dpi=150)
print("저장: images/02_curve_types.png")