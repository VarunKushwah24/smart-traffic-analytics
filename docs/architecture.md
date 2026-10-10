# System Architecture & Scalability Design

This document details the software architecture, data flow, distributed computing paradigms, and scalability considerations of the **Smart Traffic Congestion Prediction and Intelligent Route Analytics System**.

---

## 1. End-to-End System Architecture

```text
+---------------------------------------------------------------------------------------------------+
|                                       DATA INGESTION LAYER                                        |
|                                                                                                   |
|   +----------------------------------+                   +------------------------------------+   |
|   |  Historical Batch Archive        |                   |  Real-Time Sensor Telemetry        |   |
|   |  - UCI Metro Interstate Dataset  |                   |  - IoT Road Loop Detectors         |   |
|   |  - Twin Cities Corridor Network  |                   |  - Apache Kafka ('traffic-events') |   |
|   +-----------------+----------------+                   +-----------------+------------------+   |
+---------------------|------------------------------------------------------|----------------------+
                      |                                                      |
                      v                                                      v
+---------------------------------------------------------------------------------------------------+
|                                  APACHE SPARK COMPUTING ENGINE                                    |
|                                                                                                   |
|   +----------------------------------+                   +------------------------------------+   |
|   |  PySpark Batch Processing        |                   |  Spark Structured Streaming        |   |
|   |  - Ingestion with StructType     |                   |  - Real-time JSON parser           |   |
|   |  - Deduplication & Outlier Clean |                   |  - Sliding-window micro-batches    |   |
|   |  - Spatio-Temporal Feature Eng.  |                   |  - Low-latency feature generation  |   |
|   +-----------------+----------------+                   +-----------------+------------------+   |
|                     |                                                      |                      |
|                     v                                                      v                      |
|   +----------------------------------+                   +------------------------------------+   |
|   |  PySpark MLlib Machine Learning  |                   |  Streaming Model Inference         |   |
|   |  - 5 Classifiers (GBT, RF, DT,   |                   |  - Live Congestion Classification  |   |
|   |    LR, NaiveBayes)               |                   |  - Automatic Incident Alerting     |   |
|   |  - 3 Regressors (LR, RF, GBT)    |                   |  - Output: Memory/CSV File Sink    |   |
|   |  - Model Persistence in models/  |                   |                                    |   |
|   +-----------------+----------------+                   +-----------------+------------------+   |
+---------------------|------------------------------------------------------|----------------------+
                      |                                                      |
                      +--------------------------+---------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                                 INTELLIGENT ROUTING & ANALYTICS                                   |
|                                                                                                   |
|   +-------------------------------------------------------------------------------------------+   |
|   |  Dynamic Dijkstra Route Optimization                                                      |   |
|   |  - Directed Road Graph: 10 Junction Nodes, 24 Road Corridor Segments                      |   |
|   |  - Congestion-Penalized Dynamic Cost Function:                                            |   |
|   |    Cost = (Distance / Speed) * 60 * (1 + alpha * CongestionMultiplier)                    |   |
|   |  - Primary Optimal Path & Secondary Alternative Corridor Route Calculation                |   |
|   +---------------------------------------------+---------------------------------------------+   |
+-------------------------------------------------|-------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 PRESENTATION & BUSINESS INTELLIGENCE                              |
|                                                                                                   |
|   +-----------------------------------------+   +---------------------------------------------+   |
|   |  Streamlit BI Web Application           |   |  Microsoft Power BI Data Marts (powerbi/)   |   |
|   |  - 8 Interactive Modular Pages          |   |  - 6 Production-Ready Curated CSV Marts     |   |
|   |  - Real-time Inference & Sliders        |   |  - 5-Page Dashboard Layout & Visual Guide   |   |
|   |  - Plotly Spatial Geographic Maps       |   |  - Custom DAX Measures & Slicers            |   |
|   +-----------------------------------------+   +---------------------------------------------+   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Why Apache Spark is Mandatory for this Problem

1. **Massive Data Velocity & Volume:** Urban highway networks have thousands of inductive loop detectors and radar sensors recording flow every 30 seconds. A single metropolitan area generates tens of millions of records daily. Single-machine libraries like Pandas and Scikit-Learn must fit all records into RAM and are incapable of scaling horizontally across clusters.
2. **Unified Batch and Stream Processing:** Spark Structured Streaming uses the exact same DataFrame API, Catalyst optimizer, and MLlib scoring pipeline for both historical batch training and live streaming micro-batches, preventing architectural divergence between batch and real-time code.
3. **Catalyst Optimizer & Tungsten Engine:** Spark optimizes execution plans by pruning unused columns, pushing down filters directly to Parquet files, and generating compact JVM bytecode at runtime.
4. **Resilience & Fault Tolerance:** Spark automatically tracks partition lineages in Directed Acyclic Graphs (DAGs). If a node fails, Spark recomputes only the lost partition rather than restarting the entire job.

---

## 3. Distributed Processing Best Practices Applied

- **Explicit Schema Enforcement:** All data ingestion uses `StructType` rather than schema inference to avoid costly pre-reads.
- **Partition Tuning:** Configured shuffle partitions (`spark.sql.shuffle.partitions = 4`) appropriate for the local node cores to prevent idle partition overhead.
- **No Unbounded Driver Collections:** Full datasets are never pulled into driver memory using `.collect()`. Aggregations and summaries are computed in Spark SQL and only small result tables are exported.
- **Columnar Storage:** Features and processed data are persisted using Parquet with snappy compression, drastically reducing I/O footprint.
