from pyspark.sql import functions as F

# ----------------------------
# Load vehicles
# ----------------------------
df_vehicles = spark.read.table("lakehouse_eat_catalog.bronze.vehicles")

vehicles_list = [
    r["vehicle_id"]
    for r in df_vehicles.select("vehicle_id").distinct().collect()
]

vehicle_count = len(vehicles_list)

vehicle_array = F.array(*[F.lit(v) for v in vehicles_list])


# ----------------------------
# Streaming source
# ----------------------------
base_stream = (
    spark.readStream
    .format("rate")
    .option("rowsPerSecond", 50)
    .load()
)


# ----------------------------
# Deterministic vehicle mapping (FIXED)
# ----------------------------
df_stream = (
    base_stream
    .withColumn(
        "vehicle_id",
        F.element_at(
            vehicle_array,
            (F.pmod(F.col("value"), F.lit(vehicle_count)) + F.lit(1)).cast("int")
        )
    )
)


# ----------------------------
# Telemetry simulation
# ----------------------------
df_stream = (
    df_stream
    .withColumn("timestamp", F.current_timestamp())
    .withColumn("speed", F.round(F.rand() * 140, 2))
    .withColumn("rpm", F.floor(F.rand() * 5200 + 800))
    .withColumn("engine_temp", F.round(F.rand() * 60 + 60, 2))
    .withColumn("fuel_level", F.round(F.rand() * 90 + 10, 2))
    .withColumn("tire_pressure", F.round(F.rand() * 8 + 28, 2))
    .withColumn("battery_health", F.round(F.rand() * 50 + 50, 2))
    .withColumn("warning_flag", F.when(F.rand() < 0.25, 1).otherwise(0))
)


# ----------------------------
# Write stream (CATALOG + VOLUME SAFE)
# ----------------------------
query = (
    df_stream.writeStream
    .format("delta")
    .option(
        "checkpointLocation",
        "/Volumes/lakehouse_eat_catalog/bronze/checkpoints/vehicle_telemetry"
    )
    .outputMode("append")
    .trigger(availableNow=True)
    .toTable("lakehouse_eat_catalog.bronze.vehicle_telemetry")
)
