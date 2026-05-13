# Historical Telemetry
import pandas as pd
import random
from datetime import datetime, timedelta
import os

from pyspark.sql import functions as F

df_vehicles = spark.read.table("lakehouse_eat_catalog.bronze.vehicles")

vehicles_df = df_vehicles.select("vehicle_id").distinct()

df_trips = (
    vehicles_df
    .withColumn("vehicle_id", F.col("vehicle_id"))
    .withColumn("trip_id", F.concat(F.lit("TRIP-"), F.floor(F.rand() * 1000000)))

    # safer timestamp logic
    .withColumn(
        "start_time",
        F.expr("timestampadd(DAY, -cast(rand()*200 as int), current_timestamp())")
    )

    .withColumn(
        "end_time",
        F.expr("timestampadd(HOUR, cast(rand()*6 as int), start_time)")
    )

    .withColumn("distance_km", F.round(F.rand() * 495 + 5, 2))
    .withColumn("avg_speed", F.round(F.rand() * 80 + 40, 2))
    .withColumn("fuel_used", F.round(F.rand() * 55 + 5, 2))
    .withColumn("engine_temp_avg", F.round(F.rand() * 40 + 70, 2))
    .withColumn("brake_events", F.floor(F.rand() * 26))
    .withColumn("maintenance_flag", F.when(F.rand() < 0.25, 1).otherwise(0))
)

df_trips.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.bronze.vehicle_trips"
)