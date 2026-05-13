%sql
CREATE OR REPLACE TABLE lakehouse_eat_catalog.gold.ai_fleet_monitoring AS

SELECT
    vehicle_id,
    health_score,
    avg_engine_temp,
    avg_speed,
    avg_battery_health,
    risk_level,

    AI_QUERY(
      'databricks-meta-llama-3-3-70b-instruct',

      CONCAT(
        'You are an automotive fleet monitoring assistant. ',
        'Analyze the following vehicle telemetry KPIs and provide: ',
        '1. Fleet health assessment ',
        '2. Operational risk level ',
        '3. Predictive maintenance recommendation ',
        '4. Short explanation. ',

        'Vehicle ID: ', vehicle_id,
        ', Health Score: ', ROUND(health_score,2),
        ', Avg Engine Temp: ', ROUND(avg_engine_temp,2),
        ', Avg Speed: ', ROUND(avg_speed,2),
        ', Battery Health: ', ROUND(avg_battery_health,2),
        ', Risk Level: ', risk_level
      )

    ) AS ai_operational_insight

FROM lakehouse_eat_catalog.gold.fleet_kpis;