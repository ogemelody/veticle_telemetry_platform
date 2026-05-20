SELECT
  vehicle_id,
  ROUND(avg_engine_temp_c, 1) AS engine_temp,
  ROUND(avg_battery_health, 1) AS battery_health,
  health_score,
  risk_level,
  manufacturer
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
ORDER BY health_score ASC