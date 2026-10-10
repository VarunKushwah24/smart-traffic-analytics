# Real-Time Smart Traffic Congestion Prediction and Intelligent Route Optimization Using PySpark, Kafka and Machine Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache_Spark-4.2.0-orange.svg)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![Power BI](https://img.shields.io/badge/Power_BI-Compatible-yellow.svg)](https://powerbi.microsoft.com/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

An end-to-end Big Data Analytics and Business Intelligence project developed for the **CSET-371** curriculum. The platform ingests large-scale traffic telemetry, executes distributed preprocessing and feature engineering using **Apache Spark (PySpark)**, benchmarks 5 PySpark MLlib classification and regression models, executes real-time event streaming via **Apache Kafka** and **Spark Structured Streaming**, provides dynamic **Dijkstra-based congestion-penalized route optimization**, serves an 8-page interactive **Streamlit BI dashboard**, and exports production data marts for **Microsoft Power BI**.

---

## 1. System Architecture

```text
                  +----------------------------------------------+
                  |  Authentic Dataset (UCI Metro Interstate &   |
                  |     Multi-Segment Corridor Sensor Network)   |
                  +----------------------+-----------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Data Ingestion & Schemas    |
                         |     (Batch CSV / Parquet)     |
                         +---------------+---------------+
                                         |
                                         v
                    +-----------------------------------------+
                    |  PySpark Cleaning & Transformations    |
                    | (Null handling, Outliers, Aggregations) |
                    +--------------------+--------------------+
                                         |
                                         v
                    +-----------------------------------------+
                    |        PySpark Feature Engineering      |
                    | (Temporal, Peak, Rush Hour, Rolling,    |
                    |  VectorAssembler, Scaler, StringIndexer)|
                    +--------------------+--------------------+
                                         |
                    +--------------------+--------------------+
                    |                                         |
                    v                                         v
    +-------------------------------+         +-------------------------------+
    |  Exploratory Data Analysis    |         | 5+ PySpark MLlib Models       |
    | (Distributions, Correlations, |         | - Logistic Regression         |
    |  Hourly/Daily Traffic Volume) |         | - Decision Tree Classifier    |
    +---------------+---------------+         | - Random Forest Classifier    |
                    |                         | - GBT Classifier (OneVsRest)  |
                    |                         | - Naive Bayes Classifier      |
                    |                         | + Linear & GBT Regressors     |
                    |                         +---------------+---------------+
                    |                                         |
                    +--------------------+--------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   Model Evaluation & Metrics  |
                         | (Accuracy, F1, Precision,     |
                         |  Recall, ROC-AUC, Conf Matrix)|
                         +---------------+---------------+
                                         |
                     +-------------------+-------------------+
                     |                                       |
                     v                                       v
     +-------------------------------+       +-------------------------------+
     |  Intelligent Route Analytics  |       | Real-Time Streaming Pipeline  |
     |   - Road Network Graph        |       |   - Kafka Event Producer      |
     |   - Dynamic Dijkstra Routing  |       |   - Spark Structured Streaming|
     |   - Congestion-Weighted Cost  |       |   - Live Model Inference      |
     +---------------+---------------+       +---------------+---------------+
                     |                                       |
                     +-------------------+-------------------+
                                         |
                                         v
                         +-------------------------------+
                         | Decision Support System (DSS) |
                         | (Thresholds, Reroute Alerts,  |
                         |  Traffic Management Insights) |
                         +---------------+---------------+
                                         |
                     +-------------------+-------------------+
                     |                                       |
                     v                                       v
     +-------------------------------+       +-------------------------------+
     |   Streamlit BI Dashboard      |       | Power BI Data Marts (powerbi/)|
     |  (8 Interactive Modules, KPIs,|       | (Clean CSV/Parquet Exports,   |
     |   Route Maps, Live Stream)    |       |  DAX measures, Template guide)|
     +-------------------------------+       +-------------------------------+
```

---

## 2. Key Features & Technologies

- **Distributed Data Processing:** Apache Spark 4.2.0 / PySpark SQL DataFrames with Catalyst optimizer, Tungsten bytecode generation, and Parquet columnar output.
- **5 PySpark Machine Learning Classifiers:**
  - Multinomial Logistic Regression
  - Decision Tree Classifier
  - Random Forest Classifier (Top Ensemble)
  - Gradient-Boosted Trees (GBTClassifier with OneVsRest wrapper)
  - Naive Bayes (Gaussian continuous features)
- **Continuous Speed Regressors:** Linear Regression, Random Forest Regressor, GBT Regressor ($R^2 > 0.96$).
- **Intelligent Dijkstra Route Optimization:** Graph of 10 highway junctions and 24 directed segments. Dynamic congestion penalty ($\alpha$) avoids bottlenecks and calculates secondary contingency routes.
- **Real-Time Streaming:** Dual-mode Apache Kafka event publisher and Spark Structured Streaming consumer with live micro-batch scoring.
- **Streamlit BI Application:** 8 rich interactive modules with KPI cards, Plotly charts, live inference inputs, and geographic route maps.
- **Microsoft Power BI Integration:** 6 curated data marts exported in `powerbi/` with comprehensive DAX and visual layout guides.
- **UN SDG Alignment:** Quantified impact for SDG 9 (Infrastructure), SDG 11 (Sustainable Cities), and SDG 13 (Climate Action).

---

## 3. Directory Structure

```text
smart-traffic-big-data/
├── README.md                           # Master documentation
├── requirements.txt                    # Pinned python dependencies
├── pytest.ini                          # Test configuration
├── project_health_check.py             # 12-point automated health check
├── docker-compose.yml                  # Optional Kafka + Zookeeper container setup
│
├── config/
│   └── config.yaml                     # Centralized paths, Spark & ML hyperparameters
│
├── data/
│   ├── raw/                            # Authentic Metro Interstate & Corridor datasets
│   ├── processed/                      # Parquet and CSV engineered features
│   └── streaming/                      # Input & output real-time stream storage
│
├── src/
│   ├── spark/                          # SparkSession, Ingestion, Preprocessing, Feature Eng, EDA
│   ├── ml/                             # 5 MLlib Classifiers, Regressors, Evaluator, Trainer
│   ├── routing/                        # RoadNetworkGraph and Dynamic Dijkstra Algorithm
│   ├── streaming/                      # Kafka Producer & Spark Structured Streaming Pipeline
│   └── utils/                          # YAML config loader and structured logger
│
├── dashboard/
│   └── app.py                          # Streamlit 8-module interactive BI dashboard
│
├── powerbi/
│   ├── traffic_kpis.csv                # High-level metrics for Power BI card visuals
│   ├── traffic_trends.csv              # Hourly & daily aggregated trends
│   ├── congestion_analysis.csv         # Segment-level congestion profiles
│   ├── model_metrics.csv               # Model evaluation comparison matrix
│   ├── route_analysis.csv              # Road network topology and segment delays
│   ├── predictions.csv                 # Test predictions sample
│   └── POWERBI_GUIDE.md                # Page-by-page dashboard design and DAX guide
│
├── scripts/
│   ├── download_dataset.py             # Dataset downloader and topology generator
│   ├── run_pipeline.py                 # Full batch pipeline execution runner
│   ├── train_models.py                 # Standalone ML training and evaluation script
│   ├── start_streaming.py              # Real-time event streaming runner
│   ├── start_dashboard.py              # Streamlit dashboard launcher
│   └── generate_powerbi_marts.py       # Power BI export generator
│
├── tests/
│   ├── test_preprocessing.py           # Unit tests for data cleaning and schema
│   ├── test_models.py                  # Unit tests for ML models initialization
│   └── test_dijkstra.py                # Unit tests for graph routing and alternate paths
│
└── docs/
    ├── architecture.md                 # System architecture and scalability design
    ├── methodology.md                  # Preprocessing, ML formulations & cost functions
    ├── dataset.md                      # Schema, data dictionary, and download sources
    ├── viva_questions.md               # 50+ viva voce questions and simple answers
    └── presentation_outline.md         # 20-slide 10-15 minute presentation guide
```

---

## 4. Experimental Results

The models were evaluated on an 80/20 train/test holdout split using PySpark's `MulticlassClassificationEvaluator` and `RegressionEvaluator`:

### PySpark MLlib Classification Benchmark:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | Status |
|---|---|---|---|---|---|
| **GBTClassifier (OneVsRest)** | **98.83%** | **98.79%** | **98.83%** | **0.9881** | **Top Performer** |
| **RandomForestClassifier** | **98.71%** | **98.66%** | **98.71%** | **0.9868** | Highly Robust Ensemble |
| **DecisionTreeClassifier** | **98.25%** | **98.24%** | **98.25%** | **0.9824** | Interpretable Tree |
| **LogisticRegression** | **97.86%** | **97.78%** | **97.86%** | **0.9782** | Linear Baseline |
| **NaiveBayes (Gaussian)** | **87.06%** | **93.71%** | **87.06%** | **0.9024** | Probabilistic Benchmark |

### PySpark Speed Prediction Regressors:

| Regression Architecture | RMSE (km/h) | MAE (km/h) | $R^2$ Score |
|---|---|---|---|
| **LinearRegression** | 0.104 | 0.085 | **0.9998** |
| **GBTRegressor** | 0.568 | 0.270 | **0.9940** |
| **RandomForestRegressor** | 1.314 | 0.901 | **0.9678** |

---

## 5. How to Run the Project (Step-by-Step)

### Prerequisites:
- Python 3.10+
- Java JRE/JDK 8, 11, 17, or 23

### Step 1: Clone and Set Up Virtual Environment
```bash
# Navigate to project directory
cd e:\smarttraffic

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Windows CMD:
.\.venv\Scripts\activate.bat

# Install pinned requirements
pip install -r requirements.txt
```

### Step 2: Download & Prepare Datasets
```bash
python scripts/download_dataset.py
```

### Step 3: Run the Complete PySpark Batch Pipeline
```bash
# Executes Data Ingestion, Cleaning, Feature Engineering, EDA, Model Training, and Power BI Exports
python scripts/run_pipeline.py
```

### Step 4: Run Automated System Health Check
```bash
python project_health_check.py
```
*(All 12 checks will report `[ PASS ]`)*

### Step 5: Run Unit Tests
```bash
python -m pytest -v
```
*(All 8 test cases will report `PASSED`)*

### Step 6: Launch the Streamlit BI Dashboard
```bash
streamlit run dashboard/app.py
```
*(Access the interactive dashboard in your browser at `http://localhost:8501`)*

### Step 7: Run Real-Time Streaming Demonstration
```bash
python scripts/start_streaming.py
```
*(Starts the event producer and Spark Structured Streaming micro-batch inference)*

---

## 6. Demonstration Flow for College Evaluators (10–15 Minutes)

1. **System Health Check (1 min):** Run `python project_health_check.py` to prove all 12 modules pass.
2. **PySpark Pipeline Execution (2 mins):** Run `python scripts/train_models.py` to show live Spark DAG execution and real model comparison metrics in the terminal.
3. **Streamlit Executive Overview (2 mins):** Open `dashboard/app.py`. Walk through the 4 KPI cards and system architecture diagram.
4. **Traffic Analytics & Patterns (2 mins):** Demonstrate the dual-axis hourly volume vs. speed chart and adverse weather speed degradation.
5. **Congestion Prediction Lab (2 mins):** Adjust volume, speed, and weather sliders to obtain live ML inference badges and decision support advisories.
6. **Intelligent Dijkstra Routing (3 mins):**
   - Select Origin: `Downtown Minneapolis`, Destination: `Downtown St. Paul`.
   - Show how increasing the congestion penalty ($\alpha$) dynamically diverts the route around congested corridors and compare it with the alternative path on the interactive Plotly map.
7. **Real-Time Streaming Demo (2 mins):** Navigate to the Real-Time tab. Click **"Push 5 Live Test Sensor Events"** and show live micro-batch ingestion.
8. **Power BI & SDG Alignment (1 min):** Showcase the exported CSV data marts in `powerbi/` and summarize alignment with SDGs 9, 11, and 13.

---

## 7. Submission Checklist & Screenshots Guide

Capture the following screenshots for your project report and presentation:
1. **Health Check Output:** Terminal displaying `OVERALL HEALTH CHECK STATUS: 12/12 CHECKS PASSED`.
2. **Spark Model Training Output:** Terminal table comparing the 5 classification models and regression metrics.
3. **PyTest Execution:** Terminal showing `8 passed in ...s`.
4. **Streamlit Executive Overview:** Top KPI cards and congestion donut chart.
5. **Streamlit Traffic Analytics:** Dual-axis hourly volume vs. speed chart.
6. **Streamlit Prediction Lab:** Input sliders with predicted `SEVERE GRIDLOCK` or `LOW CONGESTION` badge.
7. **Streamlit Route Optimization:** Interactive geographic map displaying the recommended green route line.
8. **Generated Plot:** `results/plots/model_comparison_metrics.png`.
9. **Generated Plot:** `results/plots/confusion_matrix_best_model.png`.
10. **Power BI Directory:** File explorer showing `powerbi/` data marts and `POWERBI_GUIDE.md`.

---

## 8. License & Academic Attribution

This project is released under the Apache-2.0 License.  
Developed for CSET-371 Big Data Analytics & Business Intelligence coursework.
