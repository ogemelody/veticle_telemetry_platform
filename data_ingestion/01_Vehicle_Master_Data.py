
# generators/vehicle_master.py
import pandas as pd
import random
from faker import Faker

fake = Faker()

VEHICLE_TYPES = ["car", "truck", "van", "bus"]


def generate_vehicles(n=200):
    data = []

    for i in range(n):
        data.append({
            "vehicle_id": f"VEH-{1000 + i}",
            "vin": fake.unique.license_plate(),
            "type": random.choice(VEHICLE_TYPES),
            "manufacturer": random.choice(["BMW", "Mercedes", "Audi", "VW", "Tesla"]),
            "model_year": random.randint(2015, 2025),
            "fuel_type": random.choice(["diesel", "petrol", "electric", "hybrid"]),
            "fleet_region": random.choice(["EU-North", "EU-South", "EU-West"])
        })

    # df = pd.DataFrame(data)
    # df.write.mode("overwrite").saveAsTable("lakehouse_eat_catalog.bronze.vehicles")

    df_pd = pd.DataFrame(data)
    df_spark = spark.createDataFrame(df_pd)
    df_spark.write.mode("overwrite").saveAsTable("lakehouse_eat_catalog.bronze.vehicles")
    return df_spark


if __name__ == "__main__":
    generate_vehicles()
