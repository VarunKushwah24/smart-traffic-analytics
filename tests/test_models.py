import pytest
from src.spark.spark_session import get_spark_session
from src.ml.classification_models import get_classification_models
from src.ml.regression_models import get_regression_models

@pytest.fixture(scope="session")
def spark():
    spark_session = get_spark_session("PyTest_ML")
    yield spark_session
    spark_session.stop()

def test_five_classification_models_instantiated(spark):
    models = get_classification_models(features_col="features", label_col="congestion_numeric")
    assert len(models) == 5
    assert "LogisticRegression" in models
    assert "DecisionTreeClassifier" in models
    assert "RandomForestClassifier" in models
    assert "GBTClassifier" in models
    assert "NaiveBayes" in models

def test_regression_models_instantiated(spark):
    models = get_regression_models(features_col="features", label_col="average_speed")
    assert len(models) >= 2
    assert "LinearRegression" in models
    assert "RandomForestRegressor" in models
    assert "GBTRegressor" in models
