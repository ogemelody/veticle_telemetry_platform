%sql
CREATE OR REPLACE TABLE lakehouse_eat_catalog.gold.ai_fleet_monitoring AS

SELECT
    vehicle_id,
    manufacturer,
    type,
    fuel_type,
    fleet_region,
    health_score,
    risk_level,
    avg_engine_temp_c,
    avg_engine_rpm,
    avg_fuel_level_pct,
    avg_tire_pressure_psi,
    avg_battery_health,
    avg_speed_kmh,
    avg_brake_events,
    trip_count,
    warning_detected,

    AI_QUERY(
      'databricks-meta-llama-3-3-70b-instruct',
      CONCAT(
        'You are an automotive fleet monitoring assistant specialising in vehicle telematics and CAN bus signals. ',
        'Analyse the following vehicle telemetry and provide a response in this exact format: ',
        'HEALTH: one sentence of Fleet health assessment. ',
        'RISK: one sentence. ',
        'MAINTENANCE: Predictive maintenance recommendation. ',
        'REASON: one sentence referencing the specific signals. ',

        'Vehicle ID: ', vehicle_id,
        ', Manufacturer: ', COALESCE(manufacturer, 'Unknown'),
        ', Type: ', COALESCE(type, 'Unknown'),
        ', Fuel Type: ', COALESCE(fuel_type, 'Unknown'),
        ', Region: ', COALESCE(fleet_region, 'Unknown'),
        ', Health Score: ', ROUND(health_score, 2),
        ', Risk Level: ', risk_level,
        ', Engine Temp (C): ', ROUND(avg_engine_temp_c, 2),
        ', Engine RPM: ', ROUND(avg_engine_rpm, 0),
        ', Battery Health (%): ', ROUND(avg_battery_health, 2),
        ', Speed (km/h): ', ROUND(avg_speed_kmh, 2),
        ', Fuel Level (%): ', ROUND(avg_fuel_level_pct, 2),
        ', Tyre Pressure (PSI): ', ROUND(avg_tire_pressure_psi, 2),
        ', Brake Events: ', ROUND(avg_brake_events, 0),
        ', Warning Detected: ', warning_detected,
        ', Trip Count: ', trip_count
      )
    ) AS ai_operational_insight

FROM lakehouse_eat_catalog.gold.fleet_kpis;