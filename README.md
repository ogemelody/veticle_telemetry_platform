# 🚗 Vehicle Telemetry Platform


 AI-augmented data pipeline for fleet vehicle health monitoring and predictive maintenance recommendations using Databricks Lakehouse, Delta Lake, and Mosaic AI.

![Dashboard](src/dashboard.png)

## Project Overview
 
This platform ingests simulated IoT vehicle telemetry, 
processes it through a medallion architecture (Bronze → Silver → Gold),
and generates per-vehicle maintenance recommendations using LLM-powered 
operational intelligence via Mosaic AI (databricks-meta-llama-3-3-70b-instruct).

**In production, this pattern powers:**
- Real-time fleet health monitoring for automotive OEMs and fleet operators.
- Predictive maintenance alerting to reduce downtime and extend vehicle lifespan.
- Cost attribution and ROI analysis for maintenance spend.
- Risk classification and operational safety scoring.

## Architecture
- Databricks Autoloader ingestion (batch + streaming)
- Medallion architecture (Bronze / Silver / Gold)
- Real-time vehicle telemetry simulation
- Fleet health scoring model


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