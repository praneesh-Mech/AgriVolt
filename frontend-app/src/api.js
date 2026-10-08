// AgriVolt API client. Configure VITE_API_URL in .env (never put secret keys there).
const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const dashboardPath = import.meta.env.VITE_API_DASHBOARD_PATH || '/dashboard'
const pumpPath = import.meta.env.VITE_API_PUMP_PATH || '/pump/control'

const pick = (source, ...keys) => keys.map(key => source?.[key]).find(value => value !== undefined && value !== null)
const toNumber = (value, fallback) => value === undefined ? fallback : Number(value)

export const hasBackend = Boolean(baseUrl)

async function request(path, options = {}) {
  if (!baseUrl) return null
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
    ...options,
  })
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  if (response.status === 204) return null
  return response.json()
}

// Accepts either the camelCase names used by the UI or common snake_case backend names.
export function normalizeDashboard(payload = {}) {
  const source = payload.data || payload.dashboard || payload
  const pumpStatus = String(pick(source, 'pumpOn', 'pump_on', 'pumpStatus', 'pump_status') || 'OFF')
  return {
    readingId: pick(source, 'readingId', 'reading_id', 'id') ?? null,
    pumpOn: pumpStatus.toUpperCase() === 'ON' || pumpStatus === 'true',
    power: toNumber(pick(source, 'power', 'estimatedPower', 'estimated_power', 'estimated_power_kw', 'power_kw'), 0),
    voltage: toNumber(pick(source, 'voltage', 'voltage_v'), 0),
    current: toNumber(pick(source, 'current', 'current_a'), 0),
    tank: toNumber(pick(source, 'tank', 'tankLevel', 'tank_level', 'water_tank', 'water_tank_percent'), 0),
    moisture: toNumber(pick(source, 'moisture', 'soilMoisture', 'soil_moisture', 'soil_moisture_percent'), 0),
    energy: toNumber(pick(source, 'energy', 'todayEnergy', 'today_energy', 'todays_energy_kwh', 'energy_kwh'), 0),
    cost: toNumber(pick(source, 'cost', 'estimatedCost', 'estimated_cost', 'estimated_cost_inr'), 0),
    health: pick(source, 'health', 'pumpHealth', 'pump_health') || 'Unknown',
    alert: pick(source, 'alert') || 'No farm alert available.',
  }
}

export async function getDashboard() {
  const payload = await request(dashboardPath)
  return payload ? normalizeDashboard(payload) : null
}

export async function setPumpState(pumpOn) {
  return request(pumpPath, { method: 'POST', body: JSON.stringify({ action: pumpOn ? 'ON' : 'OFF' }) })
}
