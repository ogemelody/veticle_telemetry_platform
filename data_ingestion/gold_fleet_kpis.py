# databricks/gold/fleet_kpis.py
from pyspark.sql.functions import avg, col,min,max

df = spark.table("lakehouse_eat_catalog.silver.vehicle_health_features")

gold = df.withColumn(
    "health_score",
    (col("avg_battery_health") * 0.4 +
     (120 - col("engine_temp_avg")) * 0.3 +
     (140 - col("avg_speed")) * 0.3)
)

gold.write.mode("overwrite").saveAsTable("lakehouse_eat_catalog.gold.fleet_kpis")
