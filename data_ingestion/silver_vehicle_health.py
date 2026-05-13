from pyspark.sql.functions import avg, min, max, count, col

# Bronze tables
df_telemetry = spark.table(
    "lakehouse_eat_catalog.bronze.vehicle_telemetry"
)

df_trips = spark.table(
    "lakehouse_eat_catalog.bronze.vehicle_trips"
)

# -----------------------------------
# Telemetry aggregations
# -----------------------------------
silver_telemetry = (
    df_telemetry.groupBy("vehicle_id")
    .agg(
        avg("battery_health").alias("avg_battery_health"),
        avg("engine_temp").alias("avg_engine_temp"),
        avg("speed").alias("avg_speed"),
        max("warning_flag").alias("warning_detected")
    )
)

# -----------------------------------
# Trip aggregations
# -----------------------------------
silver_trips = (
    df_trips.groupBy("vehicle_id")
    .agg(
        avg("distance_km").alias("avg_distance_km"),
        avg("fuel_used").alias("avg_fuel_used"),
        avg("brake_events").alias("avg_brake_events"),
        count("trip_id").alias("trip_count")
    )
)

# -----------------------------------
# Final Silver table
# -----------------------------------
silver_final = (
    silver_telemetry.join(
        silver_trips,
        on="vehicle_id",
        how="left"
    )
)

silver_final.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.silver.vehicle_health_features"
)