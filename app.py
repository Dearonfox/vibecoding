from datetime import datetime, timedelta

import pandas as pd
import requests
import sqlite3
import streamlit as st
from dotenv import load_dotenv

from backend.database import CREATE_TABLE_SQL, get_connection
from backend.weather_api import (
    CATEGORY_LABELS,
    SKY_MAP,
    build_items_dataframe,
    fetch_short_term_forecast,
    get_latest_base_datetime,
    save_forecast_dataframe,
)


load_dotenv()


def ensure_database():
    with get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()


def load_from_db(fcst_date="", category="", nx=None, ny=None):
    query = "SELECT * FROM weather_forecast WHERE 1=1"
    params = []

    if fcst_date:
        query += " AND fcst_date = ?"
        params.append(fcst_date)    
    if category:
        query += " AND category = ?"
        params.append(category)
    if nx is not None:
        query += " AND nx = ?"
        params.append(nx)
    if ny is not None:
        query += " AND ny = ?"
        params.append(ny)

    query += " ORDER BY fcst_date, fcst_time, category"

    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def summarize_weather(df):
    if df.empty:
        return {}

    current_time = datetime.now().strftime("%H%M")
    today = datetime.now().strftime("%Y%m%d")
    today_rows = df[df["fcst_date"] == today].copy()
    if today_rows.empty:
        today_rows = df.copy()

    today_rows["time_gap"] = today_rows["fcst_time"].apply(
        lambda value: abs(int(value) - int(current_time)) if str(value).isdigit() else 9999
    )
    nearest_time = today_rows.sort_values("time_gap")["fcst_time"].iloc[0]
    snapshot = today_rows[today_rows["fcst_time"] == nearest_time]

    result = {}
    for code in ["TMP", "POP", "SKY"]:
        matched = snapshot[snapshot["category"] == code]
        if not matched.empty:
            result[code] = matched.iloc[0]["fcst_value"]
    result["fcst_time"] = nearest_time
    result["fcst_date"] = snapshot.iloc[0]["fcst_date"] if not snapshot.empty else ""
    return result


def make_chart_df(df, category):
    filtered = df[df["category"] == category].copy()
    if filtered.empty:
        return filtered

    filtered["forecast_at"] = pd.to_datetime(
        filtered["fcst_date"] + filtered["fcst_time"], format="%Y%m%d%H%M", errors="coerce"
    )
    filtered["fcst_value_num"] = pd.to_numeric(filtered["fcst_value"], errors="coerce")
    return filtered.dropna(subset=["forecast_at", "fcst_value_num"])


def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def main():
    st.set_page_config(page_title="단기예보 날씨 조회 앱", layout="wide")
    ensure_database()

    st.title("단기예보 날씨 조회 앱")
    st.write("공공데이터포털 단기예보 조회 API를 불러와 SQLite에 저장하고 화면에서 조회합니다.")

    now = datetime.now()
    default_base = get_latest_base_datetime(now - timedelta(minutes=10))

    with st.sidebar:
        st.header("조회 조건")
        location_name = st.text_input("지역 이름", value="서울")
        nx = st.number_input("격자 X(nx)", min_value=1, max_value=149, value=60, step=1)
        ny = st.number_input("격자 Y(ny)", min_value=1, max_value=253, value=127, step=1)
        base_date = st.text_input("발표일자", value=default_base["base_date"])
        base_time = st.selectbox("발표시각", options=default_base["valid_times"], index=default_base["index"])
        category_filter = st.selectbox("카테고리 필터", options=[""] + list(CATEGORY_LABELS.keys()), format_func=lambda x: "전체" if x == "" else f"{x} - {CATEGORY_LABELS[x]}")
        fetch_button = st.button("API 호출 후 DB 저장", use_container_width=True)
        load_button = st.button("DB 조회", use_container_width=True)

    api_result = {}
    latest_df = pd.DataFrame()

    if fetch_button:
        payload = fetch_short_term_forecast(
            base_date=base_date,
            base_time=base_time,
            nx=int(nx),
            ny=int(ny),
        )
        api_result = payload["api_result"]
        if api_result.get("resultCode") == "00":
            latest_df = build_items_dataframe(payload["items"], location_name=location_name, nx=int(nx), ny=int(ny))
            saved_count = save_forecast_dataframe(latest_df)
            st.success(f"{saved_count}건을 weather_forecast.db에 저장했습니다.")
        else:
            st.error(f"API 오류 - resultCode: {api_result.get('resultCode')}, resultMsg: {api_result.get('resultMsg')}")

    db_df = pd.DataFrame()
    if load_button or fetch_button:
        db_df = load_from_db(fcst_date="", category=category_filter, nx=int(nx), ny=int(ny))

    if api_result and api_result.get("resultCode") == "00":
        st.info(f"API 응답 - resultCode: {api_result.get('resultCode')}, resultMsg: {api_result.get('resultMsg')}")

    source_df = db_df if not db_df.empty else latest_df

    summary = summarize_weather(source_df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("예보 건수", len(source_df))
    col2.metric("기온", f"{summary.get('TMP', '-') }℃")
    col3.metric("강수확률", f"{summary.get('POP', '-') }%")
    col4.metric("하늘상태", SKY_MAP.get(str(summary.get("SKY", "-")), summary.get("SKY", "-")))

    st.subheader("카테고리 설명")
    st.write(
        "TMP: 1시간 기온, POP: 강수확률, SKY: 하늘상태, PTY: 강수형태, REH: 습도, WSD: 풍속, TMN: 일 최저기온, TMX: 일 최고기온"
    )

    st.subheader("예보 차트")
    chart_category = st.selectbox("차트 카테고리", options=["TMP", "POP", "REH", "WSD"])
    chart_df = make_chart_df(source_df, chart_category)
    if not chart_df.empty:
        st.line_chart(chart_df.set_index("forecast_at")["fcst_value_num"])
    else:
        st.info("차트로 표시할 숫자형 데이터가 없습니다.")

    st.subheader("예보 데이터 표")
    if not source_df.empty:
        st.dataframe(source_df, use_container_width=True)
        st.download_button(
            "CSV 다운로드",
            data=to_csv_bytes(source_df),
            file_name="weather_forecast.csv",
            mime="text/csv",
        )
    else:
        st.warning("표시할 데이터가 없습니다. API 호출 또는 DB 조회를 먼저 실행하세요.")


if __name__ == "__main__":
    main()
