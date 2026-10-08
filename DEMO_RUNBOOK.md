# AgriVolt hackathon demo runbook

## Start the backend

In PowerShell:

```powershell
Set-Location 'C:\Users\prane\OneDrive\Desktop\AgriVolt'
& '.\.venv\Scripts\python.exe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Keep this window open. API docs are at `http://127.0.0.1:8000/docs`.

## Demo story (about 2 minutes)

1. Introduce AgriVolt as a farm dashboard connecting pump energy, water availability, and soil moisture.
2. Show the normal dashboard and explain that the backend serves readings through FastAPI and stores them in SQLite.
3. Send a low-moisture reading. Show the irrigation recommendation.
4. Send a high-energy reading. Show the energy warning.
5. Send a normal/completed reading. Show the success state.
6. Demonstrate the pump ON/OFF request and explain that it is simulated until connected to a controller or pump hardware.

## Sample readings for Swagger

Use these bodies with `POST /readings`:

Low moisture:

```json
{
  "pump_status": "ON",
  "estimated_power_kw": 2.4,
  "voltage_v": 228,
  "current_a": 10.5,
  "water_tank_percent": 72,
  "soil_moisture_percent": 35,
  "todays_energy_kwh": 12.8,
  "pump_health": "Normal"
}
```

High energy:

```json
{
  "pump_status": "ON",
  "estimated_power_kw": 3.7,
  "voltage_v": 228,
  "current_a": 16.2,
  "water_tank_percent": 65,
  "soil_moisture_percent": 60,
  "todays_energy_kwh": 18.4,
  "pump_health": "Normal"
}
```

Irrigation complete:

```json
{
  "pump_status": "OFF",
  "estimated_power_kw": 0,
  "voltage_v": 228,
  "current_a": 0,
  "water_tank_percent": 58,
  "soil_moisture_percent": 68,
  "todays_energy_kwh": 14.1,
  "pump_health": "Normal"
}
```

## Integration notes

- Frontend API base URL: `http://127.0.0.1:8000`
- Allowed frontend development origins: `http://localhost:5173` and `http://127.0.0.1:5173`
- Dashboard: `GET /dashboard`
- New reading: `POST /readings`
- Reading history: `GET /readings?limit=20`
- Simulated pump control: `POST /pump/control` with `{ "action": "ON" }` or `{ "action": "OFF" }`
- Simulated pump state: `GET /pump/status`
- Health: `GET /health`

Cost and sensor values are demonstration data unless connected to calibrated sensors and a real electricity tariff. Pump commands are stored as requests and do not switch hardware.
