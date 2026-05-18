# 🚗 Vehicle Telemetry Platform


 AI-augmented data pipeline for fleet vehicle health monitoring and predictive maintenance recommendations using Databricks Lakehouse, Delta Lake, and Mosaic AI.

![Dashboard](src/dashboard.png)

## Project Overview
 
This platform ingests simulated IoT vehicle telemetry, 
processes it through a medallion architecture (Bronze → Silver → Gold),
and generates per-vehicle maintenance recommendations using LLM-powered 
operational intelligence via Mosaic AI (Meta LLaMA 3.3 70B).

**In production, this pattern powers:**
- Real-time fleet health monitoring for automotive OEMs and fleet operators.
- Predictive maintenance alerting to reduce downtime and extend vehicle lifespan.
- Cost attribution and ROI analysis for maintenance spend.
- Risk classification and operational safety scoring.

## Architecture
![architecture](src/vehicle_telemetry_architecture.png)

## 🚗 Use Cases in Automotive
 
### 1. **Predictive Maintenance for Fleet Operators**
Monitor thousands of vehicles in real-time. AI identifies which vehicles need maintenance before failure occurs, reducing costly downtime.
 
**Example insight:**
> "Vehicle VEH-1025 is in CRITICAL risk. Engine coolant temperature is elevated at 100.53°C, combined with high RPM of 5251. Recommend urgent cooling system inspection to prevent engine failure."
 
**Impact:** Reduce unplanned maintenance from 30% to <5% of fleet workload.
 
---
 
### 2. **OEM Warranty & Recall Management**
Aggregate telemetry across a vehicle model line. Detect systemic failures earlier (e.g., all Mercedes trucks showing brake pad wear > 85%).
 
**Example:** If 10+ vehicles of a specific model show identical DTC codes within a time window, escalate to engineering for potential recall.
 
**Impact:** Identify safety issues before they reach customer complaints.
 
---
 
### 3. **Fleet Cost Attribution**
Connect maintenance spend to telemetry signals. Build ROI models showing which preventive actions actually reduce overall costs.
 
**Example analysis:**
- Cost: €500/vehicle for quarterly coolant system flush
- Benefit: Reduced engine failures (−€8,000 per failure)
- ROI: 1600% for targeted high-risk fleet segments
---
 
### 4. **Driver Behaviour & Safety Scoring**
Identify risky driving patterns (sustained high RPM, aggressive braking) correlated with vehicle failure and insurance claims.
 
**Example:** Drivers in the top 10% for aggressive driving show 40% higher brake wear. Implement driver coaching program.
 
---
 
### 5. **Supply Chain & Parts Planning**
Predict maintenance demand by part type. If 25% of fleet shows brake pad wear >80%, procurement knows to stock 250+ brake pads next month.
 
**Example:** AI predicts battery failures in 40 vehicles over next 30 days → order 45 units, avoid stockouts.
 
---
 
### 6. **Connected Vehicle & Telematics Integration**
Real-world fleet systems (e.g. ZF Aftermarket, Bosch Connected Services) stream live CAN bus data into this pipeline. Scale from 33 vehicles (demo) to 100,000+ vehicles with the same architecture.
 
**Architectural advantage:** Auto Loader + Delta Lake handles late arrivals, duplicates, and schema changes.
 






## Features
- Historical trip simulation
- Real-time telemetry streaming (Databricks-native)
- Bronze ingestion pipelines using Auto Loader
- Silver layer feature engineering
- Gold layer fleet KPI scoring

## Tech Stack
- Databricks (Spark Structured Streaming)
- Delta Lake
- Python

## Key Skills Demonstrated
- Lakehouse architecture design
- Streaming + batch ingestion
- Schema evolution handling
- Automotive telemetry modeling
- Production-grade data pipeline design