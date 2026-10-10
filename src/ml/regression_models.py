from pyspark.ml.regression import (
    LinearRegression,
    RandomForestRegressor,
    GBTRegressor
)
from src.utils.logger import setup_logger

logger = setup_logger("RegressionModels")

def get_regression_models(
    features_col: str = "features",
    label_col: str = "average_speed",
    random_seed: int = 42
) -> dict:
    """
    Initializes PySpark MLlib regression models for continuous speed/volume prediction:
      1. Linear Regression
      2. Random Forest Regressor
      3. Gradient-Boosted Tree (GBT) Regressor
    """
    logger.info(f"Configuring PySpark MLlib regression algorithms for '{label_col}'...")
    
    # 1. Linear Regression
    lr = LinearRegression(
        featuresCol=features_col,
        labelCol=label_col,
        maxIter=50,
        regParam=0.1,
        elasticNetParam=0.2
    )
    
    # 2. Random Forest Regressor
    rf = RandomForestRegressor(
        featuresCol=features_col,
        labelCol=label_col,
        numTrees=25,
        maxDepth=7,
        seed=random_seed
    )
    
    # 3. GBT Regressor
    gbt = GBTRegressor(
        featuresCol=features_col,
        labelCol=label_col,
        maxIter=25,
        maxDepth=5,
        seed=random_seed
    )
    
    models = {
        "LinearRegression": lr,
        "RandomForestRegressor": rf,
        "GBTRegressor": gbt
    }
    
    logger.info(f"Initialized {len(models)} regression models.")
    return models
