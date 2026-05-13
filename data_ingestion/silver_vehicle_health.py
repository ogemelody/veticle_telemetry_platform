# databricks/silver/vehicle_health_features.py

from pyspark.sql.functions import avg, col, min, max

df = spark.table("lakehouse_eat_catalog.bronze.vehicles")

df_trip_info = spark.table("lakehouse_eat_catalog.bronze.vehicle_trips")

silver_vehicle_prop = df.groupBy("vehicle_id").agg(

    avg("battery_health").alias("avg_battery_health")
)

silver_trip_info = df.groupBy("vehicle_id").agg(
    avg("avg_speed").alias("vehicle_avg_speed"),
    min("brake_events").alias("min_brake_events"),
    max("brake_events").alias("max_brake_events"),
    avg("fuel_used").alias("avg_fuel_used"),
    avg("engine_temp").alias("avg_engine_temp")

)
df_with_avg = df.join(df_trip_info, on="vehicle_id", how="left")

df_with_avg.write.mode("overwrite").saveAsTable("lakehouse_eat_catalog.silver.vehicle_health_features")