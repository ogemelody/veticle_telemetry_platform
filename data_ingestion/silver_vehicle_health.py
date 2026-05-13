from pyspark.sql.functions import avg, max, count

df_telemetry = spark.table("lakehouse_eat_catalog.bronze.vehicle_telemetry")
df_trips     = spark.table("lakehouse_eat_catalog.bronze.vehicle_trips")
df_vehicle   = spark.table("lakehouse_eat_catalog.bronze.vehicles")

# Silver table 1 — telemetry signals (CAN bus aggregated)
silver_telemetry = (
    df_telemetry.groupBy("vehicle_id")
    .agg(
        avg("battery_health").alias("avg_battery_health"),
        avg("engine_temp").alias("avg_engine_temp_c"),  # CAN: coolant proxy
        avg("speed").alias("avg_speed_kmh"), #Vehicle speed sensor
        avg("rpm").alias("avg_engine_rpm"), #CAN: engine RPM
        avg("fuel_level").alias("avg_fuel_level_pct"), #Fuel level sensor
        avg("tire_pressure").alias("avg_tire_pressure_psi"), #TPMS
        max("warning_flag").alias("warning_detected"),
        count("vehicle_id").alias("telemetry_reading_count")
    )
)
silver_telemetry.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.silver.telemetry_agg"
)

# Silver table 2 — trip behaviour
silver_trips = (
    df_trips.groupBy("vehicle_id")
    .agg(
        avg("distance_km").alias("avg_distance_km"),
        avg("fuel_used").alias("avg_fuel_used"),
        avg("brake_events").alias("avg_brake_events"),
        count("trip_id").alias("trip_count")
    )
)
silver_trips.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.silver.trips_agg"
)

# Silver table 3 — vehicle reference (no aggregation needed, it's already one row per vehicle)
df_vehicle.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.silver.vehicle_profile"
)

print(" 3 Silver tables written cleanly")