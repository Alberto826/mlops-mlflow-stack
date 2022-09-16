FROM python:3.7-slim-buster
# Install python packages
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install mlflow boto3 pymysql psycopg2 conda virtualenv

RUN mkdir /mlflow
RUN chmod -R 777 /mlflow

WORKDIR /mlflow

ENTRYPOINT mlflow server \
    --backend-store-uri $BACKEND_STORE_URI \
    # --default-artifact-root $DEFAULT_ARTIFACT_ROOT \
    --artifacts-destination $ARTIFACTS_DESTINATION \
    --serve-artifacts \
    --host 0.0.0.0