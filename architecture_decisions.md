

##  Decision 1 — Data Ingestion: Why I Scrapped Azure

### What was planned
The original architecture used:
- **Azure Event Hub** for real-time POS/telemetry streaming
- **Azure SQL Database** with Change Data Capture (CDC) enabled
- **Databricks LakeFlow Connect** to pull CDC changes into Bronze Delta tables

### What blocked it

**LakeFlow Connect compute policy error:**  
LakeFlow Connect requires a dedicated gateway cluster. On the Databricks Free Edition, the compute policy enforced a minimum of 5 worker nodes. 
Reducing to 1 worker still triggered a policy violation error —
the gateway cluster configuration was locked at the platform level.


**Azure cost exposure:**  
With Event Hub and Azure SQL both running, costs were accumulating with no data moving. Keeping live cloud resources burning money while blocked on a compute policy was not a viable position.

### Decision made
Destroy the Azure resources. Rebuild ingestion entirely within Databricks using:
- A Python data generator simulating IoT telemetry (runs inside a Databricks notebook)
- DBFS as the landing zone (no external dependency)
- Auto Loader for streaming ingestion into Bronze Delta tables



---

##  Decision 2 — Bronze Layer: Auto Loader over Direct Reads

### Options considered

| Option | Description | Rejected because |
|---|---|---|
| `spark.read` (batch) | Read all files in one shot | No incremental processing — re-reads everything on each run |
| `spark.readStream` with glob | Stream all matching files | No checkpoint — cannot track what has been processed |
| **Auto Loader** | Incrementally ingests new files using checkpoint | Chosen |

### Decision made: Auto Loader

```python
spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", checkpoint_path) \
    .load(landing_path) \
    .writeStream \
    .trigger(availableNow=True) \
    .option("checkpointLocation", checkpoint_path) \
    .toTable("lakehouse_eat_catalog.bronze.vehicle_telemetry")
```

### Rationale
Auto Loader tracks exactly which files have been processed using a checkpoint. This means:
- No duplicate ingestion when new files arrive
- Schema inference handled automatically
- Native integration with Delta Lake and Unity Catalog
- Scales to millions of files without listing overhead (uses file notification mode at scale)

---

##  Decision 3 — Trigger Strategy: availableNow vs Continuous

### Options

| Trigger | Behaviour | Use case |
|---|---|---|
| `trigger(processingTime='60 seconds')` | Processes new files every 60 seconds, runs indefinitely | Production near-real-time streaming |
| `trigger(availableNow=True)` | Processes all available files then stops | Cost-controlled environments |
| `trigger(once=True)` | Processes one micro-batch then stops (deprecated) | Legacy |

### Decision made: `availableNow=True`

### Rationale
On the Databricks Free Edition, a continuously running stream consumes compute credits indefinitely. `availableNow=True` gives the exact same incremental behaviour — it processes only new files since the last checkpoint — but shuts down the cluster after completion.

The checkpoint state is preserved between runs, so the next execution picks up exactly where the last one stopped. This is behaviourally identical to continuous streaming for batch-frequency data.

### What changes in production
Switch to `trigger(processingTime='60 seconds')` inside a long-running cluster or Databricks Workflows scheduled job. For true sub-minute latency, remove the trigger entirely (default micro-batch mode).


---

##  Decision 4 — Silver Layer: Separate Tables over One Flat Table

### Options considered

| Option | Description | Rejected because |
|---|---|---|
| Single wide Silver table | Join all Bronze tables into one flat table at Silver | Violates separation of concerns; one source's schema change breaks the whole table |
| **Separate Silver tables** | One aggregated table per domain | Chosen |

### Decision made: Three separate Silver tables

```
silver.telemetry_agg      — CAN bus signals, aggregated per vehicle
silver.trips_agg          — Trip behaviour metrics, aggregated per vehicle
silver.vehicle_profile    — Vehicle dimension (manufacturer, type, region)
```

### Rationale

Silver's job is to clean, validate, and aggregate — not to serve dashboards. Keeping tables focused means:

- **Independent evolution:** Trip schema can change without touching telemetry
- **Reusability:** `silver.vehicle_profile` can serve multiple Gold tables
- **Clearer lineage:** Unity Catalog lineage shows exactly which Bronze table feeds which Silver table
- **Easier testing:** Each Silver table can be validated in isolation

### Where flattening belongs
Gold is the intentionally wide layer. `gold.fleet_kpis` joins all three Silver tables because that join is done once, at serving time, for a specific analytical purpose. That is the correct place for a wide table.

---

## Decision 5 — CAN Bus Signals: vehicle_telemetry over Separate Table

### What was considered
Creating a separate `bronze.can_bus_signals` table with additional fields: `engine_coolant_temp_c`, `dtc_code_count`, `battery_voltage_v`, `brake_pad_wear_pct`, `odometer_km`.

### Decision made: Use existing vehicle_telemetry columns

The `bronze.vehicle_telemetry` table already contained: `engine_temp`, `rpm`, `fuel_level`, `tire_pressure`, `battery_health`. These are CAN bus-derived signals. Creating a separate table would duplicate data unnecessarily.

### What was done instead
- Renamed columns with proper automotive terminology in Silver (`avg_engine_temp_c`, `avg_engine_rpm`, `avg_tire_pressure_psi`)
- These signal names map directly to real OBD-II / CAN bus data identifiers
- The Gold AI prompt explicitly references these as CAN bus signals

### Real-world alignment
In production fleet telematics, CAN bus signals arrive as part of the telemetry stream from the OBD-II port — they are not a separate data source. A separate table would have been architecturally incorrect. `vehicle_telemetry` modelling these signals as a unified stream is the right pattern.

---

## 6. Engineering Quality Decisions

### Z-Ordering

**Applied to:** `bronze.vehicle_telemetry`, `gold.fleet_kpis`

```sql
OPTIMIZE lakehouse_eat_catalog.bronze.vehicle_telemetry
ZORDER BY (vehicle_id, timestamp);

OPTIMIZE lakehouse_eat_catalog.gold.fleet_kpis
ZORDER BY (vehicle_id, risk_level);
```

**Why:** Dashboard queries filter heavily by `vehicle_id` and `risk_level`. Z-ordering co-locates related data in the same Parquet files, reducing the amount of data scanned per query. On the free tier this also reduces compute time and credit consumption.

**Trade-off:** Z-ordering is a write-time cost — `OPTIMIZE` takes longer to run. On small datasets the benefit is minimal. At scale (millions of telemetry rows), this becomes critical.

---

### Null Handling

Telemetry streams frequently produce nulls — sensor dropout, connection loss, device restart. Nulls in health score calculations produce null results, which break dashboard counters.

```python
from pyspark.sql.functions import coalesce, lit

silver_telemetry = df_telemetry.groupBy("vehicle_id").agg(
    avg(coalesce(col("engine_temp"), lit(0.0))).alias("avg_engine_temp_c"),
    avg(coalesce(col("battery_health"), lit(100.0))).alias("avg_battery_health"),
    avg(coalesce(col("tire_pressure"), lit(32.0))).alias("avg_tire_pressure_psi")
)
```

**Decision:** Use `coalesce` with domain-appropriate defaults (not zero, which would falsely indicate no pressure). In production, null handling strategy would be documented per-field and reviewed with domain experts.

---

### Schema Enforcement

Auto Loader infers schema on first run and stores it in the checkpoint location. Subsequent runs enforce that schema — new unexpected columns are rejected, missing columns raise errors.

```python
.option("cloudFiles.schemaEvolutionMode", "rescue")
```

**`rescue` mode:** Unknown columns are captured in a `_rescued_data` column rather than causing the stream to fail. This prevents pipeline outages when upstream senders add fields, while preserving the unknown data for investigation.

**Trade-off:** In strict environments, `schemaEvolutionMode` should be `"none"` to hard-fail on unexpected schema changes. Rescue mode is appropriate for development and early production where upstream schemas are still evolving.

---

### Duplicate Detection

Telemetry devices can send the same reading twice (network retry, at-least-once delivery). Without deduplication, Silver aggregations are inflated.

```sql
-- Applied in Silver transformation before aggregation
WITH deduped AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY vehicle_id, timestamp
      ORDER BY timestamp
    ) AS rn
  FROM lakehouse_eat_catalog.bronze.vehicle_telemetry
)
SELECT * FROM deduped WHERE rn = 1
```

**Decision:** Deduplicate on `(vehicle_id, timestamp)` composite key before aggregating in Silver. This is more reliable than Delta's `MERGE` deduplication for streaming scenarios where the same event can arrive in different micro-batches.

---


---

### Outlier Validation

After filtering hard-invalid values, statistical outliers may still exist — values that are technically possible but anomalous (e.g. `speed = 298 km/h` for a bus in a city fleet).

```python
from pyspark.sql.functions import percentile_approx, stddev, mean

# Compute bounds dynamically per vehicle type
stats = df_telemetry.groupBy("vehicle_id").agg(
    mean("speed").alias("mean_speed"),
    stddev("speed").alias("std_speed")
)

# Flag readings beyond 3 standard deviations
df_flagged = df_telemetry.join(stats, "vehicle_id") \
    .withColumn("speed_outlier",
        col("speed") > (col("mean_speed") + 3 * col("std_speed"))
    )
```

**Decision:** Flag outliers rather than remove them. Outlier flags are surfaced in Silver as `warning_detected`. The AI_QUERY prompt in Gold can then reason about whether flagged readings constitute a genuine risk.

---

## 7. Unity Catalog: Lineage, Tags & Governance

### Lineage

Unity Catalog automatically captures lineage when tables are created with `spark.table()` or SQL `CREATE TABLE AS SELECT`. Every Bronze → Silver → Gold transformation in this project is trackable in the Catalog Explorer under the **Lineage** tab.

**What lineage shows for this project:**
- `gold.ai_fleet_monitoring` ← `gold.fleet_kpis` ← `silver.telemetry_agg`, `silver.trips_agg`, `silver.vehicle_profile`
- `silver.telemetry_agg` ← `bronze.vehicle_telemetry`
- `silver.trips_agg` ← `bronze.vehicle_trips`
- `silver.vehicle_profile` ← `bronze.vehicle`

This  data lineage graph can be presented to a data governance team or auditor.

---

## 7. What I Would Do Differently in Production

| Area | Free Tier Decision | Production Decision |
|---|---|---|
| Ingestion source | Python generator → DBFS | IoT Hub / Event Hub → ADLS Gen2 → Auto Loader |
| Streaming trigger | `availableNow=True` | `processingTime='60 seconds'` or continuous |
| Compute | Serverless Starter (shared) | Dedicated cluster with autoscaling policy |
| LakeFlow CDC | Skipped (compute policy) | LakeFlow Connect with dedicated gateway cluster |
| Schema enforcement | Rescue mode | Strict mode with quarantine table |
| Duplicate handling | SQL window deduplication | Delta `MERGE` with `whenNotMatched` insert |
| Secrets | None (no external connections) | Databricks Secrets + Azure Key Vault |
| Orchestration | Manual notebook runs | Databricks Workflows with dependency graph |
| Monitoring | None | Databricks Lakehouse Monitoring on Silver + Gold |
| Dashboard | AIBI (Genie) | AIBI + Power BI for executive reporting |

