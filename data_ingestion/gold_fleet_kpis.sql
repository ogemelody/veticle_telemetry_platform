%sql
CREATE OR REPLACE TABLE lakehouse_eat_catalog.gold.fleet_kpis AS

SELECT
    t.vehicle_id,
    v.manufacturer,
    v.type,
    v.fuel_type,
    v.fleet_region,
    v.model_year,

    -- CAN bus signals
    t.avg_engine_temp_c,
    t.avg_engine_rpm,
    t.avg_fuel_level_pct,
    t.avg_tire_pressure_psi,
    t.avg_battery_health,
    t.avg_speed_kmh,
    t.warning_detected,
    t.telemetry_reading_count,

    -- Trip behaviour
    tr.avg_distance_km,
    tr.avg_fuel_used,
    tr.avg_brake_events,
    tr.trip_count,

    -- Health score (your existing logic)
    ROUND(
        (t.avg_battery_health * 0.4) +
        (CASE WHEN t.avg_engine_temp_c < 100 THEN 100 ELSE 60 END * 0.3) +
        (CASE WHEN t.warning_detected = 0 THEN 100 ELSE 50 END * 0.3),
    2) AS health_score,

    -- Risk classification
    CASE
        WHEN t.warning_detected = 1 OR t.avg_engine_temp_c > 110 THEN 'CRITICAL'
        WHEN t.avg_battery_health < 50 OR t.avg_tire_pressure_psi < 30 THEN 'WARNING'
        ELSE 'GOOD'
    END AS risk_level

FROM lakehouse_eat_catalog.silver.telemetry_agg t
LEFT JOIN lakehouse_eat_catalog.silver.trips_agg    tr ON t.vehicle_id = tr.vehicle_id
LEFT JOIN lakehouse_eat_catalog.silver.vehicle_profile v ON t.vehicle_id = v.vehicle_id