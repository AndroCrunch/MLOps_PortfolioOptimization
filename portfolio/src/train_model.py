from models.model import Models
from sklearn.model_selection import GridSearchCV
from skfolio.model_selection import  WalkForward
from skfolio.moments import EmpiricalCovariance, LedoitWolf
from skfolio import RatioMeasure, RiskMeasure
from skfolio.metrics import make_scorer
import os
import pandas as pd
import pickle

### INITIALIZATION OF MODELS
models = Models()
model_stacking = models.give_model_stacking()
benchmark = models.give_benchmark()

### PARAMETER TUNING
cv = WalkForward(train_size=252, test_size=60)
grid_search = GridSearchCV(
    estimator=model_stacking,
    cv=cv,
    n_jobs=-1,
    param_grid={
        "model2__prior_estimator__covariance_estimator": [
            EmpiricalCovariance(),
            LedoitWolf(),
        ],
        "model3__l1_coef": [0.001, 0.1],
        "model4__risk_measure": [
            RiskMeasure.VARIANCE,
            RiskMeasure.GINI_MEAN_DIFFERENCE,
        ],
    },
    scoring=make_scorer(RatioMeasure.CALMAR_RATIO),
)

### TRAINING
# DATA
script_dir = os.path.dirname(__file__)  # get the directory of the current script
processed_data_dir = os.path.join(script_dir, '../data/processed')

X_train = pd.read_csv(os.path.join(processed_data_dir, 'X_train.csv'), index_col=0)
X_test = pd.read_csv(os.path.join(processed_data_dir, 'X_test.csv'), index_col=0)
# fit the model
grid_search.fit(X_train)
model_stacking = grid_search.best_estimator_


### SAVE MODEL ###  
import dill as pickle
script_dir = os.path.dirname(__file__)  # get the directory of the current script
model_dir = os.path.join(script_dir, '../models/')# Define the path to save the model file
model_path = os.path.join(model_dir, 'model.pkl')
benchmark_path = os.path.join(model_dir, 'benchmark.pkl')

# MODEL
with open(model_path, 'wb') as file:
    pickle.dump(model_stacking, file)
print(f"Model saved to {model_path}")
# BENCHMARK
with open(benchmark_path, 'wb') as file:
    pickle.dump(benchmark, file)
print(f"Benchmark saved to {benchmark_path}")

