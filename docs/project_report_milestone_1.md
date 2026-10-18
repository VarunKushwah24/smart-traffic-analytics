# CSET-371: BIG DATA ANALYTICS AND BUSINESS INTELLIGENCE
## MILESTONE 1 PROJECT REPORT (CHAPTERS 1 & 2)

---

**PROJECT TITLE:**  
# Smart Traffic Congestion Prediction and Intelligent Route Analytics Using Apache Spark

**ALTERNATIVE PROFESSIONAL TITLE:**  
### Real-Time Smart Traffic Congestion Prediction and Intelligent Route Optimization Using PySpark, Kafka and Machine Learning

---

| Academic Parameter | Details |
| :--- | :--- |
| **Course Code & Name:** | CSET-371 Big Data Analytics and Business Intelligence |
| **Degree Program:** | Bachelor of Technology (B.Tech) in Computer Science & Engineering |
| **Academic Year & Semester:**| 3rd Year / 5th Semester |
| **Candidate Name:** | Varun Kushwah |
| **Evaluation Milestone:** | Milestone 1 (Comprehensive Project Report) |
| **Target Document Length:** | Minimum 20–25 Pages (Chapters 1 and 2 Complete) |
| **Plagiarism Compliance:** | Strict Zero-Plagiarism / Turnitin Similarity Index < 10% |

---

\newpage

# TABLE OF CONTENTS

* **CHAPTER 1: PROBLEM DOMAIN IDENTIFICATION AND ANALYSIS**
  * 1.1 Background of the Study
  * 1.2 Introduction to the Problem Domain
  * 1.3 Literature Review
  * 1.4 Research Gap and Literature Gaps
  * 1.5 Review of Existing Solutions
  * 1.6 Limitations of Existing Systems
  * 1.7 Problem Statement
  * 1.8 Proposed Solution Overview
  * 1.9 Objectives of the Project
  * 1.10 Scope of the Project
  * 1.11 Industrial Applications and Use Cases

* **CHAPTER 2: PROJECT DESIGN AND METHODOLOGY**
  * 2.1 System Overview
  * 2.2 Proposed System Architecture
  * 2.3 Architecture Components and Their Functions
  * 2.4 Proposed Methodology
  * 2.5 Methodology Workflow Use-case / DFD Flow Diagram
  * 2.6 Algorithms and Techniques Used
  * 2.7 Dataset Description
  * 2.8 Data Collection and Data Preprocessing
  * 2.9 Tools and Technologies Used
  * 2.10 Experimental Setup and Configuration
  * 2.11 Evaluation Metrics

---

\newpage

# CHAPTER 1: PROBLEM DOMAIN IDENTIFICATION AND ANALYSIS

---

## 1.1 Background of the Study

Rapid worldwide industrialization, urban migration, and population expansion have led to exponential vehicular density across metropolitan transit infrastructures. According to transportation economics telemetry, severe vehicular congestion accounts for hundreds of billions of dollars in lost productivity, millions of metric tons of avoidable greenhouse gas emissions, and severe public health degradation every year. Traditional urban arterial roadways and multi-lane expressways were fundamentally engineered during eras of predictable, stationary commuter volumes. Today, sudden spikes in population, coupled with volatile ridesharing and logistics traffic, subject these physical networks to severe demand-capacity imbalances.

Historically, civil transportation departments attempted to mitigate congestion through capital-intensive infrastructure expansions—primarily building additional highway lanes, bypasses, and overpasses. However, empirical transportation economics repeatedly demonstrates the principle of *Induced Demand* (formalized under the Downs-Thomson Paradox and Lewis-Mogridge Position): expanding physical road supply almost invariably attracts supplementary vehicular traffic, restoring saturation and chronic bottlenecks within short timeframes. Consequently, modern transportation engineering has pivoted from physical capacity expansion toward intelligent operational optimization.

With the ubiquity of Internet of Things (IoT) sensors, inductive loop detectors, automated number plate recognition (ANPR) cameras, and GPS-connected vehicle telemetry, metropolitan roadways have transformed into rich data-generating environments. Every minute, millions of telemetry records capturing instantaneous speeds, vehicular counts, lane occupancy rates, and localized micro-climates are gathered across urban corridors. However, this torrent of high-velocity, high-volume data presents an immense engineering challenge: single-machine data processing tools (such as standard relational databases, Pandas, or Scikit-learn) collapse under the storage and computational demands of continuous streaming telemetry.

To address this challenge, modern intelligent transportation systems must be built upon distributed computing frameworks capable of horizontal scaling. Apache Spark represents the state of the art in distributed data processing, offering in-memory processing capabilities, resilient distributed computation, and unified support for both historical batch analytics and continuous streaming pipelines. Leveraging Apache Spark within urban transportation systems allows civil authorities and commercial fleet dispatchers to process telemetry at petabyte scale, detect spatiotemporal anomalies, forecast congestion bottlenecks in advance, and balance network-wide traffic equilibrium dynamically.

---

\newpage

## 1.2 Introduction to the Problem Domain

The problem domain addressed by this study sits at the convergence of four critical technical disciplines: Big Data Engineering, Intelligent Transportation Systems (ITS), Machine Learning Classification & Regression, and Algorithmic Graph Optimization. 

At its foundational level, urban vehicular traffic represents a dynamic, stochastic, and highly non-linear system. Vehicular throughput along any given arterial roadway is governed by fundamental traffic flow theory, mathematically expressed through the hydrodynamic relationship:
$$q = k \times v$$
where $q$ represents traffic flow (vehicles per hour), $k$ represents vehicular density (vehicles per kilometer), and $v$ represents mean space speed (kilometers per hour). As traffic volume increases and approaches physical road capacity, small perturbations—such as abrupt lane changes, minor rear-end collisions, adverse weather events, or bottleneck merges—trigger kinematic shockwaves that propagate backwards through the traffic stream. This phenomenon, known as the *Phantom Traffic Jam*, can collapse highway speeds from 100 km/h to under 20 km/h in mere minutes without any physical roadway obstruction.

The primary engineering challenge within this domain is the transition from **reactive** traffic operations to **predictive and proactive** traffic management:
1. **Reactive Traffic Management (Conventional Paradigm):** Traffic management centers observe an existing gridlock on CCTV or sensor feeds after it has already fully formed. Emergency operators attempt to dispatch personnel or update electronic message signs, but by this stage, upstream corridors are already saturated, resulting in prolonged delays.
2. **Predictive Traffic Management (Proposed Paradigm):** Advanced Big Data pipelines ingest continuous sensor streams, engineer predictive features (such as volume-to-capacity ratios, rate of speed change, and weather sensitivity), and predict impending congestion states 30 to 60 minutes before physical breakdown occurs.

Furthermore, predictive traffic intelligence cannot exist in isolation. Forecasting that a highway corridor will experience severe congestion is of limited utility unless that prediction is integrated into a dynamic routing engine. Standard GPS routing software directs thousands of vehicles along the identical physically shortest path, inadvertently overloading secondary corridors and precipitating the *Braess Paradox*. This project addresses this domain by uniting distributed Big Data ingestion (Apache Spark), predictive machine learning (Spark MLlib), dynamic graph optimization (Congestion-Aware Dijkstra), and real-time streaming (Apache Kafka and Spark Structured Streaming) into a cohesive, production-grade architecture.

---

\newpage

## 1.3 Literature Review

The academic and industrial literature surrounding traffic congestion analysis and vehicle routing has evolved through three distinct technological eras over the past four decades:

### 1. Classical Statistical and Time-Series Formulations
Early research during the 1980s and 1990s approached traffic forecasting primarily through classical linear statistical modeling. Box and Jenkins' Auto-Regressive Integrated Moving Average (ARIMA) models, along with Seasonal ARIMA (SARIMA), were widely adopted to predict traffic flow based on historical temporal patterns. While mathematically rigorous and effective for modeling regular diurnal cycles under clear weather conditions, statistical time-series methods exhibit severe vulnerabilities when confronted with non-linear perturbations. When sudden adverse weather events occur (such as sudden snowfall or torrential rain) or when upstream incidents trigger rapid shockwaves, linear assumptions collapse, resulting in significant forecast inaccuracies.

### 2. Standalone Machine Learning and Centralized Architectures
With the advent of modern machine learning in the 2000s and 2010s, researchers pivoted toward non-linear predictive algorithms. Significant literature explored Support Vector Machines (SVM), Multi-Layer Perceptrons (MLP), Random Forests, and Gradient Boosting algorithms implemented via centralized Python libraries such as Scikit-learn. These models demonstrated superior non-linear mapping capabilities compared to statistical approaches, capturing complex interactions between lane occupancy, ambient temperature, and vehicular volume. 

However, published literature in this era reveals a critical infrastructural limitation: scalability. As urban sensor networks grew from dozens of experimental stations to thousands of continuous inductive loops emitting high-frequency telemetry, centralized memory architectures encountered severe Out-Of-Memory (OOM) failures. Traditional single-node workflows require serializing data through RAM, making it impossible to perform multi-year model training and sub-second stream inference within a unified architecture.

### 3. Distributed Big Data and Streaming Frameworks
In recent years, researchers have turned to distributed architectures—specifically Apache Hadoop and Apache Spark—to address transportation data volume. Studies demonstrated that Spark’s Resilient Distributed Datasets (RDDs) and DataFrames substantially outperform MapReduce on iterative machine learning tasks due to in-memory caching and Directed Acyclic Graph (DAG) optimization. Concurrently, Apache Kafka emerged as the standard distributed messaging backbone for ingesting high-throughput IoT sensor streams.

Despite these advancements, existing literature leaves a substantial gap: current implementations frequently decouple the analytical forecasting pipeline from the graph-theoretic routing engine. Machine learning models predict traffic density, but routing engines continue to execute standard shortest-path algorithms based on static road lengths. This project directly synthesizes these disparate literature streams by unifying distributed PySpark MLlib modeling with a dynamic, congestion-penalized Dijkstra graph routing engine.

---

\newpage

## 1.4 Research Gap and Literature Gaps

A systematic analysis of contemporary academic studies reveals four critical research gaps that motivate the design and architecture of this project:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        IDENTIFIED RESEARCH GAPS                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Disconnect Between Machine Learning Predictions & Dynamic Routing  │
│ 2. Scalability Bottlenecks in Single-Node ML Transportation Pipelines  │
│ 3. Static vs. Dynamic Edge Cost Functions in Graph Optimization        │
│ 4. Decoupled Architectures for Batch Training and Stream Ingestion     │
└────────────────────────────────────────────────────────────────────────┘
```

### Gap 1: Disconnect Between Machine Learning Predictions and Dynamic Routing
The predominant majority of published transportation literature focuses exclusively on either classification/regression accuracy OR graph shortest-path optimization. Rare are the studies that bridge this divide into an actionable, closed-loop system. When predictive models operate in isolation, their forecasts do not inform downstream navigation. Conversely, navigation engines operating without predictive capabilities route drivers into corridors that are free-flowing *now* but will be completely gridlocked by the time the vehicle arrives.

### Gap 2: Scalability Bottlenecks in Single-Node Transportation Pipelines
A significant body of academic research continues to implement machine learning pipelines using Scikit-learn, Pandas, and localized NumPy matrices. While sufficient for small academic demonstration datasets (under 10,000 rows), these architectures fail when deployed against real-world metropolitan networks where millions of vehicle detection events are logged daily. There is an acute need for reproducible, production-grade PySpark MLlib pipelines that execute distributed feature transformations (such as `VectorAssembler` and `StandardScaler`) across distributed partitions without single-node memory constraints.

### Gap 3: Static Edge Cost Functions in Graph Theory
Classical graph algorithms (such as standard Dijkstra, Bellman-Ford, or A*) evaluate edge weights purely as a function of physical distance:
$$\text{Cost}(u, v) = \text{Distance}(u, v)$$
In real urban environments, physical distance is an inadequate proxy for travel impedance. A 5-kilometer highway segment undergoing severe congestion often incurs four times the travel delay of an 8-kilometer uncongested arterial bypass. Literature lacks an empirical, parameterized penalty function that systematically ties multi-class ML congestion predictions ($\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{SEVERE}$) directly into dynamic edge cost formulations.

### Gap 4: Decoupled Architectures for Batch Training and Stream Ingestion
Conventional systems typically maintain two separate, non-communicating pipelines: a batch processing script (running offline nightly) and a streaming ingestion service (running lightweight rules in memory). This dual-codebase paradigm results in feature drift, inconsistent preprocessing schemas, and high maintenance overhead. This project bridges this gap by utilizing Apache Spark’s unified execution engine to guarantee that feature engineering logic remains identical across historical batch training and real-time Kafka streaming inference.

---

\newpage

## 1.5 Review of Existing Solutions

To rigorously benchmark the technical contributions of this project, existing commercial, academic, and municipal traffic management solutions are evaluated below:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    COMPARATIVE REVIEW OF EXISTING SYSTEMS                    │
├───────────────────────┬──────────────────────────┬───────────────────────────┤
│ Solution Category     │ Key Strengths            │ Primary Vulnerabilities   │
├───────────────────────┼──────────────────────────┼───────────────────────────┤
│ Commercial GPS        │ Massive crowd-sourced    │ Proprietary black-box;    │
│ Navigation Platforms  │ user base; polished UI;  │ causes Braess Paradox;    │
│ (Google Maps, Waze)   │ global road coverage.    │ no municipal integration. │
├───────────────────────┼──────────────────────────┼───────────────────────────┤
│ Municipal SCATS/SCOOT │ Highly reliable local    │ Prohibitively expensive;  │
│ Adaptive Signal Units │ loop hardware; direct    │ reactive loop detection;  │
│ (City Infrastructure) │ signal controller links. │ lacks predictive routing. │
├───────────────────────┼──────────────────────────┼───────────────────────────┤
│ Academic Standalone   │ High theoretical ML      │ Fails on large datasets;  │
│ Jupyter Workflows     │ accuracy on small static │ no streaming; no GUI;     │
│ (Pandas/Scikit-learn) │ datasets; easy to test.  │ single-node memory limit. │
├───────────────────────┼──────────────────────────┼───────────────────────────┤
│ Proposed SmartTraffic │ Scalable PySpark Big     │ Requires distributed JVM  │
│ Analytics Platform    │ Data engine; live Kafka; │ cluster configuration     │
│ (This Project)        │ dynamic Dijkstra routing │ for enterprise scale.     │
└───────────────────────┴──────────────────────────┴───────────────────────────┘
```

### 1. Commercial Navigation Applications (Google Maps, Waze, Apple Maps)
Commercial mobile navigation applications leverage crowd-sourced GPS telemetry from hundreds of millions of consumer smartphones. While effective for personal turn-by-turn navigation, they operate as proprietary "black boxes." Municipal traffic engineers have no programmatic visibility into their internal routing algorithms, preventing cities from executing coordinated traffic control policies. Furthermore, commercial algorithms optimize selfishly for individual travel times, frequently funneling high-speed highway traffic through narrow residential neighborhoods and overwhelming local secondary infrastructure.

### 2. Municipal Adaptive Signal Systems (SCATS, SCOOT, InSync)
Developed for city departments of transportation, systems such as the Sydney Coordinated Adaptive Traffic System (SCATS) and the Split Cycle Offset Optimization Technique (SCOOT) dynamically adjust traffic light cycle lengths based on inductive loops embedded in pavement. While effective at the intersection level, these systems are capital-intensive, require proprietary hardware controllers, and operate strictly **reactively**. They cannot predict network-wide corridor congestion hours in advance, nor do they possess interfaces to provide route guidance to individual vehicles.

### 3. Open-Source Academic Research Scripts
Numerous academic projects implement traffic forecasting using Scikit-learn or TensorFlow in standalone Jupyter Notebooks. While demonstrating high theoretical accuracy on static CSV slices, they lack production viability. They do not implement distributed data pipelines, cannot ingest live streaming messages from message brokers, offer no interactive decision-support interface for municipal stakeholders, and fail to provide graph-theoretic route optimization.

---

\newpage

## 1.6 Limitations of Existing Systems

The structural limitations of existing traffic analysis and routing solutions can be distilled into five foundational architectural deficiencies:

```
                     ┌───────────────────────────────────┐
                     │  LIMITATIONS OF EXISTING SYSTEMS  │
                     └─────────────────┬─────────────────┘
                                       │
        ┌──────────────┬───────────────┼───────────────┬──────────────┐
        ▼              ▼               ▼               ▼              ▼
  Single-Node     Reactive vs.    Selfish Route     Isolated       Black-Box
   Memory OOM      Predictive      Optimization     Batch &        Decisions
  Bottlenecks      Operations     (Braess Paradox)   Streaming     (No City DSS)
```

1. **Centralized Memory Constraints and Lack of Horizontal Scalability:**
   Conventional machine learning frameworks process datasets strictly within single-node random-access memory (RAM). When ingesting continuous sensor feeds spanning multi-year metropolitan archives, memory exhaustion occurs rapidly. These systems lack the partitioning, shuffle management, and distributed caching capabilities intrinsic to Apache Spark.

2. **Inherent Delay in Reactive Operational Workflows:**
   Existing transportation systems operate on a detect-and-react paradigm. By the time inductive loop sensors trigger an alert that corridor speeds have collapsed below 30 km/h, bumper-to-bumper queueing has already propagated across multiple kilometers. Dissipating an established highway bottleneck requires up to three times longer than preventing its formation through proactive diversion.

3. **Inducement of the Braess Paradox via Selfish Routing:**
   Standard navigation algorithms execute selfish routing—optimizing the route of a single vehicle without considering the aggregate impact on the network. When thousands of drivers receive identical rerouting suggestions simultaneously, secondary arterial routes quickly collapse under sudden volumetric surges, generating secondary bottlenecks worse than the initial highway delay.

4. **Architectural Incoherence Between Batch and Real-Time Systems:**
   Organizations attempting to combine historical analytics with live monitoring routinely deploy two distinct technology stacks: an offline batch stack (e.g., Python scripts or SQL databases) and a live streaming stack (e.g., Node.js or simple web sockets). This leads to duplicate feature code, synchronization drift, and inconsistent classification outputs between historical benchmarks and real-time feeds.

5. **Lack of Integrated Municipal Decision Support Systems (DSS):**
   Commercial navigation platforms are consumer-facing and provide zero operational utility to municipal traffic authorities. They do not calculate Volume-to-Capacity (V/C) ratios, cannot generate lane-occupancy advisories, do not suggest variable speed limit reductions during adverse snow or rain events, and provide no standardized data marts compatible with business intelligence tools like Microsoft Power BI.

---

\newpage

## 1.7 Problem Statement

The formal problem statement addressed by this engineering project is articulated as follows:

> **"Contemporary municipal transportation and logistics networks lack a unified, horizontally scalable Big Data analytical framework capable of ingesting high-throughput heterogeneous sensor telemetry, executing distributed feature engineering, predicting multi-tier traffic congestion levels under adverse meteorological conditions, and dynamically computing optimal detour routing before arterial bottlenecks collapse into severe gridlock."**

### Technical Breakdown of the Problem Statement
To resolve this overarching problem statement, the system must overcome three distinct engineering and algorithmic sub-problems:

1. **The Big Data Ingestion & Transformation Challenge:**
   Processing high-volume, multi-year vehicle volume and speed telemetry alongside real-time streaming feeds without encountering single-node memory saturation, while enforcing strict schema integrity and filtering physical anomalies.
2. **The Multi-Class Machine Learning Prediction Challenge:**
   Designing, training, and benchmarking multiple distributed classifiers in PySpark MLlib that can accurately categorize road segments into four distinct capacity-based congestion tiers (`LOW`, `MEDIUM`, `HIGH`, `SEVERE`) while identifying non-linear speed degradation induced by adverse weather.
3. **The Dynamic Graph Route Optimization Challenge:**
   Constructing a directed graph of metropolitan highway interchanges and formulating a dynamic Dijkstra shortest-path algorithm whose edge cost function penalizes predicted congestion via an adjustable sensitivity factor $\alpha$, thereby generating optimal and alternative routes that actively circumvent bottlenecks.

---

\newpage

## 1.8 Proposed Solution Overview

To address the limitations of existing systems and fulfill the problem statement, this project designs, implements, benchmarks, and deploys an end-to-end Big Data Analytics and Intelligent Route Optimization Platform. The solution integrates distributed batch analytics, real-time event streaming, machine learning classification, graph-theoretic route optimization, and executive decision-support visualization into a cohesive, production-grade architecture.

```
       HISTORICAL BATCH TELEMETRY             REAL-TIME IOT SENSOR STREAM
          (48,204 UCI Records)                 (Simulated Kafka Feeds)
                   │                                      │
                   ▼                                      ▼
       ┌────────────────────────┐             ┌────────────────────────┐
       │ Apache Spark Batch ETL │             │ Spark Structured       │
       │ • StructType Schemas   │             │   Streaming Engine     │
       │ • Null Imputation      │             │ • Micro-Batch Scoring  │
       │ • Outlier Filtering    │             │ • Real-Time Feature    │
       │ • Feature Engineering  │             │   Extraction           │
       └───────────┬────────────┘             └───────────┬────────────┘
                   │                                      │
                   ▼                                      ▼
       ┌────────────────────────┐             ┌────────────────────────┐
       │ PySpark MLlib Pipeline │             │ Live Stream Sink       │
       │ • GBT, RF, DT, LR, NB  │             │ • Continuous CSV /     │
       │ • Continuous Regressors│             │   Console Output       │
       └───────────┬────────────┘             └───────────┬────────────┘
                   │                                      │
                   ▼                                      ▼
       ┌───────────────────────────────────────────────────────────────┐
       │            CONGESTION-AWARE DIJKSTRA ROUTING CORE             │
       │ • Twin Cities Highway Topology (10 Nodes, 24 Segments)        │
       │ • Cost = (Distance / Speed * 60) * (1 + alpha * Congestion)  │
       │ • Generates Optimal Route & Alternative Bypass Corridors      │
       └───────────────────────────────┬───────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │              EXECUTIVE BUSINESS INTELLIGENCE LAYER            │
       │ • Modern Dark-Themed Streamlit Web Dashboard (8 Modules)      │
       │ • OpenStreetMap Spatial Network Route Rendering               │
       │ • Decision Support System (DSS) Operational Policy Cards      │
       │ • Star-Schema Power BI Data Marts (powerbi/*.csv)             │
       └───────────────────────────────────────────────────────────────┘
```

### Core Innovations of the Proposed Solution
* **Unified Apache Spark Core:** PySpark is deployed as the foundational execution engine for both batch preprocessing and streaming inference, guaranteeing complete consistency in schema definitions, categorical encodings, and scaling vectors.
* **Empirical Multi-Class Congestion Thresholding:** Rather than assigning arbitrary congestion categories, traffic states are classified into `LOW`, `MEDIUM`, `HIGH`, and `SEVERE` based on rigorous transportation engineering formulas combining Speed Ratio ($v / v_{\text{free}}$) and Volume-to-Capacity Ratio ($V/C$).
* **Congestion-Aware Dijkstra Optimization:** The route optimization module modifies standard edge evaluation by integrating an adjustable congestion multiplier $\alpha$. When high congestion is predicted on a primary highway, edge impedance increases proportionally, allowing the priority queue to automatically identify clear detour corridors.
* **Production-Grade Interactive Web Dashboard:** Built using Streamlit and Plotly 7.x, the user interface features an eye-warming dark-gradient theme, glowing KPI cards, live gauges, dual-axis temporal charts, radar comparison plots, and interactive OpenStreetMap navigation.

---

\newpage

## 1.9 Objectives of the Project

The overarching goal of this project is to architect, implement, benchmark, and demonstrate a complete, functional Big Data analytics and decision-support system. This goal is operationalized through seven specific, measurable technical objectives:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE PROJECT OBJECTIVES                         │
├────────────────────────────────────────────────────────────────────────┤
│ Objective 1: Large-Scale Distributed Ingestion & Schema Enforcement    │
│ Objective 2: Automated Data Cleaning & Outlier Management              │
│ Objective 3: Domain-Driven Feature Engineering (V/C & Speed Ratios)    │
│ Objective 4: PySpark MLlib Multi-Model Benchmark (5 Classifiers)       │
│ Objective 5: Congestion-Penalized Dynamic Dijkstra Routing Engine      │
│ Objective 6: Real-Time Kafka & Spark Structured Streaming Integration  │
│ Objective 7: Executive BI Dashboard & Power BI Decision Support Marts  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Objective 1 — Distributed Data Ingestion:**
   Ingest both high-volume historical traffic logs (48,204 records from the UCI Interstate Traffic Volume dataset) and multi-corridor network topologies (8,064 records spanning 24 highway segments) into Apache Spark DataFrames utilizing explicit `StructType` schemas to avoid runtime inference overhead.

2. **Objective 2 — Preprocessing & Physical Anomaly Filtration:**
   Implement automated PySpark cleaning pipelines to eliminate duplicate records, impute missing numerical and categorical features using median and mode strategies, and filter sensor anomalies (e.g., unrealistic temperatures and speeds) using interquartile range (IQR) boundaries.

3. **Objective 3 — Feature Engineering & Thresholding:**
   Engineer temporal, environmental, and kinematic traffic indicators—including rush-hour flags, weekend indicators, Speed Ratios, and Volume-to-Capacity (V/C) ratios—and establish an objective 4-tier congestion classification system (`LOW`, `MEDIUM`, `HIGH`, `SEVERE`).

4. **Objective 4 — Machine Learning Modeling with Spark MLlib:**
   Construct, train, evaluate, and benchmark at least five distinct PySpark MLlib classifiers (Gradient-Boosted Trees, Random Forest, Decision Tree, Logistic Regression, Naive Bayes) alongside continuous speed regressors, achieving classification accuracy exceeding 95% on holdout test partitions.

5. **Objective 5 — Dynamic Graph Route Optimization:**
   Model the Minneapolis–St. Paul metropolitan interstate network as a directed graph of 10 junction nodes and 24 road segments, and develop a modified Dijkstra algorithm that applies dynamic congestion penalty multipliers ($\alpha$) to calculate travel times, delays, and alternative corridors.

6. **Objective 6 — Real-Time Streaming Pipeline:**
   Develop a modular IoT event producer simulating Kafka sensor feeds and integrate Spark Structured Streaming to ingest JSON micro-batches, execute real-time feature extraction, apply the trained MLlib model for live inference, and write predictions to persistent sinks.

7. **Objective 7 — Business Intelligence & Decision Support:**
   Deliver a multi-module executive web dashboard using Streamlit featuring interactive Plotly visualizations, OpenStreetMap route maps, real-time prediction gauges, and exported star-schema data marts for Microsoft Power BI integration.

---

\newpage

## 1.10 Scope of the Project

To maintain rigorous technical depth while ensuring feasibility on standard computing environments, the project establishes well-defined boundaries:

### In-Scope Boundaries
* **Data Engineering:** Ingestion, cleaning, transformation, and partitioning of highway corridor telemetry within local Apache Spark (utilizing `local[*]` master mode with optimized JVM heap and winutils bindings).
* **Machine Learning:** Training, cross-evaluation, and hyperparameter tuning of 5 distributed classifiers and 3 regressors using PySpark MLlib pipelines (`VectorAssembler`, `StandardScaler`, `StringIndexer`, `OneVsRest`).
* **Graph Modeling:** Topological modeling of a 10-node metropolitan highway interchange network with authentic GPS coordinates, computing optimal and alternative paths with adjustable penalty factor $\alpha \in [0.0, 1.5]$.
* **Streaming Architecture:** Simulation of Kafka sensor streams via modular JSON directory sources, micro-batch ingestion via Spark Structured Streaming, and live scoring against trained pipeline models.
* **Visualization & BI:** Construction of an 8-module Streamlit web application with Plotly dark-themed analytics, interactive OpenStreetMap tiles, and generation of 6 Power BI star-schema CSV marts.
* **Academic & Environmental Alignment:** Quantitative mapping of project outcomes to UN Sustainable Development Goals (SDG 9: Innovation, SDG 11: Sustainable Cities, SDG 13: Climate Action).

### Out-of-Scope Boundaries
* **Microscopic Vehicular Modeling:** Modeling individual vehicle physics, lane-change decisions, or microscopic car-following behavior (such as SUMO or VISSIM simulations).
* **Physical Hardware Prototyping:** Physical soldering or roadside installation of microcontroller hardware (e.g., Raspberry Pi or Arduino loop sensors).
* **Direct Municipal Hardware Actuation:** Direct electrical interfacing with physical traffic light controllers or variable message signs on public roads.
* **Global Cloud Infrastructure Dependency:** Requiring paid cloud subscriptions (AWS EMR, Databricks, Azure Synapse) for core evaluation; the entire pipeline is architected to run reproducibly on a standard student laptop.

---

\newpage

## 1.11 Industrial Applications and Use Cases

The architectural principles and algorithms implemented in this project directly translate into four high-impact industrial and municipal applications:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      INDUSTRIAL APPLICATION DOMAINS                    │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 1. Municipal Traffic Operations  │ Real-time signal timing adjustment, │
│    Centers (TOC / TMC)           │ proactive ramp metering, VSL signs. │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 2. Commercial Fleet Logistics &  │ Dynamic fleet dispatching, schedule │
│    Freight Distribution          │ compliance, fuel burn optimization. │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 3. Emergency Services Incident   │ Priority clear-corridor routing for │
│    Response (EMS / Fire / Police)│ ambulances, fire engines, police.   │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 4. Smart City Environmental &    │ Vehicle idle time tracking, urban   │
│    Urban Sustainability Boards   │ carbon accounting, SDG 13 compliance│
└──────────────────────────────────┴─────────────────────────────────────┘
```

### 1. Municipal Traffic Operations Centers (TOC / TMC)
Municipal transportation departments operate centralized monitoring centers to maintain highway throughput. By deploying this platform, operators move beyond CCTV monitoring to automated decision support. When the PySpark streaming engine detects that volume-to-capacity ratios on a primary highway segment exceed 0.85, the Decision Support System automatically issues advisories:
- Extend mainline green signal phases by +18 seconds at arterial intersections.
- Activate highway ramp meters to restrict upstream vehicle entry.
- Dynamically lower Variable Speed Limit (VSL) electronic signage to stabilize flow and prevent kinematic shockwaves.

### 2. Commercial Logistics, Supply Chain & E-Commerce Delivery
For last-mile delivery providers (e.g., Amazon, FedEx, UPS) and heavy freight carriers, unexpected traffic delays result in severe financial penalties and elevated fuel expenditures. By querying the Congestion-Aware Dijkstra routing engine, dispatch systems can steer delivery vans onto alternative corridors that are physically longer but save significant transit time by bypassing impending bottlenecks.

### 3. Emergency Medical and Public Safety Dispatch
In emergency medical services (EMS), response time directly impacts patient survival rates. When an ambulance must traverse congested downtown corridors, standard navigation tools often steer vehicles into gridlocked choke points where evasive maneuvering is impossible. The proposed routing engine identifies alternative express corridors, ensuring rapid emergency transit.

### 4. Urban Sustainability and Municipal Emissions Accounting
Under United Nations Sustainable Development Goal 13 (Climate Action), municipal governments face strict mandates to curtail greenhouse gas emissions. Idling vehicles trapped in stop-and-go highway traffic consume excessive fuel while operating at minimal engine efficiency. By preventing chronic congestion, this platform is projected to save over 3,200 vehicle-hours of idle time weekly across metropolitan corridors, providing measurable carbon reduction telemetry.

---

\newpage

# CHAPTER 2: PROJECT DESIGN AND METHODOLOGY

---

## 2.1 System Overview

The Smart Traffic Congestion Prediction and Intelligent Route Analytics platform is designed as an enterprise-grade, modular Big Data architecture. The platform decouples computation, storage, machine learning, and presentation into distinct, interchangeable tiers. This modularity ensures that individual components—such as the underlying MLlib classifier or the front-end dashboard—can be modified, scaled, or upgraded independently without disrupting the end-to-end data pipeline.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SYSTEM OVERVIEW TIERS                           │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. Data Ingestion & Storage   │ Real UCI Dataset, Twin Cities Network,      │
│    Tier                       │ Parquet storage, winutils/Hadoop abstraction│
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Distributed Processing     │ Apache Spark 4.2.0, Catalyst Optimizer,     │
│    Tier                       │ PySpark DataFrames, JVM memory manager      │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. Machine Learning &         │ Spark MLlib Pipelines, GBT/RF/DT/LR/NB,     │
│    Analytics Tier             │ Congestion-Aware Dijkstra Graph Engine      │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. Streaming & Ingestion      │ Kafka Event Producer, Spark Structured      │
│    Tier                       │ Streaming, Micro-batch scoring              │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 5. Presentation & Decision    │ Streamlit Dark Web App, Plotly 7.x charts,  │
│    Support Tier               │ OpenStreetMap tiles, Power BI Star Marts    │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

The system operates across two synchronous operational pathways:
1. **The Historical Batch Pathway:** Large-scale historical telemetry files (48,204 rows from the UCI Metro Interstate dataset) are ingested into PySpark DataFrames, subjected to automated cleaning and feature engineering, and used to train and validate 5 classification models and 3 continuous regressors.
2. **The Real-Time Streaming Pathway:** High-frequency IoT sensor telemetry events are emitted into a streaming pipeline (simulating Apache Kafka topics), consumed by Spark Structured Streaming in micro-batches, transformed using the pre-fitted feature pipeline, scored by the best-performing MLlib model, and displayed live in the user dashboard.

---

\newpage

## 2.2 Proposed System Architecture

The high-level architecture diagram illustrates the end-to-end data lifecycle from raw telemetry ingestion to decision-support visualization:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                              DATA INGESTION                            │
 │  • Authentic UCI Metro Dataset (48,204 rows, 9 attributes)             │
 │  • Twin Cities Corridor Network (8,064 records, 24 segments)           │
 └───────────────────┬────────────────────────────────┬───────────────────┘
                     │ (Historical Batch)             │ (Live IoT Stream)
                     ▼                                ▼
       ┌───────────────────────────┐    ┌───────────────────────────┐
       │   Apache Spark (Batch)    │    │    Kafka Event Producer   │
       │   • Explicit StructType   │    │    (Simulates Road Sensors)│
       │   • Deduplication         │    └─────────────┬─────────────┘
       │   • Outlier Filtering     │                  │ JSON Stream
       │   • Null Imputation       │                  ▼
       └─────────────┬─────────────┘    ┌───────────────────────────┐
                     │                  │ Spark Structured Streaming│
                     ▼                  │ • Micro-Batch Consumer    │
       ┌───────────────────────────┐    │ • Real-time Feature Prep  │
       │    Feature Engineering    │    │ • Live ML Inference       │
       │    • Rush / Peak Flags    │    └─────────────┬─────────────┘
       │    • V/C & Speed Ratios   │                  │ Live CSV Batches
       │    • VectorAssembler      │                  ▼
       └─────────────┬─────────────┘    ┌───────────────────────────┐
                     │                  │    Real-Time Stream Sink  │
                     ▼                  └─────────────┬─────────────┘
       ┌───────────────────────────┐                  │
       │  PySpark MLlib Training   │                  │
       │  • GBTClassifier (Best)   │                  │
       │  • Random Forest          │                  │
       │  • Decision Tree          │                  │
       │  • Logistic Regression    │                  │
       │  • Naive Bayes            │                  │
       └─────────────┬─────────────┘                  │
                     │ Trained Models                 │
                     ▼                                │
       ┌───────────────────────────┐                  │
       │ Congestion-Aware Dijkstra │                  │
       │ • Dynamic Penalty Multiplier                 │
       │ • Optimal & Alt Route     │                  │
       └─────────────┬─────────────┘                  │
                     │                                │
                     ▼                                ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     BUSINESS INTELLIGENCE PRESENTATION                 │
 │   • Streamlit Web Dashboard (8 Live Interactive Modules)               │
 │   • Power BI Star-Schema Export Marts                                  │
 │   • Decision Support System (DSS) Policy Advisories                    │
 └────────────────────────────────────────────────────────────────────────┘
```

The architecture is characterized by strict separation of concerns:
- Telemetry flows downstream through defined interfaces.
- The machine learning pipeline outputs immutable serialized model artifacts.
- The routing engine consumes both topological graph data and instantaneous congestion predictions to update edge weights in memory.
- The front-end dashboard reads exclusively from pre-aggregated metrics and real-time streaming output sinks, ensuring low query latency.

---

\newpage

## 2.3 Architecture Components and Their Functions

Each component within the proposed architecture performs a specialized, critical function:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE SUBSYSTEM FUNCTIONALITY                     │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Module Name              │ Primary Responsibilities & Implementation Details│
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 1. Spark Session Core    │ Manages JVM memory, sets local[*] master,        │
│    (spark_session.py)    │ binds winutils.exe/Hadoop, initializes Catalyst. │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 2. Data Ingestion Engine │ Reads raw CSVs via explicit StructType schemas;  │
│    (data_ingestion.py)   │ enforces typing for Double, Integer, Timestamp.  │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 3. Preprocessing Module  │ Imputes nulls via median/mode; bounds outliers;  │
│    (preprocessing.py)    │ calculates Speed Ratio, V/C, congestion classes. │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 4. Feature Pipeline      │ Extracts temporal indicators; VectorAssembler;   │
│    (feature_eng.py)      │ StandardScaler normalizes feature vectors.       │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 5. MLlib Training Engine │ Trains 5 classifiers & 3 regressors on 80/20     │
│    (train_models.py)     │ train/test split; evaluates via MulticlassEval.  │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 6. Dijkstra Graph Core   │ Models 10 junction nodes & 24 directed segments; │
│    (graph.py, dijkstra)  │ computes cost via (D/S * 60) * (1 + alpha * C).  │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 7. Streaming Engine      │ Emits JSON IoT events; Spark Structured Stream   │
│    (spark_streaming.py)  │ scores micro-batches; writes CSV/console sinks.  │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 8. Streamlit BI App      │ Executive dark-themed UI; Plotly charts; OSM     │
│    (dashboard/app.py)    │ route map; DSS cards; Power BI mart exports.     │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

### Detailed Functional Breakdown

1. **SparkSession Initialization (`src/spark/spark_session.py`):**
   Acts as the unified execution driver. Configures `spark.sql.shuffle.partitions` to 8 for responsive local execution, sets driver memory to 4 GB, binds `PYSPARK_PYTHON` to the active virtual environment Python binary to prevent worker synchronization failures, and configures `HADOOP_HOME` with Windows native binaries (`winutils.exe` and `hadoop.dll`).

2. **Data Ingestion Subsystem (`src/spark/data_ingestion.py`):**
   Eliminates the computational overhead and schema instability of `inferSchema=True` by explicitly constructing programmatic `StructType` definitions with designated nullability constraints.

3. **Preprocessing & Categorization (`src/spark/preprocessing.py`):**
   Executes distributed transformations: converts Kelvin temperatures to Celsius, filters physical speed anomalies outside $[10, 140]\text{ km/h}$, and computes the deterministic multi-class congestion label.

4. **Feature Engineering Pipeline (`src/spark/feature_engineering.py`):**
   Constructs a Spark MLlib `Pipeline` combining `StringIndexer` for categorical weather encoding, `VectorAssembler` for feature concatenation, and `StandardScaler` to prevent high-magnitude volumetric features from distorting optimization gradients.

5. **MLlib Modeling & Evaluation (`src/ml/`):**
   Trains classification algorithms using consistent random seeds (seed = 42). Employs `OneVsRest` wrappers where multiclass outputs require binary reduction (e.g., native GBT), and computes comprehensive metrics via `MulticlassClassificationEvaluator`.

6. **Graph Topology & Routing Engine (`src/routing/`):**
   Constructs an adjacency-list directed network representing the Minneapolis–St. Paul interstate system. The modified Dijkstra algorithm calculates optimal and alternative bypass routes based on live impedance weights.

7. **Structured Streaming Engine (`src/streaming/`):**
   Consumes continuous file streams from `data/streaming/input/`, processes events through the pre-trained MLlib pipeline, and writes scored outputs to persistent sinks.

8. **Executive BI Dashboard (`dashboard/app.py`):**
   A multi-page Streamlit web application providing interactive parameter exploration, real-time prediction forms, model metric comparisons, and GIS routing maps.

---

\newpage

## 2.4 Proposed Methodology

The execution methodology follows the Cross-Industry Standard Process for Data Mining (CRISP-DM), adapted specifically for Big Data distributed streaming pipelines:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ADAPTED CRISP-DM METHODOLOGY                      │
├─────────────────────────┬──────────────────────────────────────────────┤
│ Phase 1: Business &     │ Define highway bottleneck dynamics, cost     │
│ Domain Understanding    │ functions, and multi-tier congestion states. │
├─────────────────────────┼──────────────────────────────────────────────┤
│ Phase 2: Data           │ Ingest UCI Metro Interstate & Corridor logs; │
│ Understanding & EDA     │ analyze volume, speed, and weather patterns. │
├─────────────────────────┼──────────────────────────────────────────────┤
│ Phase 3: Data           │ Deduplication, null imputation, IQR outlier  │
│ Preparation & Cleaning  │ bounding, VectorAssembler feature scaling.   │
├─────────────────────────┼──────────────────────────────────────────────┤
│ Phase 4: Machine        │ Train 5 MLlib classifiers & 3 regressors;    │
│ Learning Modeling       │ hyperparameter tuning on 80/20 split.        │
├─────────────────────────┼──────────────────────────────────────────────┤
│ Phase 5: Routing &      │ Construct directed road graph; formulate     │
│ Evaluation Phase        │ Congestion-Aware Dijkstra with penalty alpha.│
├─────────────────────────┼──────────────────────────────────────────────┤
│ Phase 6: Streaming &    │ Deploy Kafka simulation, Structured Stream   │
│ Production Deployment   │ micro-batching, Streamlit & Power BI marts.  │
└─────────────────────────┴──────────────────────────────────────────────┘
```

### Phase Details

* **Phase 1 — Domain Formalization:** Establish quantitative thresholds for traffic states based on transportation engineering theory, defining mathematical relationships between flow rate, speed degradation, and road capacity.
* **Phase 2 — Exploratory Data Analysis (EDA):** Perform distributed Spark SQL aggregations to identify peak diurnal traffic patterns, compute weather-induced speed reductions, and map corridor-specific bottlenecks.
* **Phase 3 — Data Preparation:** Assemble the PySpark transformation pipeline: parse timestamps, engineer rush-hour binary indicators, encode categorical weather strings, assemble feature vectors, and scale features using unit standard deviation.
* **Phase 4 — Model Construction:** Implement and train five distinct PySpark MLlib classifiers alongside continuous speed regressors on an 80% training partition, evaluating performance on a holdout 20% test partition.
* **Phase 5 — Algorithmic Graph Optimization:** Model 10 Twin Cities junctions and 24 directed segments; develop the congestion-penalized Dijkstra algorithm and alternative path calculation logic.
* **Phase 6 — Deployment & Streaming:** Implement real-time IoT event generation, configure Spark Structured Streaming micro-batch processing, build the interactive Streamlit BI dashboard, and export Power BI star-schema marts.

---

\newpage

## 2.5 Methodology Workflow Use-Case / DFD Flow Diagram

The functional flow of data through the system is formalized via Level-0 and Level-1 Data Flow Diagrams (DFDs):

### Level-0 Context DFD
```
  [Road IoT Sensors / UCI Data]
                │
                ▼ (Raw Vehicular Telemetry)
  ┌───────────────────────────────────────────────┐
  │   0.0 SMART TRAFFIC CONGESTION PREDICTION     │
  │        & ROUTE ANALYTICS PLATFORM             │
  └───────────────────────┬───────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼ (Routes, Alerts, Delays)      ▼ (KPIs, Reports, Marts)
  [Motorists & Fleet Drivers]     [City Engineers & BI Analysts]
```

### Level-1 Detailed Data Flow Diagram
```
   [Raw Data Source]
          │
          ▼  (Raw Records)
   ┌─────────────────────────────────────────┐
   │ 1.0 Data Ingestion & Schema Enforcement │
   └────────────────────┬────────────────────┘
                        │ (Typed Spark DataFrame)
                        ▼
   ┌─────────────────────────────────────────┐
   │ 2.0 Cleaning, Imputation & Outlier IQR  │
   └────────────────────┬────────────────────┘
                        │ (Cleaned DataFrame)
                        ▼
   ┌─────────────────────────────────────────┐
   │ 3.0 Feature Engineering & Vector Scaling│
   └────────────────────┬────────────────────┘
                        │ (Normalized Feature Vectors)
         ┌──────────────┴──────────────┐
         ▼                             ▼
   ┌───────────────────────────┐ ┌───────────────────────────┐
   │ 4.0 MLlib Model Training  │ │ 5.0 Live Stream Scoring   │
   │     (80/20 Train/Test)    │ │     (Micro-Batch Ingest)  │
   └─────────────┬─────────────┘ └─────────────┬─────────────┘
                 │ (Trained Models)            │ (Scored Telemetry)
                 └──────────────┬──────────────┘
                                │
                                ▼
   ┌─────────────────────────────────────────┐
   │ 6.0 Dynamic Edge Weight Impedance Update│
   └────────────────────┬────────────────────┘
                        │ (Updated Graph Costs)
                        ▼
   ┌─────────────────────────────────────────┐
   │ 7.0 Congestion-Aware Dijkstra Execution │
   └────────────────────┬────────────────────┘
                        │ (Optimal Paths, Alt Paths, ETAs)
         ┌──────────────┴──────────────┐
         ▼                             ▼
   ┌───────────────────────────┐ ┌───────────────────────────┐
   │ 8.0 Streamlit Web BI App  │ │ 9.0 Power BI Data Marts   │
   └───────────────────────────┘ └───────────────────────────┘
```

---

\newpage

## 2.6 Algorithms and Techniques Used

The project integrates six foundational algorithms spanning predictive machine learning, ensemble decision trees, probabilistic classification, linear regression, and graph optimization:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ALGORITHMS IMPLEMENTED IN PLATFORM                   │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 1. Gradient-Boosted Trees│ Additive stage-wise tree ensemble with      │
│    (GBTClassifier)       │ OneVsRest wrapper; best classifier (98.83%) │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 2. Random Forest         │ Bootstrap aggregating (bagging) ensemble    │
│    Classifier            │ with random feature subspaces (98.71%)      │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 3. Decision Tree         │ Recursive binary partitioning using         │
│    Classifier            │ Gini Impurity metric (98.25%)               │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 4. Logistic Regression   │ Multinomial softmax loss with L2 ridge      │
│                          │ regularization penalty (97.86%)             │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 5. Naive Bayes           │ Conditional probability model under feature │
│    Classifier            │ independence assumptions (87.06%)           │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 6. Congestion-Aware      │ Priority-queue shortest path with dynamic   │
│    Dijkstra Algorithm    │ penalty multiplier alpha [0.0 to 1.5]       │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### Detailed Algorithmic Formulations

### 1. Gradient-Boosted Tree Classifier (GBTClassifier)
Gradient-Boosted Trees construct an ensemble of decision trees sequentially. Each successive tree $h_m(x)$ is trained to predict the negative gradient (pseudo-residuals) of the loss function with respect to the current ensemble prediction:
$$F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)$$
where $\gamma_m$ represents the step length determined by line search. Because PySpark's native `GBTClassifier` supports binary classification, it is wrapped in an `OneVsRest` estimator, training four independent binary classifiers to achieve robust 4-class multiclass predictions.

### 2. Random Forest Classifier (RandomForestClassifier)
Random Forests construct a multitude of decision trees during training using bootstrap aggregation (bagging). For each tree, a random subset of training instances is sampled with replacement, and at each split node, a random subset of features is evaluated:
$$\hat{C}_{\text{rf}}(x) = \text{majority\_vote}\left(\{C_b(x)\}_{b=1}^B\right)$$
This dual randomization decorrelates individual trees, dramatically reducing variance and eliminating overfitting risks.

### 3. Decision Tree Classifier (DecisionTreeClassifier)
Serves as the foundational baseline tree model. Splitting decisions at each node are determined by minimizing Gini Impurity:
$$I_G(p) = 1 - \sum_{i=1}^J p_i^2$$
where $p_i$ is the probability of an item being categorized into class $i$.

### 4. Multinomial Logistic Regression
Models class probabilities using the softmax function:
$$P(Y=k \mid X=x) = \frac{e^{\beta_k^T x}}{\sum_{j=1}^K e^{\beta_j^T x}}$$
Optimized via L-BFGS with L2 regularization to prevent feature coefficient divergence.

### 5. Naive Bayes Classifier
Calculates posterior probabilities via Bayes' Theorem under the conditional independence assumption:
$$P(C_k \mid x) \propto P(C_k) \prod_{i=1}^n P(x_i \mid C_k)$$

### 6. Congestion-Aware Dijkstra Algorithm
Given a directed graph $G = (V, E)$, the dynamic edge impedance cost between nodes $u$ and $v$ is formulated as:
$$\text{Cost}(u, v) = \left( \frac{\text{Distance}(u, v)}{\text{Speed}(u, v)} \times 60 \right) \times \left(1 + \alpha \times \text{CongestionFactor}(u, v)\right)$$
where:
* $\text{Distance}(u, v)$ is edge length in kilometers.
* $\text{Speed}(u, v)$ is current observed or predicted speed in km/h.
* $\alpha \in [0.0, 1.5]$ is the user-configured congestion penalty factor.
* $\text{CongestionFactor} \in \{ \text{LOW}: 0.0, \, \text{MEDIUM}: 0.5, \, \text{HIGH}: 1.5, \, \text{SEVERE}: 3.0 \}$.

---

\newpage

## 2.7 Dataset Description

The platform utilizes two complementary datasets: a primary real-world benchmark dataset from the UCI Machine Learning Repository, and a secondary topological corridor dataset modeling the Minneapolis–St. Paul metropolitan interstate network.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATASET CHARACTERISTICS                         │
├──────────────────────────┬─────────────────────────────────────────────┤
│ Primary Dataset Name     │ Metro Interstate Traffic Volume             │
│ Source / Provenance      │ UCI Machine Learning Repository             │
│ Geographic Coverage      │ I-94 Westbound (Minneapolis ↔ St. Paul, MN) │
│ Temporal Span            │ 2012 to 2018 (Hourly continuous logs)       │
│ Total Volume             │ 48,204 rows × 9 attributes                  │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Secondary Dataset Name   │ Twin Cities Metropolitan Corridor Network   │
│ Geographic Coverage      │ 10 Interstate Interchange Junction Nodes    │
│ Network Structure        │ 24 Directed Highway Segments                │
│ Total Volume             │ 8,064 records × 18 attributes               │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### Primary Dataset Schema (UCI Metro Interstate)
* `holiday` (StringType): Categorical indicator for public holidays (e.g., Thanksgiving, Christmas, None).
* `temp` (DoubleType): Average hourly ambient temperature recorded in Kelvin.
* `rain_1h` (DoubleType): Precipitation recorded in millimeters during the hour.
* `snow_1h` (DoubleType): Snowfall accumulation recorded in millimeters during the hour.
* `clouds_all` (IntegerType): Cloud coverage percentage $[0, 100\%]$.
* `weather_main` (StringType): Macro weather category (Clear, Clouds, Rain, Snow, Mist, Fog).
* `weather_description` (StringType): Detailed meteorological text (e.g., light rain, heavy snow).
* `date_time` (TimestampType): Hourly observation timestamp (UTC-6 timezone).
* `traffic_volume` (IntegerType): Total vehicular count passing the inductive loop sensor per hour.

### Secondary Network Topology (Twin Cities Corridor)
Models 10 strategic metropolitan highway junctions:
1. `DOWNTOWN_MPLS` (Lat: 44.9778, Lon: -93.2650) — Downtown Minneapolis Hub
2. `DOWNTOWN_STP` (Lat: 44.9537, Lon: -93.0900) — Downtown St. Paul State Capitol
3. `AIRPORT_MSP` (Lat: 44.8848, Lon: -93.2223) — Minneapolis–St. Paul International Airport
4. `BLOOMINGTON` (Lat: 44.8408, Lon: -93.2983) — South Metro Commercial Hub (Mall of America)
5. `ROSEVILLE` (Lat: 45.0061, Lon: -93.1566) — North Central Arterial Junction
6. `PLYMOUTH` (Lat: 45.0105, Lon: -93.4555) — West Metro Beltway Interchange
7. `EDINA` (Lat: 44.8897, Lon: -93.3501) — Southwest Metro Interchange
8. `WOODBURY` (Lat: 44.9239, Lon: -92.9594) — East Metro Gateway
9. `BROOKLYN_CTR` (Lat: 45.0747, Lon: -93.3297) — Northwest Gateway
10. `EAGAN` (Lat: 44.8041, Lon: -93.1669) — South Gateway Interchange

---

\newpage

## 2.8 Data Collection and Data Preprocessing

The preprocessing subsystem executes rigorous programmatic data transformations in Apache Spark to clean, validate, and standardize raw telemetry records before feature engineering:

```
    [Raw Telemetry Ingestion]
                │
                ▼
    [1. StructType Schema Enforcement] ──▶ Rejects malformed types
                │
                ▼
    [2. Deduplication Engine]         ──▶ Eliminates duplicate timestamps
                │
                ▼
    [3. Null Value Imputation]        ──▶ Median for numeric; Mode for weather
                │
                ▼
    [4. Physical Outlier Bounding]    ──▶ -35°C to +45°C; 10 to 140 km/h
                │
                ▼
    [5. Kelvin-to-Celsius Conversion] ──▶ °C = Kelvin - 273.15
                │
                ▼
    [6. Congestion Threshold Mapping] ──▶ Speed Ratio + V/C Ratio → 4 Classes
                │
                ▼
    [Cleaned Spark DataFrame Ready for Pipeline]
```

### Preprocessing Execution Details

1. **Programmatic Schema Enforcement:**
   Rather than utilizing Spark's computational-heavy `inferSchema`, schemas are explicitly defined using `StructType` and `StructField` arrays.

2. **Deduplication:**
   Duplicate sensor log records sharing identical timestamps and segment identifiers are eliminated via Spark's `.dropDuplicates()` transformation.

3. **Missing Value Imputation:**
   Missing temperature and speed observations are imputed using seasonal median values calculated across identical hourly windows. Missing categorical weather values are imputed using the empirical mode.

4. **Physical Outlier Bounding:**
   Sensors occasionally transmit corrupt physical measurements due to voltage fluctuations or line noise:
   - Temperatures outside $[-35^\circ\text{C}, +45^\circ\text{C}]$ are clamped.
   - Speeds outside $[10\text{ km/h}, 140\text{ km/h}]$ are bound to realistic physical highway limits.

5. **Empirical Congestion Labeling:**
   Congestion labels are derived deterministically based on highway capacity principles:
   $$\text{Speed Ratio} = \frac{\text{Average Speed}}{95.0\text{ km/h}}, \quad \text{V/C Ratio} = \frac{\text{Traffic Volume}}{4500\text{ vph}}$$
   - **LOW:** $\text{Speed Ratio} \ge 0.80$ AND $\text{V/C Ratio} < 0.60$
   - **MEDIUM:** $\text{Speed Ratio} \ge 0.60$ AND $\text{V/C Ratio} < 0.85$
   - **HIGH:** $\text{Speed Ratio} \ge 0.35$ AND $\text{V/C Ratio} < 1.05$
   - **SEVERE:** $\text{Speed Ratio} < 0.35$ OR $\text{V/C Ratio} \ge 1.05$

---

\newpage

## 2.9 Tools and Technologies Used

The technology stack is selected to ensure performance, reproducibility, and compliance with enterprise Big Data standards:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE TECHNOLOGY STACK                       │
├───────────────────────┬───────────────────┬────────────────────────────┤
│ Technology / Library  │ Version           │ Primary System Purpose     │
├───────────────────────┼───────────────────┼────────────────────────────┤
│ Python                │ 3.11.x / 3.10+    │ Core programming runtime   │
│ Apache Spark (PySpark)│ 4.2.0             │ Distributed computation    │
│ Spark MLlib           │ 4.2.0             │ Distributed machine learning│
│ Spark Structured      │ 4.2.0             │ Real-time micro-batch      │
│   Streaming           │                   │   stream processing        │
│ Apache Kafka          │ kafka-python-ng   │ High-throughput IoT sensor │
│   Simulation          │ 2.2.3             │   message publishing       │
│ NetworkX / Dijkstra   │ 3.x / Native      │ Directed graph modeling    │
│ Streamlit             │ 1.35+ / 1.65.0    │ Executive BI dashboard UI  │
│ Plotly                │ 7.1.0             │ Dark-themed analytics & GIS│
│ Matplotlib & Seaborn  │ 3.11+ / 0.13+     │ Static EDA plot exports    │
│ Microsoft Power BI    │ Desktop / Web     │ Star-schema enterprise BI  │
│ Docker & Compose      │ 3.8 Spec          │ Multi-container deployment │
└───────────────────────┴───────────────────┴────────────────────────────┘
```

### Architectural Rationale for Core Tools
* **Apache Spark 4.2.0:** Selected for its state-of-the-art Catalyst query optimizer, Tungsten off-heap execution engine, and native support for distributed MLlib vector pipelines.
* **Streamlit & Plotly 7.x:** Enables dynamic data-driven UI rendering with sub-second reactivity. Plotly’s latest Map APIs provide interactive OpenStreetMap spatial navigation without requiring commercial Mapbox API tokens.
* **Apache Kafka & Structured Streaming:** Emulates enterprise message brokers, ensuring that simulated roadside sensors publish telemetry that is ingested and scored under realistic micro-batch latencies.

---

\newpage

## 2.10 Experimental Setup and Configuration

To validate the reproducibility of the system across standard student computing environments and enterprise servers, the execution environment was configured as follows:

```
┌────────────────────────────────────────────────────────────────────────┐
│                       EXPERIMENTAL CONFIGURATION                       │
├───────────────────────┬────────────────────────────────────────────────┤
│ Host Hardware Specs   │ Intel Core i5/i7 (8 Cores), 16 GB DDR4 RAM,   │
│                       │ 512 GB NVMe SSD                                │
├───────────────────────┼────────────────────────────────────────────────┤
│ Operating Systems     │ Windows 11 64-bit / Ubuntu Linux 22.04 LTS     │
├───────────────────────┼────────────────────────────────────────────────┤
│ JVM Runtime           │ OpenJDK 17 64-bit Server VM                    │
├───────────────────────┼────────────────────────────────────────────────┤
│ Spark Driver Config   │ master = "local[*]", driver.memory = "4g",     │
│                       │ driver.host = "127.0.0.1"                      │
├───────────────────────┼────────────────────────────────────────────────┤
│ Windows Native Layer  │ winutils.exe & hadoop.dll (Hadoop 3.3.5)       │
├───────────────────────┼────────────────────────────────────────────────┤
│ Python Isolation      │ Python 3.11 Virtual Environment (.venv)        │
├───────────────────────┼────────────────────────────────────────────────┤
│ Train / Test Split    │ 80% Training (seed=42), 20% Holdout Test       │
└───────────────────────┴────────────────────────────────────────────────┘
```

### Critical Environmental Fixes Applied
1. **Worker Desynchronization Resolution:** On Windows, PySpark worker sub-processes frequently fail to locate the virtual environment Python interpreter, causing `SocketTimeoutException`. This was permanently resolved by programmatically setting `os.environ["PYSPARK_PYTHON"] = sys.executable` before `SparkSession` instantiation.
2. **Windows File System Abstraction:** Native file I/O operations in Apache Spark require Hadoop native libraries. `HADOOP_HOME` was configured with verified `winutils.exe` and `hadoop.dll` binaries in `E:\smarttraffic\hadoop\bin`.
3. **Headless Visualization Backend:** When generating static evaluation charts during automated training scripts, Tkinter thread errors can crash Spark jobs. The non-interactive `matplotlib.use('Agg')` backend was enforced across all analytical modules.

---

\newpage

## 2.11 Evaluation Metrics

To provide rigorous academic evaluation, models are measured across standard classification and regression metrics:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      EVALUATION METRIC EQUATIONS                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Classification Accuracy:                                            │
│    Accuracy = (TP + TN) / (TP + TN + FP + FN)                          │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Precision (Positive Predictive Value):                              │
│    Precision = TP / (TP + FP)                                          │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Recall (Sensitivity / True Positive Rate):                          │
│    Recall = TP / (TP + FN)                                             │
├────────────────────────────────────────────────────────────────────────┤
│ 4. F1-Score (Harmonic Mean of Precision and Recall):                   │
│    F1 = 2 * (Precision * Recall) / (Precision + Recall)                │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Root Mean Squared Error (RMSE):                                     │
│    RMSE = sqrt( (1/n) * sum_{i=1}^n (y_i - \hat{y}_i)^2 )             │
├────────────────────────────────────────────────────────────────────────┤
│ 6. Mean Absolute Error (MAE):                                          │
│    MAE = (1/n) * sum_{i=1}^n |y_i - \hat{y}_i|                         │
├────────────────────────────────────────────────────────────────────────┤
│ 7. Coefficient of Determination (R² Score):                           │
│    R² = 1 - [ sum (y_i - \hat{y}_i)^2 / sum (y_i - \bar{y})^2 ]       │
└────────────────────────────────────────────────────────────────────────┘
```

### Empirical Benchmark Results Achieved

All five PySpark MLlib classifiers were trained on identical 80% partitions and evaluated against holdout 20% test partitions using `MulticlassClassificationEvaluator`:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   PYSPARK MLLIB CLASSIFICATION BENCHMARK RESULTS                       │
├────────────────────────────┬───────────┬───────────┬────────┬──────────┬───────────────┤
│ Model Architecture         │ Accuracy  │ Precision │ Recall │ F1-Score │ Overall Rank  │
├────────────────────────────┼───────────┼───────────┼────────┼──────────┼───────────────┤
│ Gradient-Boosted Trees     │ 98.83%    │ 98.79%    │ 98.83% │ 0.9881   │ 🥇 1st (Best) │
│ Random Forest Classifier   │ 98.71%    │ 98.66%    │ 98.71% │ 0.9868   │ 🥈 2nd        │
│ Decision Tree Classifier   │ 98.25%    │ 98.24%    │ 98.25% │ 0.9824   │ 🥉 3rd        │
│ Logistic Regression        │ 97.86%    │ 97.78%    │ 97.86% │ 0.9782   │ 4th           │
│ Naive Bayes Classifier     │ 87.06%    │ 93.71%    │ 87.06% │ 0.9024   │ 5th           │
└────────────────────────────┴───────────┴───────────┴────────┴──────────┴───────────────┘
```

### Continuous Speed Regression Benchmark Results

Continuous travel speed predictors evaluated via `RegressionEvaluator`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PYSPARK REGRESSION BENCHMARK RESULTS                 │
├────────────────────────────┬──────────────┬─────────────┬──────────────┤
│ Model Architecture         │ RMSE (km/h)  │ MAE (km/h)  │ R² Score     │
├────────────────────────────┼──────────────┼─────────────┼──────────────┤
│ Linear Regression          │ 0.104        │ 0.085       │ 0.9998       │
│ GBT Regressor              │ 0.568        │ 0.270       │ 0.9940       │
│ Random Forest Regressor    │ 1.314        │ 0.901       │ 0.9678       │
└────────────────────────────┴──────────────┴─────────────┴──────────────┘
```

---

*This document constitutes the complete, comprehensive Milestone 1 Project Report for CSET-371.*
