from flask import Flask, render_template
import requests
import asyncio
import docker


app = Flask(__name__)
docker_client = docker.from_env()

data={'registered_models': [
    {
        'name': 'iris_xgb', 
        'creation_timestamp': 1662026569871, 
        'last_updated_timestamp': 1662026657342, 
        'latest_versions': [
            {
                'name': 'iris_xgb', 
                'version': '1', 
                'creation_timestamp': 1662026570223, 
                'last_updated_timestamp': 1662026657342, 
                'current_stage': 'Staging', 
                'description': '', 
                'source': 'mlflow-artifacts:/11/cab39c93ea0f49a684d701681688a369/artifacts/iris_xgb', 
                'run_id': 'cab39c93ea0f49a684d701681688a369', 
                'status': 'READY', 
                'run_link': ''
            }
        ]}
    ]}

async def main():
    container = docker_client.services.create(
        image="python:3.7-slim-buster",
        name="iris_xgb",
        networks=["traefik-public"],
        env=[],
        labels={},
    )

asyncio.run(main())

@app.route("/")
def index():
    # data = requests.get('http://mlflow:5000/api/2.0/preview/mlflow/registered-models/list').json()
    return render_template('index.html', data=data)