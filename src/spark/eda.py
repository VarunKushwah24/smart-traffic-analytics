import os
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, avg, count, min as sp_min, max as sp_max, stddev, round as sp_round
)
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.logger import setup_logger

logger = setup_logger("SparkEDA")

def run_spark_eda(df: DataFrame, results_dir: str = "results") -> dict:
    """
    Computes distributed Exploratory Data Analysis (EDA) statistics using PySpark SQL.
    Generates summary tables, hourly/daily aggregations, correlation tables, and visual charts.
    """
    metrics_dir = os.path.join(results_dir, "metrics")
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    logger.info("Computing Spark SQL aggregations for EDA...")
    
    # 1. High-level Summary Statistics
    summary_df = df.select(
        "traffic_volume", "average_speed", "occupancy", "temperature_c"
    ).summary("count", "mean", "stddev", "min", "25%", "50%", "75%", "max")
    
    summary_pd = summary_df.toPandas()
    summary_csv = os.path.join(metrics_dir, "summary_statistics.csv")
    summary_pd.to_csv(summary_csv, index=False)
    logger.info(f"Saved numerical summary statistics to: {summary_csv}")
    
    # 2. Hourly Profile Aggregation
    hourly_df = (
        df.groupBy("hour")
        .agg(
            sp_round(avg("traffic_volume"), 1).alias("avg_volume"),
            sp_round(avg("average_speed"), 1).alias("avg_speed"),
            sp_round(avg("occupancy"), 3).alias("avg_occupancy"),
            count("*").alias("record_count")
        )
        .orderBy("hour")
    )
    hourly_pd = hourly_df.toPandas()
    hourly_csv = os.path.join(metrics_dir, "hourly_traffic_profile.csv")
    hourly_pd.to_csv(hourly_csv, index=False)
    
    # 3. Day of Week Profile
    dow_df = (
        df.groupBy("day_of_week")
        .agg(
            sp_round(avg("traffic_volume"), 1).alias("avg_volume"),
            sp_round(avg("average_speed"), 1).alias("avg_speed"),
            count("*").alias("record_count")
        )
        .orderBy("day_of_week")
    )
    dow_pd = dow_df.toPandas()
    dow_csv = os.path.join(metrics_dir, "day_of_week_profile.csv")
    dow_pd.to_csv(dow_csv, index=False)
    
    # 4. Congestion Distribution
    cong_df = (
        df.groupBy("congestion_level")
        .agg(
            count("*").alias("count"),
            sp_round(avg("average_speed"), 1).alias("avg_speed"),
            sp_round(avg("traffic_volume"), 1).alias("avg_volume")
        )
        .orderBy(col("count").desc())
    )
    cong_pd = cong_df.toPandas()
    total_records = cong_pd["count"].sum()
    cong_pd["percentage"] = (cong_pd["count"] / total_records * 100).round(2)
    cong_csv = os.path.join(metrics_dir, "congestion_distribution.csv")
    cong_pd.to_csv(cong_csv, index=False)
    
    # 5. Weather Impact on Traffic
    weather_df = (
        df.groupBy("weather_main")
        .agg(
            count("*").alias("count"),
            sp_round(avg("average_speed"), 1).alias("avg_speed"),
            sp_round(avg("traffic_volume"), 1).alias("avg_volume")
        )
        .orderBy(col("count").desc())
    )
    weather_pd = weather_df.toPandas()
    weather_csv = os.path.join(metrics_dir, "weather_traffic_impact.csv")
    weather_pd.to_csv(weather_csv, index=False)
    
    # 6. Generate Static EDA Plots (for report & documentation)
    _generate_eda_plots(hourly_pd, cong_pd, weather_pd, plots_dir)
    
    logger.info("Spark EDA and chart generation completed successfully.")
    return {
        "summary": summary_pd,
        "hourly": hourly_pd,
        "dow": dow_pd,
        "congestion": cong_pd,
        "weather": weather_pd
    }

def _generate_eda_plots(hourly_pd, cong_pd, weather_pd, plots_dir):
    """Generates and saves publication-quality EDA charts."""
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Plot 1: Hourly Traffic Volume & Speed Profile
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    
    ax1.plot(hourly_pd["hour"], hourly_pd["avg_volume"], color="#1f77b4", marker="o", linewidth=2.5, label="Avg Volume (vph)")
    ax2.plot(hourly_pd["hour"], hourly_pd["avg_speed"], color="#d62728", marker="s", linewidth=2.5, linestyle="--", label="Avg Speed (km/h)")
    
    ax1.set_xlabel("Hour of the Day (00:00 - 23:00)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Traffic Volume (vehicles/hour)", color="#1f77b4", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Average Speed (km/h)", color="#d62728", fontsize=11, fontweight="bold")
    ax1.set_title("Hourly Traffic Dynamics: Volume vs. Average Speed Profile", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xticks(range(0, 24))
    
    fig.tight_layout()
    plot_path1 = os.path.join(plots_dir, "hourly_traffic_profile.png")
    plt.savefig(plot_path1, dpi=300)
    plt.close(fig)
    
    # Plot 2: Congestion Class Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#2ca02c", "#ff7f0e", "#d62728", "#7f7f7f"]
    bars = ax.bar(cong_pd["congestion_level"], cong_pd["count"], color=colors[:len(cong_pd)], edgecolor="black", alpha=0.85)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 50, f"{int(yval):,}", ha='center', va='bottom', fontweight='bold')
    ax.set_title("Distribution of Traffic Congestion Levels", fontsize=13, fontweight="bold")
    ax.set_xlabel("Congestion Level", fontsize=11, fontweight="bold")
    ax.set_ylabel("Record Count", fontsize=11, fontweight="bold")
    fig.tight_layout()
    plot_path2 = os.path.join(plots_dir, "congestion_distribution.png")
    plt.savefig(plot_path2, dpi=300)
    plt.close(fig)

    # Plot 3: Weather Condition Impact
    fig, ax = plt.subplots(figsize=(10, 5))
    top_weather = weather_pd.head(6)
    sns.barplot(data=top_weather, x="weather_main", y="avg_speed", palette="Blues_d", ax=ax)
    ax.set_title("Impact of Adverse Weather on Corridor Average Speed", fontsize=13, fontweight="bold")
    ax.set_xlabel("Weather Condition", fontsize=11, fontweight="bold")
    ax.set_ylabel("Average Speed (km/h)", fontsize=11, fontweight="bold")
    fig.tight_layout()
    plot_path3 = os.path.join(plots_dir, "weather_impact_speed.png")
    plt.savefig(plot_path3, dpi=300)
    plt.close(fig)
