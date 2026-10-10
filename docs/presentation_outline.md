# 10–15 Minute Project Presentation Outline

**Project Title:** Smart Traffic Congestion Prediction and Intelligent Route Analytics Using Apache Spark  
**Target Duration:** 12–15 Minutes | 20 Slides  
**Audience:** Academic Evaluators, External Examiners, and Project Committee

---

### Slide 1: Title Slide (0:00 - 0:45)
- **Title:** Smart Traffic Congestion Prediction and Intelligent Route Optimization
- **Subtitle:** An End-to-End Big Data Analytics & Business Intelligence System
- **Technologies:** Apache Spark, PySpark MLlib, Spark Structured Streaming, Kafka, Dijkstra, Streamlit, Power BI
- **Presenter:** B.Tech 3rd Year Student (CSET-371)

### Slide 2: Problem Statement (0:45 - 1:30)
- Urban highway corridors suffer from chronic recurrent congestion during peak hours and weather incidents.
- Traditional traffic control is reactive rather than predictive.
- IoT loop detectors produce high-volume continuous telemetry streams that overwhelm single-node relational databases.

### Slide 3: Motivation & Societal Impact (1:30 - 2:15)
- Billions of dollars lost annually in commuter delays and wasted fuel.
- Direct alignment with UN Sustainable Development Goals:
  - **SDG 9:** Resilient transportation infrastructure
  - **SDG 11:** Sustainable, livable urban communities
  - **SDG 13:** Mitigating carbon emissions from vehicle idle time

### Slide 4: Project Objectives (2:15 - 3:00)
- Ingest and process large-scale multi-sensor traffic telemetry using Apache Spark.
- Perform distributed cleaning and feature engineering in PySpark.
- Train, evaluate, and benchmark 5+ PySpark MLlib classification and regression models.
- Implement real-time streaming ingestion via Kafka and Spark Structured Streaming.
- Develop dynamic Dijkstra-based route optimization with congestion penalties.
- Deploy an executive Streamlit dashboard and Power BI business intelligence data marts.

### Slide 5: Existing Systems vs. Proposed Architecture (3:00 - 3:45)
- **Existing Systems:** Batch-only single-node tools (Pandas/Scikit-Learn), static GPS shortest-path routing leading into gridlock, fragmented BI reporting.
- **Proposed System:** Unified distributed platform coupling PySpark batch analytics, streaming micro-batches, machine learning inference, and dynamic rerouting.

### Slide 6: High-Level System Architecture (3:45 - 4:30)
- Architecture diagram walkthrough:
  - Data Sources: UCI Interstate & Corridor Network Telemetry
  - Ingestion: Spark CSV/Parquet Reader & Kafka Producer
  - Processing Engine: Apache Spark 4.2.0 Core, Catalyst Optimizer
  - Machine Learning: PySpark MLlib Pipeline (5 Classifiers + Regressors)
  - Routing Engine: Dynamic Dijkstra with Congestion Penalty ($\alpha$)
  - BI Tier: Streamlit Interactive App & Power BI Data Marts

### Slide 7: Authentic Dataset & Preprocessing (4:30 - 5:15)
- Dataset Source: UCI Metro Interstate Traffic Volume & Twin Cities Corridor Sensor Network.
- Features: Timestamps, volumes, speeds, lane occupancy, rain, snow, temperatures, road coordinates.
- PySpark Preprocessing: Deduplication, null imputation, timestamp casting, physical outlier filtering.

### Slide 8: Feature Engineering & Congestion Formulation (5:15 - 6:00)
- Temporal Features: Hour, day of week, morning peak (7–9 AM), evening peak (4–7 PM), rush hour flags.
- Traffic Ratios: Speed deficit ratio ($S / S_{\text{limit}}$), Volume-to-Capacity ratio ($V / C$).
- Congestion Classes: Formulated into 4 discrete levels (LOW, MEDIUM, HIGH, SEVERE).

### Slide 9: PySpark MLlib Classification Pipeline (6:00 - 7:00)
- Model Architectures Evaluated:
  1. Multinomial Logistic Regression
  2. Decision Tree Classifier
  3. Random Forest Classifier
  4. Gradient-Boosted Trees (OneVsRest wrapper for multiclass)
  5. Naive Bayes (Gaussian continuous features)
- Feature Pipeline: StringIndexer -> VectorAssembler -> StandardScaler -> Estimator.

### Slide 10: Experimental Results & Model Benchmark (7:00 - 8:00)
- Real Execution Metrics (80/20 train/test split on holdout data):
  - **GBTClassifier:** Accuracy: 98.83% | F1-Score: 0.9881 (Top Performer)
  - **Random Forest:** Accuracy: 98.71% | F1-Score: 0.9868
  - **Decision Tree:** Accuracy: 98.25% | F1-Score: 0.9824
  - **Logistic Regression:** Accuracy: 97.86% | F1-Score: 0.9782
  - **Naive Bayes:** Accuracy: 87.06% | F1-Score: 0.9024
- Continuous Speed Regressors: Linear Regression ($R^2 = 0.999$), GBT Regressor ($R^2 = 0.994$, RMSE: 0.56 km/h).

### Slide 11: Confusion Matrix & Error Analysis (8:00 - 8:45)
- Confusion Matrix display for the best model.
- High diagonal concentration with minimal false negatives for severe congestion.
- Discussion on why ensemble boosting minimizes residual bias on transition states.

### Slide 12: Real-Time Ingestion (Kafka + Spark Streaming) (8:45 - 9:30)
- Kafka event producer publishing JSON telemetry at 1–2 Hz.
- Spark Structured Streaming parsing JSON schema, extracting live features, and performing real-time inference.
- Dual-mode architecture: seamlessly supports local streaming simulation when external Kafka broker is offline.

### Slide 13: Intelligent Dijkstra Route Optimization (9:30 - 10:30)
- Graph formulation: Nodes = Intersections, Edges = Road Segments.
- Dynamic cost function:
  $$\text{Cost} = \frac{\text{Distance}}{\text{Speed}} \times 60 \times (1 + \alpha \times \text{CongestionFactor})$$
- Contrast: Static distance-based path vs. Dynamic congestion-avoidance path.
- Travel time savings and automatic secondary alternative corridor routing.

### Slide 14: Streamlit Business Intelligence Dashboard (10:30 - 11:15)
- 8 Modular Interactive Tabs:
  - Executive Overview & KPIs
  - Exploratory Traffic Analytics
  - Congestion Prediction Lab (Custom User Inputs)
  - Model Performance Benchmark
  - Intelligent Route Optimization (Interactive Plotly Map)
  - Real-Time Streaming Monitor
  - Decision Support Advisory
  - Academic & SDG Alignment

### Slide 15: Microsoft Power BI Integration (11:15 - 12:00)
- 6 Curated Data Marts in `powerbi/`: `traffic_kpis.csv`, `traffic_trends.csv`, `congestion_analysis.csv`, etc.
- 5-Page Power BI layout design: Executive Overview, Congestion Analytics, Model Performance, Network Delays, Real-Time Alerts.
- Custom DAX measures for real-time monitoring and reporting.

### Slide 16: Business Intelligence & Decision Support (12:00 - 12:45)
- Practical, calculated operational policies:
  - Dynamic signal timing extension (+18s green phase during peak volumes).
  - Variable speed limit (VSL) alerts during rain and snow.
  - Early rerouting advisories when $V/C > 0.85$ before mainline breakdown occurs.

### Slide 17: Scalability & Big Data Principles (12:45 - 13:30)
- Why Apache Spark is mandatory:
  - Distributed memory management and cluster scaling.
  - Lazy evaluation and Catalyst optimizer DAG execution.
  - Absence of full driver collections (`.collect()`) preserving memory efficiency.
  - Parquet columnar storage and partition pruning.

### Slide 18: UN Sustainable Development Goals (SDG) (13:30 - 14:00)
- Direct quantification of project alignment:
  - SDG 9: Infrastructure modernization with distributed computing.
  - SDG 11: Urban transit delay reduction.
  - SDG 13: Vehicle idle time reduction mitigating carbon emissions.

### Slide 19: Live Demonstration Walkthrough (14:00 - 14:45)
- Step 1: Show processed data and model metrics generated by PySpark.
- Step 2: Demonstrate interactive Route Optimization with dynamic traffic penalty $\alpha$.
- Step 3: Trigger real-time sensor events and observe live streaming updates in Streamlit.

### Slide 20: Conclusion & Future Scope (14:45 - 15:00)
- Summary: Delivered fully working, modular, verified end-to-end Big Data & BI platform.
- Future Work: Integration with GraphFrames for distributed graph algorithms, deep learning LSTM time-series forecasting, and connected vehicle (V2X) communication.
- **Open for Q&A.**
