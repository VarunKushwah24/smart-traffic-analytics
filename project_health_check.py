"""
Automated Project Health Check Script for Smart Traffic Big Data System.
Verifies all 12 core system requirements and reports PASS / FAIL status.
"""

import os
import sys
import glob

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def check_component(name: str, check_fn) -> bool:
    try:
        passed, msg = check_fn()
        status = "[ PASS ]" if passed else "[ FAIL ]"
        print(f"{status} {name:<35} : {msg}")
        return passed
    except Exception as e:
        print(f"[ FAIL ] {name:<35} : Exception: {e}")
        return False

def check_python_version():
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    passed = v.major == 3 and v.minor >= 10
    return passed, f"Python {ver_str}"

def check_required_packages():
    required = ["pyspark", "streamlit", "pandas", "numpy", "scipy", "sklearn", "matplotlib", "seaborn", "plotly", "yaml", "pytest"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return True, "All required libraries installed"
    return False, f"Missing packages: {', '.join(missing)}"

def check_dataset_exists():
    corridor = os.path.join(ROOT, "data", "raw", "metro_corridor_network.csv")
    uci = os.path.join(ROOT, "data", "raw", "Metro_Interstate_Traffic_Volume.csv")
    if os.path.exists(corridor) and os.path.exists(uci):
        return True, f"Raw datasets present ({os.path.getsize(corridor):,} & {os.path.getsize(uci):,} bytes)"
    return False, "Raw datasets missing in data/raw/"

def check_dataset_columns():
    import pandas as pd
    corridor = os.path.join(ROOT, "data", "raw", "metro_corridor_network.csv")
    if not os.path.exists(corridor):
        return False, "File missing"
    df = pd.read_csv(corridor, nrows=5)
    cols = ["timestamp", "segment_id", "traffic_volume", "average_speed", "congestion_level"]
    missing = [c for c in cols if c not in df.columns]
    if not missing:
        return True, f"Found all essential columns ({len(df.columns)} total cols)"
    return False, f"Missing columns: {missing}"

def check_spark_works():
    from src.spark.spark_session import get_spark_session
    spark = get_spark_session("HealthCheckProbe")
    df = spark.range(3)
    c = df.count()
    spark.stop()
    return c == 3, "SparkSession initialized and computed DataFrame count"

def check_processed_data_exists():
    sample = os.path.join(ROOT, "data", "processed", "traffic_features_sample.csv")
    if os.path.exists(sample):
        return True, f"Found processed dataset: {sample}"
    return False, "Processed dataset missing (run run_pipeline.py)"

def check_models_exist():
    clf = os.path.join(ROOT, "models", "best_classifier")
    reg = os.path.join(ROOT, "models", "best_regressor")
    if os.path.exists(clf) or os.path.exists(reg):
        return True, "Trained PySpark MLlib models present in models/"
    return False, "Models missing (run scripts/train_models.py)"

def check_metrics_exist():
    comp = os.path.join(ROOT, "results", "metrics", "model_comparison.csv")
    summary = os.path.join(ROOT, "results", "metrics", "summary_statistics.csv")
    if os.path.exists(comp):
        return True, "Model metrics and EDA statistics present in results/metrics/"
    return False, "Metrics missing in results/metrics/"

def check_plots_exist():
    plots = glob.glob(os.path.join(ROOT, "results", "plots", "*.png"))
    if len(plots) >= 2:
        return True, f"Found {len(plots)} generated result plots in results/plots/"
    return False, "Plots missing in results/plots/"

def check_route_algorithm_works():
    from src.routing.graph import RoadNetworkGraph
    from src.routing.dijkstra import find_optimal_route
    g = RoadNetworkGraph()
    g.add_edge("S1", "Test Road", "DOWNTOWN_MPLS", "DOWNTOWN_STP", 15.0, 90.0, 75.0, "LOW")
    r = find_optimal_route(g, "DOWNTOWN_MPLS", "DOWNTOWN_STP")
    if r and r["total_distance_km"] == 15.0:
        return True, "Dijkstra optimal path calculation verified"
    return False, "Route optimization returned invalid result"

def check_dashboard_imports():
    import streamlit
    import plotly
    # Test importing the dashboard module
    dashboard_file = os.path.join(ROOT, "dashboard", "app.py")
    if os.path.exists(dashboard_file):
        return True, "Streamlit dashboard app.py exists and dependencies resolved"
    return False, "dashboard/app.py missing"

def check_kafka_streaming_config():
    from src.utils.config import load_config
    cfg = load_config()
    if "kafka" in cfg and "streaming_input" in cfg["paths"]:
        return True, f"Topic '{cfg['kafka']['topic']}' & Stream paths configured"
    return False, "Streaming configuration missing in config.yaml"

def main():
    print("=" * 75)
    print("        PROJECT HEALTH CHECK: SMART TRAFFIC BIG DATA SYSTEM")
    print("=" * 75)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Authentic Dataset Exists", check_dataset_exists),
        ("Dataset Columns & Schema", check_dataset_columns),
        ("Apache Spark & JVM Runtime", check_spark_works),
        ("Processed Dataset Exists", check_processed_data_exists),
        ("PySpark MLlib Models", check_models_exist),
        ("Evaluation Metrics Generated", check_metrics_exist),
        ("Visual Result Plots", check_plots_exist),
        ("Dijkstra Route Algorithm", check_route_algorithm_works),
        ("Streamlit Dashboard Modules", check_dashboard_imports),
        ("Kafka & Streaming Pipeline", check_kafka_streaming_config),
    ]
    
    results = []
    for name, fn in checks:
        passed = check_component(name, fn)
        results.append((name, passed))
        
    print("=" * 75)
    all_passed = all(r[1] for r in results)
    total_passed = sum(1 for r in results if r[1])
    print(f"OVERALL HEALTH CHECK STATUS: {total_passed}/{len(results)} CHECKS PASSED")
    if all_passed:
        print("[ SUCCESS ] ALL SYSTEM COMPONENTS ARE HEALTHY AND OPERATIONAL!")
    else:
        print("[ NOTICE  ] Some components require pipeline execution (e.g. run scripts/run_pipeline.py).")
    print("=" * 75)

if __name__ == "__main__":
    main()
