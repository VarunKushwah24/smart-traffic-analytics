import os
import sys
from pyspark.sql import SparkSession
from src.utils.logger import setup_logger

logger = setup_logger("SparkSessionBuilder")

def get_spark_session(app_name: str = "SmartTrafficAnalytics", master: str = "local[*]") -> SparkSession:
    """
    Creates and returns a tuned, Windows-compatible SparkSession.
    Configures Python executable paths and networking settings to avoid
    Windows socket timeout issues and unnecessary logging noise.
    """
    # Force PySpark to use the current Python interpreter in the virtual environment
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    
    # Configure HADOOP_HOME for Windows to enable native file writing / winutils
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    hadoop_dir = os.path.join(project_root, "hadoop")
    if os.path.exists(hadoop_dir):
        os.environ["HADOOP_HOME"] = hadoop_dir
        os.environ["hadoop.home.dir"] = hadoop_dir
        bin_dir = os.path.join(hadoop_dir, "bin")
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + ";" + os.environ.get("PATH", "")
    
    # Define local spark warehouse directory inside the project root
    warehouse_dir = os.path.join(project_root, "spark-warehouse")
    os.makedirs(warehouse_dir, exist_ok=True)
    
    logger.info("Initializing Apache Spark Session...")
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.warehouse.dir", warehouse_dir)
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.driver.memory", "2g")
        .config("spark.ui.enabled", "false")
    )
    
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    logger.info(f"SparkSession active: version {spark.version}, Master: {master}")
    return spark
