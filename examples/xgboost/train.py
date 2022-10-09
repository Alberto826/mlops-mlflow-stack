import os
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import xgboost as xgb
import matplotlib as mpl
import mlflow
import mlflow.xgboost

os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = 'true'
remote_server_uri = "https://mlflow.localhost" # set to your server URI
mlflow.set_tracking_uri(remote_server_uri)

mpl.use("Agg")

def main():
    # prepare train and test data
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    mlflow.set_experiment("xgboost-example")
    with mlflow.start_run():
        # enable auto logging
        mlflow.xgboost.autolog(log_input_examples=True)
        # train model
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        print("artifact uri: ", mlflow.get_artifact_uri())
        print("registry uri: ", mlflow.get_registry_uri())
        print("tracking uri: ", mlflow.get_tracking_uri())
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
        # log project files
        mlflow.log_artifacts('./','project')

if __name__ == "__main__":
    main()