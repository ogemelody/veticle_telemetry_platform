SELECT
  CASE
    WHEN health_score >= 90 THEN '90-100 Excellent'
    WHEN health_score >= 75 THEN '75-89 Good'
    WHEN health_score >= 60 THEN '60-74 Fair'
    ELSE 'Below 60 Poor'
  END AS health_band,
  COUNT(*) AS vehicle_count
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring
GROUP BY health_band
ORDER BY health_band DESC