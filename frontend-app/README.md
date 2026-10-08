# AgriVolt Frontend

Responsive React/Vite dashboard for pump, irrigation, energy, water-tank, soil-moisture, and farm-health monitoring.

## Run locally

```powershell
cd "C:\Users\Pranav R\OneDrive\Desktop\agrivolt frontend"
cmd /c npm install
cmd /c npm run dev
```

Open the local URL printed by Vite.

## Connect the backend

1. Copy `.env.example` to a new file named `.env`.
2. Set your backend base URL, for example:

```env
VITE_API_URL=http://localhost:8080/api
VITE_API_DASHBOARD_PATH=/dashboard
VITE_API_PUMP_PATH=/pump
```

3. Restart the frontend after changing `.env`.

The frontend requests:

| Purpose | Default endpoint | Method |
| --- | --- | --- |
| Live dashboard readings | `/dashboard` | `GET` |
| Start or stop pump | `/pump` | `PATCH` |

Pump updates send a JSON body with `pumpOn`, `pump_on`, and `status` for easy backend compatibility. Dashboard data supports the UI’s camelCase names and common snake_case alternatives (`soil_moisture`, `tank_level`, `estimated_power`, etc.).

## Backend requirements

- Allow CORS from the development frontend URL, for example `http://localhost:5173` or the port Vite prints.
- Return JSON from both endpoints.
- Do not put database passwords, private API keys, or JWT secrets in the frontend `.env`; Vite exposes variables beginning with `VITE_` to the browser.

## Share with the backend developer

Send this whole folder as a ZIP, or preferably push it to a GitHub repository and invite your friend. Include this README and `.env.example`, but **do not share your actual `.env`** file.

Ask your friend to send:

- API base URL
- Exact endpoint paths and methods
- Example JSON response for dashboard readings
- Required authorization method, if any
- CORS configuration status
