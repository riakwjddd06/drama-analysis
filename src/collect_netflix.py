
# src/collect_netflix.py
# 넷플릭스 공식 TOP 10 데이터(전체 기간)를 내려받아 data/raw/에 원본 그대로 저장한다.
import requests
import pandas as pd

BASE = "https://www.netflix.com/tudum/top10/data/"

for name in ["all-weeks-global.tsv", "all-weeks-countries.tsv"]:
    res = requests.get(BASE + name, timeout=120)
    res.raise_for_status()                      # 다운로드 실패면 여기서 멈춤
    path = f"data/raw/{name}"
    with open(path, "wb") as f:
        f.write(res.content)                    # 받은 파일을 그대로 저장

    df = pd.read_csv(path, sep="\t")            # 잘 받았는지 확인용
    print(name, "저장 완료:", df.shape, "| 최신 주:", df["week"].max())