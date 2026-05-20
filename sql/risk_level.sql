SELECT
  risk_level,
  ROUND(AVG(avg_engine_temp_c), 1) AS avg_temp_c,
  ROUND(AVG(avg_engine_rpm), 0) AS avg_rpm,
  ROUND(AVG(avg_battery_health), 1) AS avg_battery,
  ROUND(AVG(avg_tire_pressure_psi), 1) AS avg_tire_psi,
  ROUND(AVG(avg_speed_kmh), 1) AS avg_speed,
  COUNT(*) AS vehicle_count
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
GROUP BY risk_level
ORDER BY
  CASE WHEN risk_level = 'CRITICAL' THEN 1
       WHEN risk_level = 'WARNING' THEN 2
       ELSE 3 END