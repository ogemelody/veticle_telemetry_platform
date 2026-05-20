SELECT
  COUNT(*) AS total_vehicles,
  SUM(CASE WHEN risk_level = 'GOOD' THEN 1 ELSE 0 END) AS good,
  SUM(CASE WHEN risk_level = 'WARNING' THEN 1 ELSE 0 END) AS warning,
  SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) AS critical,
  ROUND(AVG(health_score), 1) AS avg_health_score
FROM lakehouse_eat_catalog.gold.ai_fleet_monitoring