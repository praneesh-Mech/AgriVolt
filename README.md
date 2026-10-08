# AgriVolt Backend

FastAPI backend for smart farm energy and irrigation monitoring.

## Run locally

```powershell
Set-Location 'C:\Users\prane\OneDrive\Desktop\AgriVolt'
& '.\.venv\Scripts\python.exe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

- API documentation: `http://127.0.0.1:8000/docs`
- Temporary demo dashboard: `http://127.0.0.1:8000/app`

## API contract for the frontend

### Get the current dashboard

`GET /dashboard`

Returns the latest farm reading, calculated electricity cost, and one alert message.

### Send a sensor reading

`POST /readings`

```json
{
  "pump_status": "ON",
  "estimated_power_kw": 2.4,
  "voltage_v": 228,
  "current_a": 10.5,
  "water_tank_percent": 72,
  "soil_moisture_percent": 41,
  "todays_energy_kwh": 12.8,
  "pump_health": "Normal"
}
```

### Get reading history

`GET /readings?limit=20`

### Request a pump command (demo only)

`POST /pump/control`

```json
{
  "action": "ON"
}
```

Use `"OFF"` to request that the pump stops.

### Get the latest requested pump state

`GET /pump/status`

### Check that the backend is available

`GET /health`

## Integration plan

Your teammate's frontend should call this backend at `http://127.0.0.1:8000` while you are both running locally. CORS is configured for the Vite preview origins `http://localhost:5173` and `http://127.0.0.1:5173`.

In the frontend, use `http://127.0.0.1:8000` as the API base URL. Example:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
const response = await fetch(`${API_BASE_URL}/dashboard`);
const dashboard = await response.json();
```

If the frontend runs on a different port, add its exact origin to the `allow_origins` list in `backend/main.py` and restart the backend.

The `frontend/index.html` file in this repository is only a local demo/test page. It does not need to be used by the final frontend.

## Hackathon demo sequence

1. Start the backend and the teammate's frontend preview.
2. Open the teammate's frontend and confirm its dashboard loads from `GET /dashboard`.
3. Send one reading to `POST /readings`; confirm the frontend updates its values and alert.
4. Try `POST /pump/control` or the frontend's pump controls; describe this as a simulated command unless physical pump hardware is connected.
5. If the frontend integration is unavailable, use the included local demo at `http://127.0.0.1:8000/app`.

The current backend uses local SQLite. Cost uses a demo rate of ₹7.50 per kWh, and the pump controls record requested commands without controlling real hardware.
