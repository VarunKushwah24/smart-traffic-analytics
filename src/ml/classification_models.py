from pyspark.ml.classification import (
    LogisticRegression,
    DecisionTreeClassifier,
    RandomForestClassifier,
    GBTClassifier,
    NaiveBayes,
    OneVsRest
)
from src.utils.logger import setup_logger

logger = setup_logger("ClassificationModels")

def get_classification_models(
    features_col: str = "features",
    label_col: str = "congestion_numeric",
    random_seed: int = 42
) -> dict:
    """
    Initializes 5 PySpark MLlib classification models:
      1. Multinomial Logistic Regression
      2. Decision Tree Classifier
      3. Random Forest Classifier
      4. Gradient-Boosted Trees (wrapped in OneVsRest for multiclass support)
      5. Naive Bayes (Gaussian / Multinomial compatible)
      
    Returns:
      Dictionary mapping model name to configured PySpark Estimator
    """
    logger.info("Configuring 5 PySpark MLlib classification algorithms...")
    
    # 1. Multinomial Logistic Regression
    lr = LogisticRegression(
        featuresCol=features_col,
        labelCol=label_col,
        maxIter=50,
        regParam=0.01,
        elasticNetParam=0.0,
        family="multinomial"
    )
    
    # 2. Decision Tree Classifier
    dt = DecisionTreeClassifier(
        featuresCol=features_col,
        labelCol=label_col,
        maxDepth=7,
        seed=random_seed
    )
    
    # 3. Random Forest Classifier
    rf = RandomForestClassifier(
        featuresCol=features_col,
        labelCol=label_col,
        numTrees=20,
        maxDepth=6,
        seed=random_seed
    )
    
    # 4. Gradient-Boosted Trees (OneVsRest wrapper enables multiclass classification in PySpark)
    gbt_base = GBTClassifier(
        featuresCol=features_col,
        labelCol=label_col,
        maxIter=10,
        maxDepth=4,
        seed=random_seed
    )
    gbt_ovr = OneVsRest(
        featuresCol=features_col,
        labelCol=label_col,
        classifier=gbt_base
    )
    
    # 5. Naive Bayes Classifier (Gaussian modelType for continuous scaled traffic features)
    nb = NaiveBayes(
        featuresCol=features_col,
        labelCol=label_col,
        modelType="gaussian"
    )
    
    models = {
        "LogisticRegression": lr,
        "DecisionTreeClassifier": dt,
        "RandomForestClassifier": rf,
        "GBTClassifier": gbt_ovr,
        "NaiveBayes": nb
    }
    
    logger.info(f"Initialized {len(models)} classification models: {list(models.keys())}")
    return models
