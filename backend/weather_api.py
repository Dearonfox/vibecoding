import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from backend.database import get_connection


load_dotenv()

API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
CATEGORY_LABELS = {
    "TMP": "기온",
    "POP": "강수확률",
    "SKY": "하늘상태",
    "PTY": "강수형태",
    "REH": "습도",
    "WSD": "풍속",
    "TMN": "최저기온",
    "TMX": "최고기온",
    "VEC": "풍향",
    "UUU": "동서바람성분",
    "VVV": "남북바람성분",
}
SKY_MAP = {"1": "맑음", "3": "구름많음", "4": "흐림"}
PTY_MAP = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}


def get_api_key():
    return os.getenv("WEATHER_API_KEY", "").strip()


def get_latest_base_datetime(now=None):
    if now is None:
        now = datetime.now()

    valid_times = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]
    current_hhmm = now.strftime("%H%M")
    selected = valid_times[-1]
    base_date = now.strftime("%Y%m%d")

    for time_code in valid_times:
        if current_hhmm >= time_code:
            selected = time_code

    if current_hhmm < valid_times[0]:
        yesterday = now.fromtimestamp(now.timestamp() - 86400)
        base_date = yesterday.strftime("%Y%m%d")
        selected = valid_times[-1]

    return {
        "base_date": base_date,
        "base_time": selected,
        "valid_times": valid_times,
        "index": valid_times.index(selected),
    }


def fetch_short_term_forecast(base_date, base_time, nx, ny, num_of_rows=1000, page_no=1):
    api_key = get_api_key()
    if not api_key:
        return {
            "api_result": {
                "resultCode": "ENV",
                "resultMsg": "WEATHER_API_KEY 환경변수가 설정되지 않았습니다.",
            },
            "items": [],
            "raw": {},
        }

    params = {
        "serviceKey": api_key,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }
    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()
    header = payload.get("response", {}).get("header", {})
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", {}).get("item", []) or []

    return {
        "api_result": {
            "resultCode": str(header.get("resultCode", "")),
            "resultMsg": str(header.get("resultMsg", "")),
        },
        "items": items,
        "raw": payload,
    }


def build_items_dataframe(items, location_name, nx, ny):
    if not items:
        return pd.DataFrame(
            columns=[
                "base_date",
                "base_time",
                "fcst_date",
                "fcst_time",
                "forecast_datetime",
                "category",
                "fcst_value",
                "nx",
                "ny",
                "location_name",
            ]
        )

    df = pd.DataFrame(items).copy()
    df = df.rename(
        columns={
            "baseDate": "base_date",
            "baseTime": "base_time",
            "fcstDate": "fcst_date",
            "fcstTime": "fcst_time",
            "fcstValue": "fcst_value",
        }
    )
    df["nx"] = int(nx)
    df["ny"] = int(ny)
    df["location_name"] = location_name
    df["forecast_datetime"] = df["fcst_date"].astype(str) + df["fcst_time"].astype(str)
    return df[
        [
            "base_date",
            "base_time",
            "fcst_date",
            "fcst_time",
            "forecast_datetime",
            "category",
            "fcst_value",
            "nx",
            "ny",
            "location_name",
        ]
    ]


def save_forecast_dataframe(df):
    if df.empty:
        return 0

    records = df.to_dict(orient="records")
    query = """
    INSERT OR IGNORE INTO weather_forecast (
        base_date, base_time, fcst_date, fcst_time, forecast_datetime,
        category, fcst_value, nx, ny, location_name
    ) VALUES (
        :base_date, :base_time, :fcst_date, :fcst_time, :forecast_datetime,
        :category, :fcst_value, :nx, :ny, :location_name
    )
    """

    with get_connection() as conn:
        cursor = conn.executemany(query, records)
        conn.commit()
    return cursor.rowcount if cursor.rowcount is not None else 0
