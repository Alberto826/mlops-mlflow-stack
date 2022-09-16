import argparse
import os

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
from mlflow.models.signature import infer_signature
import xgboost as xgb
import matplotlib as mpl


import mlflow
import mlflow.xgboost

os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = 'true'


remote_server_uri = "https://mlflow.localhost" # set to your server URI
mlflow.set_tracking_uri(remote_server_uri)


mpl.use("Agg")


# def parse_args():
#     parser = argparse.ArgumentParser(description="XGBoost example")
#     parser.add_argument(
#         "--learning-rate",
#         type=float,
#         default=0.3,
#         help="learning rate to update step size at each boosting step (default: 0.3)",
#     )
#     parser.add_argument(
#         "--colsample-bytree",
#         type=float,
#         default=1.0,
#         help="subsample ratio of columns when constructing each tree (default: 1.0)",
#     )
#     parser.add_argument(
#         "--subsample",
#         type=float,
#         default=1.0,
#         help="subsample ratio of the training instances (default: 1.0)",
#     )
#     return parser.parse_args()


def main():
    # parse command-line arguments
    # args = parse_args()

    # prepare train and test data
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    

    # enable auto logging
    mlflow.xgboost.autolog()

    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    mlflow.set_experiment("xgboost-example-11")
    with mlflow.start_run():
        print("artifact uri: ", mlflow.get_artifact_uri())
        print("registry uri: ", mlflow.get_registry_uri())
        print("tracking uri: ", mlflow.get_tracking_uri())
        # train model
        params = {
            "objective": "multi:softprob",
            "num_class": 3,
            "learning_rate": 0.2,
            "eval_metric": "mlogloss",
            "colsample_bytree": 0.8,
            "subsample": 0.9,
            "seed": 42,
        }
        model = xgb.train(params, dtrain, evals=[(dtrain, "train")])

        # evaluate model
        y_proba = model.predict(dtest)
        y_pred = y_proba.argmax(axis=1)
        loss = log_loss(y_test, y_proba)
        acc = accuracy_score(y_test, y_pred)

        # log metrics
        mlflow.log_metrics({"log_loss": loss, "accuracy": acc})
        # signature = infer_signature(dtrain, model.predict(dtrain))
        mlflow.xgboost.log_model(model, "iris_xgb")


if __name__ == "__main__":
    main()