import math
from datetime import datetime, timedelta

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st
from dotenv import load_dotenv

from backend.weather_api import CATEGORY_LABELS, get_latest_base_datetime


load_dotenv()

BACKEND_URL = "http://127.0.0.1:8000"
SKY_MAP = {"1": "맑음", "3": "구름많음", "4": "흐림"}
PTY_MAP = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
PRESET_LOCATIONS = [
    {"name": "서울", "nx": 60, "ny": 127},
    {"name": "인천", "nx": 55, "ny": 124},
    {"name": "수원", "nx": 60, "ny": 121},
    {"name": "춘천", "nx": 73, "ny": 134},
    {"name": "강릉", "nx": 92, "ny": 131},
    {"name": "청주", "nx": 69, "ny": 106},
    {"name": "대전", "nx": 67, "ny": 100},
    {"name": "전주", "nx": 63, "ny": 89},
    {"name": "광주", "nx": 58, "ny": 74},
    {"name": "대구", "nx": 89, "ny": 90},
    {"name": "부산", "nx": 98, "ny": 76},
    {"name": "울산", "nx": 102, "ny": 84},
    {"name": "제주", "nx": 52, "ny": 38},
]


def set_single_location_mode():
    st.session_state["show_all_locations"] = False


def set_all_locations_mode():
    st.session_state["show_all_locations"] = True


def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f9fc;
            color: #1f2937;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border-right: 1px solid #dbe2ea;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5eaf0;
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
        }
        div[data-testid="stMetricLabel"] {
            color: #758592;
            font-weight: 700;
        }
        div[data-testid="stMetricValue"] {
            color: #1f2937;
        }
        .stButton > button {
            background: linear-gradient(135deg, #5383e8 0%, #3b6fe0 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            min-height: 46px;
            box-shadow: 0 10px 24px rgba(83, 131, 232, 0.22);
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #4777da 0%, #2f63d3 100%);
            color: white;
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div {
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #d7dee8;
            color: #1f2937;
            min-height: 46px;
        }
        div[data-baseweb="select"] input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #1f2937 !important;
            -webkit-text-fill-color: #1f2937 !important;
        }
        div[data-testid="stDataFrame"] {
            background: white;
            border-radius: 18px;
            border: 1px solid #e5eaf0;
            padding: 8px;
        }
        .weather-hero {
            background: linear-gradient(135deg, #1f3b8f 0%, #3557d6 55%, #5383e8 100%);
            color: #ffffff;
            padding: 28px 30px;
            border-radius: 24px;
            margin-bottom: 20px;
            box-shadow: 0 22px 48px rgba(53, 87, 214, 0.2);
        }
        .weather-hero h1 {
            margin: 0 0 8px 0;
            font-size: 2rem;
            letter-spacing: -0.03em;
        }
        .weather-hero p {
            margin: 0;
            color: rgba(255, 255, 255, 0.88);
        }
        .weather-badge {
            display: inline-block;
            margin-bottom: 10px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h2, h3 {
            color: #1f2937;
            letter-spacing: -0.02em;
        }
        [data-testid="stCaptionContainer"] {
            color: #758592;
        }
        .opgg-panel {
            background: #ffffff;
            border: 1px solid #e6ebf2;
            border-radius: 20px;
            padding: 18px 20px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
            margin-bottom: 16px;
        }
        .opgg-panel h3 {
            margin: 0 0 6px 0;
            font-size: 1.1rem;
        }
        .opgg-panel p {
            margin: 0;
            color: #758592;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_location_by_name(name):
    for item in PRESET_LOCATIONS:
        if item["name"] == name:
            return item
    return PRESET_LOCATIONS[0]


def post_fetch(base_date, base_time, nx, ny, location_name):
    url = f"{BACKEND_URL}/forecasts/fetch"
    payload = {
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
        "location_name": location_name,
    }
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def get_forecasts(fcst_date="", fcst_time="", category="", nx=None, ny=None):
    url = f"{BACKEND_URL}/forecasts"
    params = {}
    if fcst_date:
        params["fcst_date"] = fcst_date
    if fcst_time:
        params["fcst_time"] = fcst_time
    if category:
        params["category"] = category
    if nx is not None:
        params["nx"] = nx
    if ny is not None:
        params["ny"] = ny

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_multiple_locations(base_date, base_time, locations):
    rows = []
    for location in locations:
        result = post_fetch(base_date, base_time, location["nx"], location["ny"], location["name"])
        rows.append(
            {
                "location_name": location["name"],
                "resultCode": result.get("resultCode"),
                "resultMsg": result.get("resultMsg"),
                "saved_count": result.get("saved_count", 0),
            }
        )
    return pd.DataFrame(rows)


def to_dataframe(items):
    if not items:
        return pd.DataFrame(
            columns=[
                "id",
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
                "created_at",
                "updated_at",
            ]
        )
    return pd.DataFrame(items)


def format_summary(df):
    if df.empty or "category" not in df.columns:
        return {"TMP": "-", "POP": "-", "SKY": "-", "PTY": "-", "time": "-"}

    working = df.copy()
    working["forecast_at"] = pd.to_datetime(
        working["fcst_date"].astype(str) + working["fcst_time"].astype(str),
        format="%Y%m%d%H%M",
        errors="coerce",
    )
    working = working.dropna(subset=["forecast_at"])
    if working.empty:
        return {"TMP": "-", "POP": "-", "SKY": "-", "PTY": "-", "time": "-"}

    now = pd.Timestamp.now()
    unique_times = working[["forecast_at", "fcst_date", "fcst_time"]].drop_duplicates().copy()
    unique_times["time_gap"] = (unique_times["forecast_at"] - now).abs()
    nearest = unique_times.sort_values("time_gap").iloc[0]
    snapshot = working[
        (working["fcst_date"] == nearest["fcst_date"]) & (working["fcst_time"] == nearest["fcst_time"])
    ]

    result = {"time": nearest["fcst_time"]}
    for code in ["TMP", "POP", "SKY", "PTY"]:
        matched = snapshot[snapshot["category"] == code]
        result[code] = matched.iloc[0]["fcst_value"] if not matched.empty else "-"
    return result


def prepare_chart(df, category, location_name):
    if df.empty or "category" not in df.columns:
        return pd.DataFrame()

    filtered = df[df["category"] == category].copy()
    if location_name != "전체":
        filtered = filtered[filtered["location_name"] == location_name]
    if filtered.empty:
        return pd.DataFrame()

    filtered["forecast_at"] = pd.to_datetime(
        filtered["fcst_date"] + filtered["fcst_time"], format="%Y%m%d%H%M", errors="coerce"
    )
    filtered["fcst_value_num"] = pd.to_numeric(filtered["fcst_value"], errors="coerce")
    return filtered.dropna(subset=["forecast_at", "fcst_value_num"])


def highlight_rows(row, target_date, target_time):
    if row.get("fcst_date") == target_date and (not target_time or row.get("fcst_time") == target_time):
        return ["background-color: #e8fff1"] * len(row)
    return [""] * len(row)


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def grid_to_latlon(nx, ny):
    re = 6371.00877 / 5.0
    slat1 = math.radians(30.0)
    slat2 = math.radians(60.0)
    olon = math.radians(126.0)
    olat = math.radians(38.0)
    xo = 43
    yo = 136

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)
    xn = nx - xo
    yn = ro - ny + yo
    ra = math.sqrt(xn * xn + yn * yn)
    alat = (re * sf / ra) ** (1.0 / sn)
    alat = 2.0 * math.atan(alat) - math.pi * 0.5
    theta = 0.0 if abs(xn) <= 0.0 else math.atan2(xn, yn)
    alon = theta / sn + olon
    return math.degrees(alat), math.degrees(alon)


def sky_to_color(sky_value):
    if str(sky_value) == "1":
        return [3, 199, 90, 190]
    if str(sky_value) == "3":
        return [255, 193, 7, 190]
    if str(sky_value) == "4":
        return [107, 114, 128, 190]
    return [33, 150, 243, 180]


def build_map_snapshot(df):
    required = {"location_name", "nx", "ny", "category", "fcst_date", "fcst_time", "fcst_value"}
    if df.empty or not required.issubset(df.columns):
        return pd.DataFrame()

    working = df.copy()
    working["forecast_at"] = pd.to_datetime(
        working["fcst_date"].astype(str) + working["fcst_time"].astype(str),
        format="%Y%m%d%H%M",
        errors="coerce",
    )
    working = working.dropna(subset=["forecast_at"])
    if working.empty:
        return pd.DataFrame()

    now = pd.Timestamp.now()
    time_table = working[["location_name", "nx", "ny", "forecast_at", "fcst_date", "fcst_time"]].drop_duplicates()
    time_table["time_gap"] = (time_table["forecast_at"] - now).abs()
    nearest = (
        time_table.sort_values("time_gap")
        .groupby(["location_name", "nx", "ny"], as_index=False)
        .first()
    )

    merged = working.merge(
        nearest[["location_name", "nx", "ny", "forecast_at"]],
        on=["location_name", "nx", "ny", "forecast_at"],
        how="inner",
    )

    snapshot = (
        merged.pivot_table(
            index=["location_name", "nx", "ny", "fcst_date", "fcst_time", "forecast_at"],
            columns="category",
            values="fcst_value",
            aggfunc="first",
        )
        .reset_index()
    )

    if snapshot.empty:
        return snapshot

    latitudes = []
    longitudes = []
    colors = []
    radii = []
    labels = []

    for _, row in snapshot.iterrows():
        lat, lon = grid_to_latlon(int(row["nx"]), int(row["ny"]))
        latitudes.append(lat)
        longitudes.append(lon)
        colors.append(sky_to_color(row.get("SKY", "")))

        pop_value = pd.to_numeric(pd.Series([row.get("POP")]), errors="coerce").iloc[0]
        if pd.isna(pop_value):
            pop_value = 10
        radii.append(28000 + int(pop_value) * 1300)

        tmp_label = row.get("TMP", "-")
        pop_label = row.get("POP", "-")
        sky_label = SKY_MAP.get(str(row.get("SKY", "")), str(row.get("SKY", "-")))
        labels.append(f"기온 {tmp_label}℃ / 강수확률 {pop_label}% / 하늘 {sky_label}")

    snapshot["lat"] = latitudes
    snapshot["lon"] = longitudes
    snapshot["color"] = colors
    snapshot["radius"] = radii
    snapshot["weather_label"] = labels
    return snapshot


def draw_weather_map(map_df):
    if map_df.empty:
        st.info("지도에 표시할 데이터가 없습니다. 왼쪽에서 지역 불러오기를 먼저 눌러주세요.")
        return

    view_state = pdk.ViewState(
        latitude=float(map_df["lat"].mean()),
        longitude=float(map_df["lon"].mean()),
        zoom=6.3,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.72,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=2,
    )

    tooltip = {
        "html": "<b>{location_name}</b><br/>{weather_label}<br/>예보시각 {fcst_date} {fcst_time}",
        "style": {"backgroundColor": "#0f172a", "color": "white"},
    }

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))


def main():
    st.set_page_config(page_title="날씨 조회 대시보드", layout="wide")
    apply_custom_style()

    if "show_all_locations" not in st.session_state:
        st.session_state["show_all_locations"] = True

    st.markdown(
        """
        <div class="weather-hero">
            <div class="weather-badge">Weather Dashboard</div>
            <h1>날씨 조회 대시보드</h1>
            <p>지도에서 필요한 레이어만 간단하게 보고, 아래에서 차트와 표를 확인할 수 있습니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    default_base = get_latest_base_datetime(datetime.now() - timedelta(minutes=10))
    today = datetime.now().strftime("%Y%m%d")
    default_city_names = ["서울", "인천", "대전", "광주", "대구", "부산", "제주"]

    with st.sidebar:
        st.header("간단 메뉴")
        selected_city = st.selectbox("지역 선택", options=[item["name"] for item in PRESET_LOCATIONS], index=0)
        st.caption("선택한 한 도시만 저장하고 바로 확인할 때 사용합니다.")
        fetch_button = st.button(
            "이 지역만 불러오기",
            use_container_width=True,
            on_click=set_single_location_mode,
        )

        selected_city_names = st.multiselect(
            "전국 지도 도시",
            options=[item["name"] for item in PRESET_LOCATIONS],
            default=default_city_names,
        )
        st.caption("선택한 여러 도시를 한 번에 저장해서 지도에 채울 때 사용합니다.")
        bulk_fetch_button = st.button(
            "선택한 도시들 한 번에 불러오기",
            use_container_width=True,
            on_click=set_all_locations_mode,
        )

        with st.expander("조회 옵션", expanded=False):
            fcst_date = st.text_input("예보일자", value=today)
            fcst_time = st.text_input("예보시각", value="", placeholder="비우면 전체")
            show_all_locations = st.checkbox("전체 지역 보기", key="show_all_locations")
            load_button = st.button("DB 조회", use_container_width=True)

        with st.expander("고급 설정", expanded=False):
            location = get_location_by_name(selected_city)
            st.caption("보통은 건드리지 않아도 됩니다.")
            st.text_input("발표일자", value=default_base["base_date"], key="advanced_base_date")
            st.selectbox("발표시각", default_base["valid_times"], index=default_base["index"], key="advanced_base_time")
            st.number_input("격자 X(nx)", min_value=1, max_value=149, value=int(location["nx"]), step=1, key="advanced_nx")
            st.number_input("격자 Y(ny)", min_value=1, max_value=253, value=int(location["ny"]), step=1, key="advanced_ny")

    if "fcst_date" not in locals():
        fcst_date = today
        fcst_time = ""
        show_all_locations = True
        load_button = False

    if fetch_button:
        location = get_location_by_name(selected_city)
        base_date = st.session_state["advanced_base_date"]
        base_time = st.session_state["advanced_base_time"]
        nx = int(location["nx"])
        ny = int(location["ny"])

        try:
            result = post_fetch(base_date, base_time, nx, ny, selected_city)
            if result.get("resultCode") == "00":
                st.success(f"{selected_city} 데이터를 저장했습니다. 저장 건수: {result.get('saved_count', 0)}")
            else:
                st.error(f"API 오류 - resultCode: {result.get('resultCode')}, resultMsg: {result.get('resultMsg')}")
        except requests.RequestException as error:
            st.error(f"백엔드 요청 오류: {error}")

    if bulk_fetch_button:
        selected_locations = [item for item in PRESET_LOCATIONS if item["name"] in selected_city_names]
        if not selected_locations:
            st.warning("최소 한 개 지역을 선택해주세요.")
        else:
            try:
                result_df = fetch_multiple_locations(
                    st.session_state["advanced_base_date"],
                    st.session_state["advanced_base_time"],
                    selected_locations,
                )
                success_count = int((result_df["resultCode"] == "00").sum()) if not result_df.empty else 0
                st.success(f"{success_count}개 지역 데이터를 저장했습니다.")
                failed = result_df[result_df["resultCode"] != "00"]
                if not failed.empty:
                    st.warning("일부 지역은 실패했습니다.")
                    st.dataframe(failed, use_container_width=True)
            except requests.RequestException as error:
                st.error(f"여러 지역 저장 중 오류: {error}")

    items = []
    if load_button or fetch_button or bulk_fetch_button:
        try:
            location = get_location_by_name(selected_city)
            items = get_forecasts(
                fcst_date=fcst_date,
                fcst_time=fcst_time,
                category="",
                nx=None if show_all_locations else int(location["nx"]),
                ny=None if show_all_locations else int(location["ny"]),
            )
        except requests.RequestException as error:
            st.error(f"조회 오류: {error}")

    df = to_dataframe(items)
    summary = format_summary(df)
    map_df = build_map_snapshot(df)

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("예보 건수", len(df))
    metric2.metric("기온", f"{summary['TMP']}℃" if summary["TMP"] != "-" else "-")
    metric3.metric("강수확률", f"{summary['POP']}%" if summary["POP"] != "-" else "-")
    metric4.metric("하늘상태", SKY_MAP.get(str(summary["SKY"]), summary["SKY"]))

    st.markdown(
        """
        <div class="opgg-panel">
            <h3>전국 지도</h3>
            <p>원 크기는 강수확률, 색상은 하늘상태를 나타냅니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    draw_weather_map(map_df)

    st.markdown(
        """
        <div class="opgg-panel">
            <h3>날씨 설명</h3>
            <p>TMP는 기온, POP는 강수확률, SKY는 하늘상태, PTY는 강수형태, REH는 습도, WSD는 풍속입니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if summary["PTY"] != "-":
        st.info(f"현재와 가장 가까운 시각 기준 강수형태: {PTY_MAP.get(str(summary['PTY']), summary['PTY'])}")

    st.markdown(
        """
        <div class="opgg-panel">
            <h3>예보 차트</h3>
            <p>지역별 시간 흐름을 비교해서 온도와 강수확률 변화를 확인할 수 있습니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    location_options = ["전체"] + sorted(df["location_name"].dropna().unique().tolist()) if not df.empty else ["전체"]
    chart_col1, chart_col2 = st.columns(2)
    selected_chart_location = chart_col1.selectbox("차트 지역", options=location_options)
    chart_category = chart_col2.selectbox("차트 항목", ["TMP", "POP", "REH", "WSD"])
    chart_df = prepare_chart(df, chart_category, selected_chart_location)
    if not chart_df.empty:
        if selected_chart_location == "전체":
            pivot_df = chart_df.pivot_table(
                index="forecast_at",
                columns="location_name",
                values="fcst_value_num",
                aggfunc="first",
            ).sort_index()
            st.line_chart(pivot_df)
        else:
            st.line_chart(chart_df.set_index("forecast_at")["fcst_value_num"])
    else:
        st.warning("차트로 표시할 숫자형 데이터가 없습니다.")

    if not df.empty:
        st.download_button(
            "CSV 다운로드",
            data=csv_bytes(df),
            file_name="weather_forecast_filtered.csv",
            mime="text/csv",
        )
    else:
        st.warning("조회 결과가 없습니다. 왼쪽에서 데이터를 먼저 불러와주세요.")


if __name__ == "__main__":
    main()
