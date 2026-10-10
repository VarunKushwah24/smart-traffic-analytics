# Research Methodology, Formulations & ML Pipelines

This document outlines the theoretical, mathematical, and algorithmic methodologies implemented across the PySpark data processing, machine learning benchmarking, and route optimization components.

---

## 1. Congestion Classification Formulation

To establish an objective, reproducible measure of traffic congestion without arbitrary thresholds, we formulated congestion by coupling the **Bureau of Public Roads (BPR)** speed-flow relationship with the **Volume-to-Capacity Ratio ($V/C$)** and **Speed Deficit Ratio ($S / S_{\text{free-flow}}$)**.

### Mathematical Formulation:
$$\text{Speed Ratio} = \frac{v_t}{v_{\text{limit}}}$$
$$\text{Volume-to-Capacity Ratio} = \frac{Q_t}{C_{\text{segment}}}$$

Where:
- $v_t$ is the observed average speed on the road segment at time $t$ ($\text{km/h}$).
- $v_{\text{limit}}$ is the posted free-flow speed limit ($\text{km/h}$).
- $Q_t$ is the traffic volume (vehicles per hour).
- $C_{\text{segment}}$ is the theoretical corridor capacity (vehicles per hour).

### Congestion Level Decision Boundary:
1. **LOW (Free Flow):**
   $$\text{Speed Ratio} \ge 0.80 \quad \text{AND} \quad \frac{Q_t}{C} < 0.60$$
2. **MEDIUM (Moderate Flow):**
   $$\text{Speed Ratio} \in [0.60, 0.80) \quad \text{AND} \quad \frac{Q_t}{C} \in [0.60, 0.85)$$
3. **HIGH (Congested Flow):**
   $$\text{Speed Ratio} \in [0.35, 0.60) \quad \text{AND} \quad \frac{Q_t}{C} \in [0.85, 1.05)$$
4. **SEVERE (Gridlock / Breakdown):**
   $$\text{Speed Ratio} < 0.35 \quad \text{OR} \quad \frac{Q_t}{C} \ge 1.05$$

---

## 2. Spatio-Temporal Feature Engineering

Features are computed using PySpark SQL functions to prevent data leakage:
- **Temporal Cyclical Indicators:**
  - $\text{hour} \in [0, 23]$
  - $\text{day\_of\_week} \in [1, 7]$
  - $\text{is\_weekend} \in \{0, 1\}$
- **Peak Hour Flags:**
  - $\text{is\_morning\_peak} = 1$ if $\text{hour} \in [7, 9]$ and $\text{is\_weekend} = 0$
  - $\text{is\_evening\_peak} = 1$ if $\text{hour} \in [16, 19]$ and $\text{is\_weekend} = 0$
  - $\text{is\_rush\_hour} = \text{is\_morning\_peak} \lor \text{is\_evening\_peak}$
- **Weather Indexing:** Nominal categories (`Clear`, `Clouds`, `Rain`, `Snow`, `Mist`) transformed into numeric dense categories via `StringIndexer`.
- **Vector Assembly:** Combined into dense feature vectors and scaled using `StandardScaler` ($\mu = 0, \sigma = 1$).

---

## 3. Dynamic Dijkstra Route Optimization Formulation

Standard routing algorithms minimize distance:
$$\min \sum_{e \in P} d_e$$
This creates systemic bottlenecks because high-capacity highways quickly saturate. Our system formulates a **Congestion-Penalized Dynamic Cost Function**:

$$C(e) = T_{\text{travel}}(e) \times \left(1 + \alpha \cdot \mu_{\text{congestion}}(e)\right)$$

Where:
$$T_{\text{travel}}(e) = \frac{d_e}{v_e} \times 60 \quad (\text{minutes})$$
- $d_e$ is the physical length of road segment $e$ in kilometers.
- $v_e$ is the current live or predicted speed on segment $e$ in $\text{km/h}$.
- $\alpha \ge 0$ is the sensitivity penalty parameter (default $\alpha = 0.50$).
- $\mu_{\text{congestion}}$ is the penalty multiplier based on congestion state:
  $$\mu = \begin{cases} 0.00 & \text{for LOW} \\ 0.35 & \text{for MEDIUM} \\ 0.90 & \text{for HIGH} \\ 2.20 & \text{for SEVERE} \end{cases}$$

### Secondary Alternative Route Formulation:
To compute the contingency route, the algorithm detects the bottleneck segment $e_{\text{bottleneck}} = \arg\max_{e \in P^*} T_{\text{travel}}(e)$ of the primary path $P^*$ and temporarily removes it from the graph:
$$G' = (V, E \setminus \{e_{\text{bottleneck}}\})$$
Dijkstra's algorithm is re-run on $G'$ to yield the secondary corridor route.

---

## 4. Model Evaluation Formulations

All PySpark classification models are evaluated using weighted multiclass metrics:

$$\text{Accuracy} = \frac{\sum_{i=1}^K TP_i}{N}$$
$$\text{Precision}_{\text{weighted}} = \sum_{i=1}^K \frac{N_i}{N} \times \frac{TP_i}{TP_i + FP_i}$$
$$\text{Recall}_{\text{weighted}} = \sum_{i=1}^K \frac{N_i}{N} \times \frac{TP_i}{TP_i + FN_i}$$
$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

For continuous speed prediction regressors:
$$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
$$\text{MAE} = \frac{1}{N}\sum_{i=1}^N |y_i - \hat{y}_i|$$
$$R^2 = 1 - \frac{\sum_{i=1}^N (y_i - \hat{y}_i)^2}{\sum_{i=1}^N (y_i - \bar{y})^2}$$
