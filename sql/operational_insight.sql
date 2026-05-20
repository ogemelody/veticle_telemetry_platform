SELECT
  vehicle_id,
  manufacturer,
  type,
  fleet_region,
  ROUND(health_score, 1) AS health_score,
  risk_level,
  ROUND(avg_engine_temp_c, 1) AS engine_temp_c,
  ROUND(avg_battery_health, 1) AS battery_health,
  ROUND(avg_engine_rpm, 0) AS engine_rpm,
  ROUND(avg_tire_pressure_psi, 1) AS tire_pressure_psi,
  warning_detected,
  SUBSTRING(ai_operational_insight, 1, 100) AS maintenance_hint
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
WHERE risk_level IN ('CRITICAL', 'WARNING')
ORDER BY health_score ASC