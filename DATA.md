# DATA.md — 데이터 수집 기록과 데이터 사전

분석에 쓴 원본 데이터는 모두 `data/raw/`에 동봉했다. 이 문서는 각 파일을 **어디서, 어떻게, 언제** 받았는지와 컬럼의 뜻을 기록한다. 같은 조건으로 다시 받으면 같은 데이터를 얻을 수 있도록 조회 조건을 그대로 적었다.

## 1. 수집 기록

| 데이터 | 파일 | 출처 | 수집 방법 | 수집일 | 기간 · 단위 |
|---|---|---|---|---|---|
| TV 시청률 | `data/raw/ratings.csv` | 네이버 드라마 정보 '시청률' 탭 (제공: 닐슨코리아, 전국) | 작품별 화면을 보고 옮겨 적음 → 닐슨코리아 공식 자료와 대조 | 2026-10-20 | 2026-01-03 ~ 07-25, 회차별 |
| 넷플릭스 TOP 10 | `data/raw/all-weeks-countries.tsv`, `all-weeks-global.tsv` | [Netflix Tudum TOP 10](https://www.netflix.com/tudum/top10) | `python src/collect_netflix.py` | 2026-10-20 | 주별(월~일), `week` = 그 주 일요일 |
| 라코이 화제성 | `data/raw/racoi/racoi_ibuzz_20251229_20260802.xlsx` | [RACOI](https://www.racoi.or.kr) 인터넷반응DB (한국방송광고진흥공사) | 인터넷반응 → 인터넷반응DB → 기간별다운 → EXCEL다운 (아래 1-0) | 2026-10-30 | 2026년 1~31주차(2025-12-29 ~ 2026-08-02), 주별 |
| 구글 검색 관심도 | `data/raw/google/kr_batch1.csv`, `kr_batch2a.csv`, `kr_batch2b.csv`, `kr_batch3.csv` | Google Trends, **주제(Topic)**, 대한민국 | 아래 링크에서 "시간 흐름에 따른 관심도" CSV 다운로드 | 1·3: 2026-10-20, 2a·2b: 2026-10-30 | 2025-12-15 ~ 2026-09-09, 일별 |
| 네이버 검색량 | `data/raw/naver/batch1~3.xlsx` | 네이버 데이터랩 검색어 트렌드 | 웹 화면에서 엑셀 다운로드 | 2026-10-20 | 2025-12-01 ~ 2026-10-15, 일별 |
| 펀덱스 화제성 | `data/raw/fundex.csv` | 굿데이터코퍼레이션 펀덱스 TV-OTT 드라마 화제성 (보도 기사) | 주차별 기사에서 우리 10편의 순위·점유율만 옮김 | 2026-10-23 | 2026년 2~30주차 중 21주, 주별 |

### 1-0. 라코이 다운로드 조건 (2장 메인)

[데이터 다운로드 화면](https://www.racoi.or.kr/kobaco/excel/response.do?menu=ibuzz)에서 아래처럼 설정했다.

| 항목 | 설정 |
|---|---|
| 분류 선택 | 인터넷반응 DB |
| 기간 | 2025-12-29 ~ 2026-08-02 |
| 드라마 | 전체 (예능·시사/정보는 끔) |
| 채널 · 카테고리 | 전체 |

엑셀에는 주차별 프로그램마다 시청자 버즈(게시글·댓글·동영상 조회), 미디어 버즈(뉴스·동영상 수), 각 점유율, 닐슨 시청자 수·시청률(가구·2049)이 들어 있다. 라코이는 **방영 중인 주만** 집계한다. 받은 파일에서 10편 모두 1주차부터 마지막 방영 주까지 빠짐없이 확인했다(오늘부터 인간입니다만의 빈 주 1개는 설 연휴 결방).

### 1-1. 구글 트렌드 조회 조건 (일별 흐름 분석, 3장 보조)

검색어가 아니라 **주제(Topic)** 로 조회했다. 주제 ID(mid)를 링크에 직접 넣어 같은 조건을 재현할 수 있다. 공통 조건: 기간 2025-12-15 ~ 2026-09-09(270일 미만이라 일별 값), 지역 대한민국, 모든 카테고리.

| 작품 | 주제 ID |
|---|---|
| 은애하는 도적님아 | /g/11ww97dpff |
| 오늘부터 인간입니다만 | /g/11wc2qz5hk |
| 언더커버 미쓰홍 | /g/11xmvg43fs |
| 아기가 생겼어요 | /g/11xlzc6s7h |
| 샤이닝 | /g/11xp89zh0v |
| 신이랑 법률사무소 | /g/11x2w8wlfq |
| 모두가 자신의 무가치함과 싸우고 있다 | /g/11mzt8950d |
| 오늘도 매진했습니다 | /g/11ygm_9xmp |
| 멋진 신세계 | /g/11yh37vkw5 |
| 김부장 | /g/11n3r2lt31 |

| 파일 | 묶음 구성 | 조회 링크 |
|---|---|---|
| kr_batch1 | 신이랑(기준), 은애하는 도적님아, 오늘부터 인간입니다만, 아기가 생겼어요, 샤이닝 | [링크](https://trends.google.com/trends/explore?date=2025-12-15%202026-09-09&geo=KR&hl=ko&q=%2Fg%2F11x2w8wlfq,%2Fg%2F11ww97dpff,%2Fg%2F11wc2qz5hk,%2Fg%2F11xlzc6s7h,%2Fg%2F11xp89zh0v) |
| kr_batch2a | 신이랑(기준), 언더커버 미쓰홍, 모두가…, 언더커버 미쓰홍 중복 주제(/g/11nr4zc6q8, 확인용) | [링크](https://trends.google.com/trends/explore?date=2025-12-15%202026-09-09&geo=KR&hl=ko&q=%2Fg%2F11x2w8wlfq,%2Fg%2F11xmvg43fs,%2Fg%2F11mzt8950d,%2Fg%2F11nr4zc6q8) |
| kr_batch2b | 오늘도 매진했습니다, 김부장, 멋진 신세계, 모두가…(연결용) | [링크](https://trends.google.com/trends/explore?date=2025-12-15%202026-09-09&geo=KR&hl=ko&q=%2Fg%2F11ygm_9xmp,%2Fg%2F11n3r2lt31,%2Fg%2F11yh37vkw5,%2Fg%2F11mzt8950d) |
| kr_batch3 | 신이랑(기준), 오늘도 매진했습니다, 은애하는 도적님아(검증용) | [링크](https://trends.google.com/trends/explore?date=2025-12-15%202026-09-09&geo=KR&hl=ko&q=%2Fg%2F11x2w8wlfq,%2Fg%2F11ygm_9xmp,%2Fg%2F11ww97dpff) |

처음 받은 묶음 2(`google/old/kr_batch2_old.csv`)는 김부장이 너무 커서 다른 작품이 0~5로 눌려 2a·2b로 나눠 다시 받았다.

### 1-2. 네이버 데이터랩 조회 조건 (검증용)

공통 조건: 기간 2025-12-01 ~ 2026-10-15, 일간, 전체 기기·성별·연령. 주제어마다 검색어 4개를 같은 규칙으로 넣었다: "제목 드라마", "제목(붙여쓰기) 드라마", "제목 주연1", "제목 주연2"(크레딧 상위 2명).

| 파일 | 주제어 |
|---|---|
| batch1.xlsx | 은애하는 도적님아(기준), 오늘부터 인간입니다만, 언더커버 미쓰홍, 아기가 생겼어요, 샤이닝 |
| batch2.xlsx | 은애하는 도적님아(기준), 신이랑 법률사무소, 모두가 자신의 무가치함과 싸우고 있다, 오늘도 매진했습니다, 멋진 신세계 |
| batch3.xlsx | 은애하는 도적님아(기준), 김부장 |

이 방식은 제목 종류에 따라 잡히는 검색 비율이 달라 메인 지표에서 제외하고 검증용으로만 썼다(REPORT 4-3). 구글 트렌드도 저신뢰 작품이 4편이라 화제성 메인 지표는 라코이로 정했다.

### 1-3. 펀덱스 출처

"확인 범위"는 기사 본문에서 확인된 순위 수 / 점유율 수다. 10위까지 다 나온 주에서만 빠진 작품을 "TOP 10 밖"으로 볼 수 있다. 순위 번호가 빠진 주는 점유율 크기 순으로 순위를 매겼다.

| 주차 | 주 시작일(월) | 확인 범위 | 기사 |
|---|---|---|---|
| 2 | 2026-01-05 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15932896) |
| 3 | 2026-01-12 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15939435) |
| 5 | 2026-01-26 | 10/5 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15952232) |
| 6 | 2026-02-02 | 6/3 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15963174) |
| 7 | 2026-02-09 | 10/5 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15978370) |
| 8 | 2026-02-16 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15982991) |
| 9 | 2026-02-23 | 5/5 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=15990273) |
| 11 | 2026-03-09 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16007258) |
| 13 | 2026-03-23 | 7/7 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16021366) |
| 14 | 2026-03-30 | 10/7 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16027632) |
| 18 | 2026-04-27 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16052160) |
| 19 | 2026-05-04 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16058287) |
| 20 | 2026-05-11 | 9/9 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16064897) |
| 22 | 2026-05-25 | 9/9 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16078174) |
| 23 | 2026-06-01 | 10/8 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16084637) |
| 25 | 2026-06-15 | 8/8 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16107859) |
| 26 | 2026-06-22 | 1/0 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16118486) |
| 27 | 2026-06-29 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16126662) |
| 28 | 2026-07-06 | 1/0 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16133829) |
| 29 | 2026-07-13 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16141352) |
| 30 | 2026-07-20 | 10/10 | [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16147682) |

못 찾은 주: 1, 4, 10, 12, 15, 16, 17, 21, 24, 31, 32주차.

### 1-4. 시도했지만 쓰지 않은 데이터

| 데이터 | 시도 내용 | 제외 이유 |
|---|---|---|
| 빅카인즈 뉴스 기사 수 | "은애하는 도적님아"로 검색해 기사 목록 엑셀 다운로드 | 22건뿐(방영 기간 10건, 한 언론사가 59%). 연예 매체가 거의 없어 일별 곡선 검증에 부적합 |
| 네이버 검색 API | API 키 발급 시도 | NAVER API HUB가 결제수단 등록을 요구해 데이터랩 웹 다운로드로 대체 |
| 위키백과 시청률 표 | 수집 코드 작성 | 출처 신뢰성 문제로 네이버 드라마 정보(닐슨코리아)로 대체 |

## 2. 데이터 사전

### data/dramas.csv — 분석 대상 10편

| 컬럼 | 뜻 | 예시 |
|---|---|---|
| title | 작품명(한국어) | 김부장 |
| broadcaster | 방송사 | SBS |
| first_air / last_air | 1화 / 최종화 방영일 | 2026-06-26 |
| episodes | 부작 | 10 |
| nf_title | 넷플릭스 TOP 10 파일의 영문 제목 | Agent Kim Reactivated |
| in_kr_top10, overseas | 넷플릭스 한국 TOP 10 진입 여부, 해외 공개 여부 | Y |

`data/originals.csv`는 같은 기간 넷플릭스 오리지널 8편(보너스 비교군)이다.

### data/raw/ratings.csv — TV 시청률

| 컬럼 | 뜻 |
|---|---|
| title | 작품명 |
| episode | 회차 |
| air_date | 방영일 |
| rating | 시청률(%), 닐슨코리아 전국, 소수점 첫째 자리 |

### data/processed/racoi_weekly.csv — 라코이 주간 화제성 (`load_racoi.py`가 만듦)

| 컬럼 | 뜻 |
|---|---|
| title, week, week_start, week_no | 작품명, 라코이 주차 코드(ISO 연도·주차), 그 주 월요일, 방영 주차 |
| posts, comments | 게시글 수, 댓글 수 (블로그·카페·커뮤니티 등) |
| buzz | 시청자 버즈 = posts + comments (2장 메인 지표) |
| views | 동영상 조회수 |
| news, videos | 뉴스 기사 수, 동영상 수 (미디어 버즈) |
| rating_hh, rating_2049 | 닐슨 주간 시청률(%), 가구·2049 |

### data/raw/fundex.csv — 펀덱스 화제성

| 컬럼 | 뜻 |
|---|---|
| iso_week | 펀덱스 발표 주차(월~일) |
| week_start | 그 주 월요일 |
| rank | TV-OTT 통합 드라마 화제성 순위 |
| title | 작품명 |
| share | 화제성 점유율(%), 기사에 없으면 빈칸 |

### data/processed/ — 코드가 만드는 파일

| 파일 | 만드는 코드 | 내용 |
|---|---|---|
| google_kr_daily.csv | load_google.py | title, date, value_level(10편 공통 눈금), value_shape(작품별 최고 날 = 100), batch_used |
| tv_weekly.csv | ch1_curves.py | title, week_no, rating(주차 평균), rating_idx(1주차 = 100) |
| nf_kr_weekly.csv | ch1_curves.py | title, week_no, week, weekly_rank (TOP 10 밖은 행 없음) |
| ch1_types.csv | ch1_curves.py | 작품별 TV·넷플릭스 유형, 2×2 분류, 민감도 |
| ch2_sources.csv, ch2_gap.csv | ch2_gap.py | 출처별 원값(라코이·펀덱스·구글·네이버), 순위, 갭 |
| racoi_weekly.csv | load_racoi.py | 위 설명 참고 |
| ch3_halflife.csv, ch3_sensitivity.csv | ch3_halflife.py | 구글 기준 최고점 도달, 종영일 관심, 반감기, 기준별 반감기 |
| ch3_netflix.csv | ch3_netflix.py | 종영 주 넷플릭스 순위, 종영 후 TOP 10 잔존 주 수, 잔존 점수, 구글 반감기 |
| weekday_effect.csv | graph07_trend_weekday.py | 방송일 ÷ 비방송일 배수 |

**방영 주차(week_no):** 1화가 들어 있는 월~일 주 = 1주차. 넷플릭스 `week`(일요일)는 6일을 빼 월요일로 바꾼 뒤 계산했다.

## 3. 참고 사항

- **시청률 기준 차이:** 지상파(KBS2·SBS)는 "13개 지역, 가구", 종편·케이블(tvN·JTBC·채널A)은 "전국, 유료플랫폼 가입 가구" 기준이다.
- **반올림:** 네이버 화면은 소수점 첫째 자리까지 표시한다.
- **2부 편성:** 한 회가 1·2부로 나뉜 경우 높은 쪽 시청률을 썼다.
- **결방:** 오늘부터 인간입니다만은 설 연휴(2/13~14) 결방.
- **같은 날 2회:** 샤이닝은 금요일마다 2회씩 방영해 air_date가 같은 회차가 있다.
- **구글 값:** 0~100 정수이며, 검색이 기준보다 적은 날은 0, 1 미만은 `<1`로 표시된다(코드에서 0.5로 처리). 표본으로 계산되어 다시 받으면 조금씩 달라질 수 있다.
- **이상값:** 멋진 신세계 8/2~3은 제외(관련 기사 없음, 네이버 변화 없음). 멋진 신세계 6/14, 김부장 8/8~9는 드라마 관련 이슈로 확인해 유지(REPORT 4-2).

## 4. 라이선스

- 시청률은 닐슨코리아 발표치를 네이버 드라마 정보에서 재인용했으며, 학습 목적으로만 사용한다.
- 라코이 데이터는 한국방송광고진흥공사 RACOI 사이트가 제공하는 Excel 다운로드로 받았으며, 학습 목적으로만 사용한다.
- 넷플릭스·구글·네이버 데이터는 각 서비스의 이용약관을 따르며, 학습 목적으로만 사용한다.
- 펀덱스 순위·점유율은 보도 기사에서 인용했으며, 출처 링크를 위에 기록했다.
