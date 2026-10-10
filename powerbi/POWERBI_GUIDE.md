# Microsoft Power BI Integration & Dashboard Design Guide

This guide provides step-by-step instructions to load the exported data marts from the `powerbi/` directory into Microsoft Power BI Desktop to build a professional 5-page Business Intelligence dashboard.

---

## 1. Exported Data Mart Files

The `powerbi/` folder contains six curated, clean CSV files ready for import:

| File Name | Purpose / Granularity | Primary Fields |
|---|---|---|
| `traffic_kpis.csv` | Executive KPI Cards | Total records, average speed, congestion %, severe count |
| `traffic_trends.csv` | Temporal Trends (hourly/daily) | Timestamp, hour, day_of_week, avg_speed, avg_volume, weather |
| `congestion_analysis.csv` | Segment Congestion Profile | Segment ID, road name, distances, % Low, % Medium, % High, % Severe |
| `model_metrics.csv` | ML Model Performance Matrix | Model architecture, accuracy, precision, recall, F1-score |
| `route_analysis.csv` | Spatial Network & Route Delays | Coordinates, segment lengths, free-flow time, delay minutes |
| `predictions.csv` | Test Set Predictions | Actual vs predicted congestion, speed, volume |

---

## 2. Step-by-Step Data Ingestion into Power BI

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to `e:\smarttraffic\powerbi\` and select all CSV files (`traffic_kpis.csv`, `traffic_trends.csv`, `congestion_analysis.csv`, `model_metrics.csv`, `route_analysis.csv`, `predictions.csv`).
4. Click **Load** (or **Transform Data** to inspect data types: ensure `timestamp` is DateTime, and numeric columns are Decimal / Whole Number).
5. In the **Model View**, establish the relationship between:
   - `congestion_analysis[segment_id]` (1) <---> `route_analysis[segment_id]` (*)
   - `congestion_analysis[segment_id]` (1) <---> `predictions[segment_id]` (*)

---

## 3. Recommended DAX Measures

Create a new table named `_Measures` and add these DAX formulas:

```dax
// 1. Overall Average Speed
Avg Speed = AVERAGE(traffic_trends[avg_speed])

// 2. Total Traffic Volume
Total Volume = SUM(traffic_trends[avg_volume])

// 3. Overall Congestion Rate (%)
Congestion Rate = 
DIVIDE(
    SUM(congestion_analysis[severe_pct]) + SUM(congestion_analysis[high_pct]),
    COUNTROWS(congestion_analysis) * 100,
    0
)

// 4. Total Travel Delay (Minutes)
Total Delay Minutes = SUM(route_analysis[delay_minutes])

// 5. Model Accuracy Benchmark
Top Model F1 = MAX(model_metrics[f1_score])
```

---

## 4. Multi-Page Dashboard Design

### PAGE 1: Traffic Overview (Executive Monitoring)
- **Top Row - KPI Cards**:
  - `Total Records Analyzed` (from `traffic_kpis`)
  - `Average System Speed (km/h)`
  - `Congestion Rate (%)`
  - `Severe Incident Count`
- **Center Visual**: Line and Clustered Column Chart
  - **Shared Axis**: `hour` (0 to 23)
  - **Column Values**: `avg_volume`
  - **Line Values**: `avg_speed`
- **Right Visual**: Donut Chart for `congestion_level` distribution.
- **Slicers**: `day_of_week`, `weather_main`.

### PAGE 2: Congestion Analytics & Bottlenecks
- **Top Visual**: Stacked Bar Chart of Segments by Congestion breakdown (`low_pct`, `medium_pct`, `high_pct`, `severe_pct`).
- **Bottom Left**: Heatmap / Matrix of `day_of_week` vs `hour` with cell background colored by `avg_volume`.
- **Bottom Right**: Clustered Column Chart of `weather_main` vs `avg_speed` showing adverse weather slowdowns.
- **Slicers**: `road_name`, `segment_id`.

### PAGE 3: ML Model Performance & Congestion Prediction
- **Top Visual**: Clustered Bar Chart comparing the 5 PySpark models:
  - **Y-Axis**: `model` (RandomForest, GBT, DecisionTree, LogisticRegression, NaiveBayes)
  - **Values**: `accuracy`, `precision`, `recall`, `f1_score`
- **Bottom Left**: Matrix displaying actual vs predicted congestion classes (Confusion Matrix representation).
- **Bottom Right**: Gauge visual showing the Best Model's F1-Score vs a 0.90 target threshold.

### PAGE 4: Route Optimization & Network Delay
- **Top Visual**: Map Visual using `source_lat`, `source_lon`, `target_lat`, `target_lon` colored by `congestion_level`.
- **Center Visual**: Waterfall Chart of cumulative travel time along the I-94 and I-35 corridors.
- **Table Visual**: Segment Bottleneck Ranking:
  - Columns: `road_name`, `distance_km`, `average_speed`, `delay_minutes`, `congestion_level`
  - Conditional formatting: Highlight rows with `delay_minutes > 5.0` in light red.

### PAGE 5: Real-Time Stream Monitoring
- **Visual 1**: Streaming card indicating current network operational status: `NORMAL`, `WARNING`, or `GRIDLOCK`.
- **Visual 2**: Live Line Chart of incoming speed vs volume for critical junctions (Airport, Downtown Minneapolis, Downtown St. Paul).
- **Visual 3**: Incident alert feed table highlighting high-priority traffic management interventions.
