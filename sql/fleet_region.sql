SELECT
  fleet_region,
  COUNT(*) AS vehicle_count,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
WHERE fleet_region IS NOT NULL
GROUP BY fleet_region
ORDER BY vehicle_count DESC