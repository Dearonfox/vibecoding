from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_connection, initialize_database
from backend.schemas import FetchRequest, ForecastCreate, ForecastUpdate
from backend.weather_api import build_items_dataframe, fetch_short_term_forecast, save_forecast_dataframe


app = FastAPI(title="Weather Forecast API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def row_to_dict(row):
    return dict(row) if row else None


def build_forecast_datetime(fcst_date, fcst_time):
    return f"{fcst_date}{fcst_time}"


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def read_root():
    return {"message": "Weather Forecast FastAPI backend is running."}


@app.post("/forecasts/fetch")
def fetch_and_store_forecasts(request: FetchRequest):
    payload = fetch_short_term_forecast(
        base_date=request.base_date,
        base_time=request.base_time,
        nx=request.nx,
        ny=request.ny,
    )
    api_result = payload["api_result"]

    if api_result.get("resultCode") != "00":
        return {
            "saved_count": 0,
            "resultCode": api_result.get("resultCode"),
            "resultMsg": api_result.get("resultMsg"),
            "items": [],
        }

    df = build_items_dataframe(
        payload["items"],
        location_name=request.location_name,
        nx=request.nx,
        ny=request.ny,
    )
    saved_count = save_forecast_dataframe(df)

    return {
        "saved_count": saved_count,
        "resultCode": api_result.get("resultCode"),
        "resultMsg": api_result.get("resultMsg"),
        "items": df.to_dict(orient="records"),
    }


@app.get("/forecasts")
def list_forecasts(
    fcst_date: Optional[str] = None,
    fcst_time: Optional[str] = None,
    category: Optional[str] = None,
    nx: Optional[int] = None,
    ny: Optional[int] = None,
):
    query = "SELECT * FROM weather_forecast WHERE 1=1"
    params = []

    if fcst_date:
        query += " AND fcst_date = ?"
        params.append(fcst_date)
    if fcst_time:
        query += " AND fcst_time = ?"
        params.append(fcst_time)
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
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


@app.get("/forecasts/{forecast_id}")
def get_forecast(forecast_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM weather_forecast WHERE id = ?", (forecast_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return dict(row)


@app.post("/forecasts")
def create_forecast(data: ForecastCreate):
    forecast_datetime = build_forecast_datetime(data.fcst_date, data.fcst_time)
    query = """
    INSERT INTO weather_forecast (
        base_date, base_time, fcst_date, fcst_time, forecast_datetime,
        category, fcst_value, nx, ny, location_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    data.base_date,
                    data.base_time,
                    data.fcst_date,
                    data.fcst_time,
                    forecast_datetime,
                    data.category,
                    data.fcst_value,
                    data.nx,
                    data.ny,
                    data.location_name,
                ),
            )
            conn.commit()
            created_id = cursor.lastrowid
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"등록 실패: {error}")

    return get_forecast(created_id)


@app.put("/forecasts/{forecast_id}")
def update_forecast(forecast_id: int, data: ForecastUpdate):
    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM weather_forecast WHERE id = ?", (forecast_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

        fcst_value = data.fcst_value if data.fcst_value is not None else existing["fcst_value"]
        location_name = data.location_name if data.location_name is not None else existing["location_name"]

        conn.execute(
            """
            UPDATE weather_forecast
            SET fcst_value = ?, location_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (fcst_value, location_name, forecast_id),
        )
        conn.commit()

    return get_forecast(forecast_id)


@app.delete("/forecasts/{forecast_id}")
def delete_forecast(forecast_id: int):
    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM weather_forecast WHERE id = ?", (forecast_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

        conn.execute("DELETE FROM weather_forecast WHERE id = ?", (forecast_id,))
        conn.commit()
    return {"message": "삭제되었습니다.", "id": forecast_id}


@app.get("/forecasts-summary")
def get_forecast_summary(
    nx: int = Query(...),
    ny: int = Query(...),
    fcst_date: Optional[str] = None,
):
    query = "SELECT * FROM weather_forecast WHERE nx = ? AND ny = ?"
    params = [nx, ny]

    if fcst_date:
        query += " AND fcst_date = ?"
        params.append(fcst_date)

    query += " ORDER BY fcst_date, fcst_time, category"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if df.empty:
        return {"count": 0, "categories": {}, "items": []}

    category_counts = df["category"].value_counts().to_dict()
    return {
        "count": int(len(df)),
        "categories": category_counts,
        "items": df.to_dict(orient="records"),
    }
