import sqlite3
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


app = FastAPI(title="AgriVolt API")
DATABASE_PATH = Path(__file__).resolve().parent.parent / "agrivolt.db"
DASHBOARD_PAGE = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

default_origins = "http://localhost:5173,http://127.0.0.1:5173"
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", default_origins).split(",") if origin.strip()]

# Production hosts are configured through CORS_ORIGINS; local preview keeps working by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class DashboardData(BaseModel):
    reading_id: int | None = None
    pump_status: str
    estimated_power_kw: float
    voltage_v: float
    current_a: float
    water_tank_percent: int
    soil_moisture_percent: int
    todays_energy_kwh: float
    estimated_cost_inr: float
    pump_health: str
    alert: str


class SensorReading(BaseModel):
    pump_status: str = Field(examples=["ON"])
    estimated_power_kw: float = Field(ge=0, examples=[2.4])
    voltage_v: float = Field(ge=0, examples=[228.0])
    current_a: float = Field(ge=0, examples=[10.5])
    water_tank_percent: int = Field(ge=0, le=100, examples=[72])
    soil_moisture_percent: int = Field(ge=0, le=100, examples=[41])
    todays_energy_kwh: float = Field(ge=0, examples=[12.8])
    pump_health: str = Field(examples=["Normal"])


class SavedReading(SensorReading):
    id: int
    recorded_at: str


class PumpControlRequest(BaseModel):
    action: Literal["ON", "OFF"]


class PumpControlResponse(BaseModel):
    pump_status: Literal["ON", "OFF"]
    message: str
    commanded_at: str


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                pump_status TEXT NOT NULL,
                estimated_power_kw REAL NOT NULL,
                voltage_v REAL NOT NULL,
                current_a REAL NOT NULL,
                water_tank_percent INTEGER NOT NULL,
                soil_moisture_percent INTEGER NOT NULL,
                todays_energy_kwh REAL NOT NULL,
                pump_health TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pump_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pump_status TEXT NOT NULL,
                commanded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.on_event("startup")
def start_database() -> None:
    initialize_database()


def get_manual_pump_status() -> str:
    """The pump state is controlled only by the latest manual command."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT pump_status FROM pump_commands ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row["pump_status"] if row else "OFF"


def build_dashboard(reading: SensorReading, pump_status: str | None = None) -> DashboardData:
    if reading.soil_moisture_percent < 45:
        alert = "Soil moisture is low. Irrigation recommended."
    elif reading.pump_health.lower() != "normal":
        alert = "Pump needs attention. Please inspect it."
    elif reading.estimated_power_kw > 3.0:
        alert = "Pump is consuming more energy than usual."
    else:
        alert = "Irrigation completed successfully."

    values = reading.model_dump()
    values["pump_status"] = pump_status or get_manual_pump_status()
    return DashboardData(
        reading_id=getattr(reading, "id", None),
        **values,
        estimated_cost_inr=round(reading.todays_energy_kwh * 7.5, 2),
        alert=alert,
    )


def row_to_saved_reading(row: sqlite3.Row) -> SavedReading:
    return SavedReading(**dict(row))


def get_latest_reading() -> SavedReading | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row_to_saved_reading(row) if row else None


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "AgriVolt backend is running"}


@app.get("/app", include_in_schema=False)
async def farmer_dashboard() -> FileResponse:
    """Serve the farmer-facing dashboard."""
    return FileResponse(DASHBOARD_PAGE)


@app.get("/dashboard", response_model=DashboardData)
async def get_dashboard() -> DashboardData:
    """Return the current smart-farm dashboard readings."""
    latest_reading = get_latest_reading()
    if latest_reading is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings yet. Send a reading to POST /readings first.",
        )
    return build_dashboard(latest_reading, get_manual_pump_status())


@app.post("/readings", response_model=DashboardData)
async def add_reading(reading: SensorReading) -> DashboardData:
    """Save the latest sensor reading and return the updated dashboard."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO readings (
                pump_status, estimated_power_kw, voltage_v, current_a,
                water_tank_percent, soil_moisture_percent, todays_energy_kwh,
                pump_health
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(reading.model_dump().values()),
        )
        saved_id = cursor.lastrowid
        row = connection.execute(
            "SELECT * FROM readings WHERE id = ?", (saved_id,)
        ).fetchone()

    return build_dashboard(row_to_saved_reading(row), get_manual_pump_status())


@app.get("/readings", response_model=list[SavedReading])
async def list_readings(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[SavedReading]:
    """Return recent sensor readings, newest first."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [row_to_saved_reading(row) for row in rows]


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Check whether the AgriVolt API is available."""
    return {"status": "ok", "service": "AgriVolt API"}


@app.post("/pump/control", response_model=PumpControlResponse)
async def control_pump(command: PumpControlRequest) -> PumpControlResponse:
    """Record a requested ON/OFF pump command for the demo."""
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO pump_commands (pump_status) VALUES (?)", (command.action,)
        )
        row = connection.execute(
            "SELECT * FROM pump_commands WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return PumpControlResponse(
        pump_status=row["pump_status"],
        message=f"Pump command recorded: {row['pump_status']}",
        commanded_at=row["commanded_at"],
    )


@app.get("/pump/status", response_model=PumpControlResponse)
async def get_pump_status() -> PumpControlResponse:
    """Return the latest requested pump state for the demo."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM pump_commands ORDER BY id DESC LIMIT 1"
        ).fetchone()

    if row is None:
        return PumpControlResponse(
            pump_status="OFF",
            message="No pump command recorded yet.",
            commanded_at="Not commanded",
        )
    return PumpControlResponse(
        pump_status=row["pump_status"],
        message=f"Latest pump command: {row['pump_status']}",
        commanded_at=row["commanded_at"],
    )
