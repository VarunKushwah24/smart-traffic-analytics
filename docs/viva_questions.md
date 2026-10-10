# 50+ High-Yield Viva Voce Questions & Answers

**Course:** CSET-371 Big Data Analytics and Business Intelligence  
**Project:** Smart Traffic Congestion Prediction and Intelligent Route Analytics Using Apache Spark

---

### Part 1: Apache Spark & PySpark Fundamentals

#### Q1. What is Apache Spark, and why is it preferred over Hadoop MapReduce?
**Ans:** Apache Spark is an open-source, distributed general-purpose cluster-computing framework. It is up to 100 times faster than Hadoop MapReduce because it processes data in-memory (RAM) rather than writing intermediate results to physical disks after every map/reduce step.

#### Q2. What is an RDD (Resilient Distributed Dataset)?
**Ans:** An RDD is the foundational data abstraction of Apache Spark. It represents an immutable, fault-tolerant, partitioned collection of records that can be processed in parallel across worker nodes.

#### Q3. What is the difference between an RDD and a Spark DataFrame?
**Ans:** While RDDs provide low-level control without schema awareness, DataFrames are organized into named columns (similar to relational database tables) and benefit from Spark's **Catalyst Query Optimizer** and **Tungsten execution engine**, providing vastly superior execution speed and memory efficiency.

#### Q4. What is Lazy Evaluation in Apache Spark?
**Ans:** Spark does not execute transformations (like `.filter()`, `.select()`, `.withColumn()`) immediately when defined. Instead, it builds an execution plan represented as a Directed Acyclic Graph (DAG). Execution is only triggered when an **action** (like `.count()`, `.collect()`, `.show()`, or writing to disk) is invoked. This allows the Catalyst engine to optimize the entire plan.

#### Q5. What is the difference between Spark Transformations and Actions?
**Ans:** 
- **Transformations** produce a new DataFrame from an existing one lazily (e.g., `filter`, `select`, `groupBy`, `join`).
- **Actions** trigger computation and return a value or write data to storage (e.g., `count`, `first`, `collect`, `write.parquet`).

#### Q6. What are Narrow vs. Wide Transformations?
**Ans:** 
- **Narrow Transformations:** Each input partition contributes to at most one output partition without data shuffling across the network (e.g., `map`, `filter`).
- **Wide Transformations:** Multiple child partitions depend on data from multiple parent partitions, requiring data to be shuffled across nodes (e.g., `groupByKey`, `distinct`, `join`).

#### Q7. What is Partitioning in Spark and why does it matter?
**Ans:** Partitioning is the division of a dataset into smaller chunks stored and processed across cluster nodes. Proper partitioning ensures even workload distribution and prevents data skew where one worker becomes a bottleneck.

#### Q8. When should you use caching (`df.cache()` / `df.persist()`)?
**Ans:** Caching stores a DataFrame in memory across worker nodes. It should only be used when an intermediate DataFrame is going to be accessed multiple times in iterative algorithms or downstream queries. Caching everything wastes cluster memory.

#### Q9. Why should developers avoid using `.collect()` on large datasets?
**Ans:** `.collect()` pulls all distributed partitions from all worker nodes into the driver node's single-machine RAM. If the dataset exceeds driver memory, it causes a fatal `OutOfMemoryError` (OOM).

#### Q10. What is PySpark MLlib?
**Ans:** PySpark MLlib is Spark’s distributed machine learning library providing scalable implementations of common algorithms (classification, regression, clustering, collaborative filtering) and pipeline utilities (feature scaling, vector assembly, cross-validation).

---

### Part 2: Feature Engineering & Preprocessing

#### Q11. What is VectorAssembler in PySpark?
**Ans:** `VectorAssembler` is a feature transformer that combines multiple individual numeric or encoded columns into a single unified vector column required by MLlib machine learning estimators.

#### Q12. What is StringIndexer and OneHotEncoder?
**Ans:** `StringIndexer` maps string column categories into numerical category indices ($0, 1, 2, \dots$). `OneHotEncoder` maps categorical indices to binary sparse vectors to avoid imposing false ordinal relationships on nominal categories.

#### Q13. Why did we scale features using `StandardScaler`?
**Ans:** Algorithms sensitive to magnitude (such as Logistic Regression and distance-based estimators) require features to have zero mean and unit variance so high-magnitude features (like volume = 4000) don't dominate low-magnitude features (like temperature = 15).

#### Q14. What is Data Leakage and how did you prevent it?
**Ans:** Data leakage occurs when information from outside the training dataset (such as target labels or future timestamps) is used to create features. We prevented it by strictly excluding the target label from the `VectorAssembler` input columns and calculating transformations purely from observable historical features.

#### Q15. How did you handle outliers in traffic speed and weather?
**Ans:** We filtered sensor anomalies such as speeds $> 160\text{ km/h}$ or $\le 5\text{ km/h}$, clipped rainfall readings $> 100\text{ mm/h}$, and corrected temperature Kelvin readings ($< 200\text{ K}$) before model training.

#### Q16. How is traffic congestion defined in your project?
**Ans:** Congestion is classified into 4 levels based on Volume-to-Capacity ratio ($V/C$) and speed deficit:
- **LOW:** Speed $\ge 80\%$ limit, $V/C < 0.60$
- **MEDIUM:** Speed $60\%\text{--}80\%$, $V/C \in [0.60, 0.85)$
- **HIGH:** Speed $35\%\text{--}60\%$, $V/C \in [0.85, 1.05)$
- **SEVERE:** Speed $< 35\%$ limit or $V/C \ge 1.05$ (Gridlock)

---

### Part 3: Machine Learning Models & Metrics

#### Q17. Which 5 classification models did you implement in PySpark?
**Ans:** 
1. Multinomial Logistic Regression
2. Decision Tree Classifier
3. Random Forest Classifier
4. Gradient-Boosted Trees (wrapped in OneVsRest)
5. Naive Bayes (Gaussian model)

#### Q18. Why does GBTClassifier require OneVsRest in PySpark for multiclass?
**Ans:** PySpark MLlib's native `GBTClassifier` only supports binary classification ($k = 2$). For 4 congestion classes, wrapping it in `OneVsRest` trains 4 separate binary classifiers ($1\text{ vs Rest}$) in an ensemble.

#### Q19. What is the difference between Bagging (Random Forest) and Boosting (GBT)?
**Ans:** 
- **Random Forest (Bagging):** Builds multiple independent decision trees in parallel on bootstrap subsets and averages their predictions to reduce variance.
- **Gradient-Boosted Trees (Boosting):** Builds trees sequentially, where each new tree specifically learns to correct the residual errors made by prior trees to reduce bias.

#### Q20. What is a Confusion Matrix?
**Ans:** A matrix layout that visualizes the performance of an algorithm: rows represent the actual target classes and columns represent the predicted classes. It reveals exact True Positives, False Positives, False Negatives, and True Negatives.

#### Q21. What is the difference between Precision and Recall?
**Ans:** 
- **Precision:** Of all instances predicted as congested, how many were actually congested? $\frac{TP}{TP + FP}$.
- **Recall:** Of all actual congested instances, how many did the model identify? $\frac{TP}{TP + FN}$.

#### Q22. What is the F1-Score and why is it preferred over simple Accuracy?
**Ans:** The F1-score is the harmonic mean of Precision and Recall:
$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
It is preferred when class distributions are imbalanced because simple accuracy can be misleading if a majority class dominates.

#### Q23. Which model performed best and why?
**Ans:** Gradient-Boosted Trees (GBTClassifier) and Random Forest achieved the highest F1-scores ($> 0.98$). Tree ensembles effectively capture non-linear traffic breakdown thresholds and complex multi-feature interactions between volume, rush hour, and weather.

#### Q24. What regression models did you evaluate for speed prediction?
**Ans:** Linear Regression, Random Forest Regressor, and GBT Regressor. GBT and Random Forest achieved $R^2 > 0.96$, demonstrating high accuracy in predicting continuous speed.

---

### Part 4: Real-Time Streaming & Apache Kafka

#### Q25. What is Apache Kafka and what role does it play in this project?
**Ans:** Apache Kafka is a distributed, high-throughput event streaming platform. In our system, it acts as a centralized real-time ingestion buffer for continuous telemetry messages generated by IoT road sensors.

#### Q26. What is a Kafka Topic, Producer, and Consumer?
**Ans:** 
- **Topic:** A named category/feed to which records are published.
- **Producer:** An application that publishes event messages to Kafka topics.
- **Consumer:** An application that subscribes to topics and processes the stream.

#### Q27. What is Spark Structured Streaming?
**Ans:** It is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine. It treats live data streams as an unbounded table that is continuously appended to, processing micro-batches with low latency.

#### Q28. What is the purpose of checkpointing in Spark Streaming?
**Ans:** Checkpointing writes streaming metadata and processed offsets to fault-tolerant storage (HDFS or local disk) so the stream can recover with exactly-once guarantees if a worker fails.

#### Q29. How does the system handle environments where Kafka is not running?
**Ans:** We implemented a dual-mode producer and consumer: if a live Kafka broker is unavailable, it automatically activates **Local Streaming Simulation Mode**, streaming JSON events through a file directory source using Spark Structured Streaming.

---

### Part 5: Dijkstra's Intelligent Route Optimization

#### Q30. What is Dijkstra's Algorithm?
**Ans:** Dijkstra's algorithm is a greedy graph search algorithm that finds the shortest path between a source node and all other nodes in a graph with non-negative edge weights.

#### Q31. How are edges and weights defined in your road network graph?
**Ans:** 
- **Nodes:** Key transit junctions and highway interchanges with GPS coordinates.
- **Edges:** Directed road segments with distance and speed limits.
- **Weight:** Dynamic traffic cost:
  $$\text{Cost} = \frac{\text{Distance}}{\text{Speed}} \times 60 \times (1 + \alpha \times \text{CongestionMultiplier})$$

#### Q32. What is the congestion penalty factor $\alpha$?
**Ans:** $\alpha$ controls how aggressively the routing algorithm penalizes congestion. When $\alpha = 0$, routing is purely based on free-flow travel time. When $\alpha > 0$, heavily congested segments are penalized, dynamically guiding vehicles to alternative uncongested corridors.

#### Q33. How does the system calculate alternative routes?
**Ans:** It identifies the primary bottleneck road segment along the optimal path and temporarily excludes or penalizes it, finding the next least-cost alternative route to provide drivers with contingency options.

---

### Part 6: Business Intelligence & Power BI

#### Q34. What data marts were exported for Power BI?
**Ans:** Six clean data marts: `traffic_kpis.csv`, `traffic_trends.csv`, `congestion_analysis.csv`, `model_metrics.csv`, `route_analysis.csv`, and `predictions.csv`.

#### Q35. What is DAX in Power BI?
**Ans:** DAX (Data Analysis Expressions) is a formula expression language used in Power BI, Analysis Services, and Power Pivot in Excel to define custom calculations, calculated columns, and dynamic measures.

#### Q36. What decision-support recommendations does the BI dashboard generate?
**Ans:** 
1. Dynamic green-light phase extensions during detected peak hours.
2. Variable speed limit advisories during adverse weather events.
3. Automatic corridor rerouting when segment Volume-to-Capacity ratio exceeds $0.85$.

---

### Part 7: Sustainable Development Goals (SDG)

#### Q37. Which UN SDGs does this project address?
**Ans:** 
- **SDG 9:** Industry, Innovation, and Infrastructure
- **SDG 11:** Sustainable Cities and Communities
- **SDG 13:** Climate Action

#### Q38. How does smart traffic analytics contribute to SDG 13 (Climate Action)?
**Ans:** Stop-and-go traffic drastically increases fuel consumption and vehicle idle greenhouse gas emissions. By predicting gridlock and dynamically rerouting traffic, the system minimizes idle times and reduces carbon emissions.
