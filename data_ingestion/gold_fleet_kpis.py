from pyspark.sql.functions import col, when

df = spark.table(
    "lakehouse_eat_catalog.silver.vehicle_health_features"
)

gold = (
    df.withColumn(
        "health_score",
        (
            col("avg_battery_health") * 0.4 +
            (120 - col("avg_engine_temp")) * 0.3 +
            (140 - col("avg_speed")) * 0.3
        )
    )
    .withColumn(
        "risk_level",
        when(col("health_score") > 85, "GOOD")
        .when(col("health_score") > 70, "WARNING")
        .otherwise("CRITICAL")
    )
)

gold.write.mode("overwrite").saveAsTable(
    "lakehouse_eat_catalog.gold.fleet_kpis"
)