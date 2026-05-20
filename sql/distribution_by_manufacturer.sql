SELECT
  manufacturer,
  risk_level,
  COUNT(*) AS vehicle_count
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
WHERE manufacturer IS NOT NULL
GROUP BY manufacturer, risk_level
ORDER BY manufacturer,
  CASE WHEN risk_level = 'CRITICAL' THEN 1
       WHEN risk_level = 'WARNING' THEN 2
       ELSE 3 END