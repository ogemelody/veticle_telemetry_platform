%sql
CREATE OR REPLACE TABLE lakehouse_eat_catalog.gold.fleet_sentiment AS
SELECT
    vehicle_id,
    health_score,
    engine_temp_avg,
    avg_speed,

    AI_QUERY(
      'databricks-meta-llama-3-3-70b-instruct',
      CONCAT(
        'Analyze this fleet vehicle health. ',
        'Health Score: ', health_score,
        ', Engine Temp: ', engine_temp_avg,
        ', Avg Speed: ', avg_speed,
        '. Return sentiment (Good/Warning/Critical) ',
        'and short operational recommendation.'
      )
    ) AS ai_fleet_sentiment

FROM  lakehouse_eat_catalog.gold.fleet_kpis;