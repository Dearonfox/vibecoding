# 단기예보 조회 웹 앱

공공데이터포털의 단기예보 조회 API를 활용해 날씨 정보를 조회하고 시각화하는 웹 앱입니다.  
Python, FastAPI, Streamlit, SQLite를 사용해 만들었습니다.

## 프로젝트 소개

- 공공데이터포털 단기예보 API를 호출합니다.
- 응답 데이터를 pandas DataFrame으로 변환합니다.
- SQLite 데이터베이스에 저장합니다.
- FastAPI로 CRUD와 데이터 적재 기능을 제공합니다.
- Streamlit으로 지도, 지표, 차트 중심의 화면을 제공합니다.

## 기술 스택

- Python
- FastAPI
- Streamlit
- SQLite
- requests
- pandas

## 프로젝트 구조

```text
코덱스/
├─ backend/
│  ├─ __init__.py
│  ├─ database.py
│  ├─ main.py
│  ├─ schemas.py
│  └─ weather_api.py
├─ frontend/
│  └─ app.py
├─ app.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

## 주요 기능

- 단기예보 API 호출
- JSON 응답 파싱
- pandas DataFrame 변환
- SQLite 저장
- FastAPI CRUD
- 지역별 조회
- 전국 지도 시각화
- 기온, 강수확률, 하늘상태 요약 표시
- 차트 시각화
- CSV 다운로드
- API 오류 시 resultCode, resultMsg 표시

## 데이터베이스 설계

데이터베이스 파일명은 `weather_forecast.db`입니다.

테이블명: `weather_forecast`

주요 컬럼:

- `id`
- `base_date`
- `base_time`
- `fcst_date`
- `fcst_time`
- `forecast_datetime`
- `category`
- `fcst_value`
- `nx`
- `ny`
- `location_name`
- `created_at`
- `updated_at`

중복 저장 방지를 위해 아래 조합에 UNIQUE 제약조건을 두었습니다.

- `base_date`
- `base_time`
- `fcst_date`
- `fcst_time`
- `category`
- `nx`
- `ny`

## 주요 카테고리 설명

- `TMP`: 기온
- `POP`: 강수확률
- `SKY`: 하늘상태
- `PTY`: 강수형태
- `REH`: 습도
- `WSD`: 풍속

## 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

Windows에서 `pip`가 안 될 경우:

```bash
py -3 -m pip install -r requirements.txt
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래처럼 입력합니다.

```env
WEATHER_API_KEY=발급받은_API_인증키
```

### 3. 백엔드 실행

```bash
uvicorn backend.main:app --reload
```

또는

```bash
py -3 -m uvicorn backend.main:app --reload
```

### 4. 프론트엔드 실행

```bash
streamlit run frontend/app.py
```

또는

```bash
py -3 -m streamlit run frontend/app.py
```

## 테스트 방법

1. 백엔드 서버를 실행합니다.
2. 프론트엔드 서버를 실행합니다.
3. 화면 왼쪽에서 지역을 선택합니다.
4. `이 지역만 불러오기` 또는 `선택한 도시들 한 번에 불러오기`를 누릅니다.
5. 지도와 차트가 정상적으로 표시되는지 확인합니다.
6. CSV 다운로드가 되는지 확인합니다.

FastAPI 테스트 문서:

- `http://127.0.0.1:8000/docs`

## API 출처

- 공공데이터포털 단기예보 조회 서비스
- 기상청 단기예보 조회 API

## 제출 시 주의사항

- `.env` 파일은 GitHub에 올리면 안 됩니다.
- `weather_forecast.db` 파일도 보통 제외하는 것이 좋습니다.
- 저장소는 Public으로 설정합니다.

## 실행 화면 예시

실행 후 아래와 같은 흐름으로 사용할 수 있습니다.

- 지역 선택
- API 데이터 저장
- 지도 확인
- 차트 확인
- CSV 다운로드
