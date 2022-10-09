import os
import h2o
from h2o.estimators.random_forest import H2ORandomForestEstimator
from mlflow.models.signature import infer_signature
import mlflow
import mlflow.h2o

os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = 'true'
remote_server_uri = "https://mlflow.localhost" # set to your server URI
mlflow.set_tracking_uri(remote_server_uri)

h2o.init()

wine = h2o.import_file("./wine-quality.csv")
r = wine["quality"].runif()
train = wine[r < 0.7]
test = wine[0.3 <= r]


def train_random_forest(ntrees):
    mlflow.set_experiment("h2o-example")
    with mlflow.start_run():
        rf = H2ORandomForestEstimator(ntrees=ntrees)
        train_cols = [n for n in wine.col_names if n != "quality"]
        rf.train(train_cols, "quality", training_frame=train, validation_frame=test)
        mlflow.log_param("ntrees", ntrees)

        mlflow.log_metric("rmse", rf.rmse())
        mlflow.log_metric("r2", rf.r2())
        mlflow.log_metric("mae", rf.mae())
        signature = infer_signature(train[train_cols].as_data_frame(), rf.predict(train[train_cols]).as_data_frame())
        mlflow.h2o.log_model(rf, "model", signature=signature, input_example=train[train_cols].as_data_frame().head(5))
        mlflow.log_artifacts('./','project')

if __name__ == "__main__":
    for ntrees in [1,50,100,200]:
        train_random_forest(ntrees)