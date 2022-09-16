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

def run_container(name, version):
    full_name=f"{name}-v{version}"
    container = docker_client.containers.run(
            image="mlflow_server",
            name=full_name,
            network="traefik-public",
            labels={
                "mlflow_model":"true",
                "traefik.enable":"true",
                "traefik.docker.network":"traefik-public",
                "traefik.http.routers.models-http.rule":f"Host(`models.localhost`) && PathPrefix(`/{name}/{version}`)",
                "traefik.http.routers.models-http.entrypoints":"http",
                "traefik.http.routers.models-http.middlewares":"https-redirect",
                "traefik.http.routers.models-https.rule":f"Host(`models.localhost`) && PathPrefix(`/{name}/{version}`)",
                "traefik.http.routers.models-https.entrypoints":"https",
                "traefik.http.routers.models-https.tls.certresolver":"le",
                "traefik.http.services.models.loadbalancer.server.port":"5000",
            },
            # command=f'mlflow models serve -m "models:/{name}/{version}"',
            entrypoint=f'pip install virtualenv & mlflow models serve -m "models:/{name}/{version}" --env-manager virtualenv',
            # command=f'mlflow models serve --help',
            # entrypoint=f'mlflow models serve --help',
            detach=True,
            environment={
                "MLFLOW_TRACKING_URI":"http://mlflow:5000",
                "MLFLOW_TRACKING_INSECURE_TLS":"true"
            },
        )

def load_model(name, version, source):
    full_name=f"{name}-v{version}"
    try:
        cont = docker_client.containers.get(full_name)
        if cont.status in ["exited","created"]:
            print(f"Container {full_name} | Status: {cont.status}")
            print(f"Starting container {full_name}....")
            cont.remove()
            run_container(name, version)
            print(f"Container {full_name} | Status: {cont.status}")
    except docker.errors.NotFound:
        run_container(name, version)

async def main():
    data = requests.get('https://mlflow.localhost/api/2.0/preview/mlflow/registered-models/list', verify=False).json()
    for i, model in enumerate(data.get("registered_models")):
        for v in model.get("latest_versions"):
            load_model(v.get("name"), v.get("version"), v.get("source"))


asyncio.run(main())

@app.route("/")
def index():
    # data = requests.get('http://mlflow:5000/api/2.0/preview/mlflow/registered-models/list').json()
    data2 = requests.get('https://mlflow.localhost/api/2.0/preview/mlflow/registered-models/list', verify=False).json()
    return render_template('index.html', data=data2)