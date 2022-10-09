from flask import Flask, render_template
import requests
import asyncio
import os
from dotenv import load_dotenv
import mlflow
load_dotenv()

os.environ['MLFLOW_TRACKING_INSECURE_TLS'] = 'true'
mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
client = mlflow.MlflowClient()


app = Flask(__name__)

def deploy_stack(name, version, stack_id=None, method='post'):
    full_name=f"{name}-v{version}"
    compose=f'''
    version: "3.8"
    services:
        {full_name}:
            image: mlflow_server
            entrypoint: mlflow models serve -m "models:/{name}/{version}" -h 0.0.0.0
            networks:
                - traefik-public
            environment:
                - MLFLOW_TRACKING_URI=${"{MLFLOW_TRACKING_URI}"}
                - MLFLOW_TRACKING_INSECURE_TLS=${"{MLFLOW_TRACKING_INSECURE_TLS}"}
            labels:
                - traefik.enable=true
                - traefik.docker.network=traefik-public
                - traefik.constraint-label=traefik-public
                - traefik.http.middlewares.{full_name}.stripprefix.prefixes=/{name}/{version}
                - traefik.http.routers.{full_name}-http.rule=Host(`{os.environ['MLDEPLOY_DOMAIN']}`) && (PathPrefix(`/{name}/{version}`) || PathPrefix(`/v2/models/{name}/versions/{version}`))
                - traefik.http.routers.{full_name}-http.entrypoints=http
                - traefik.http.routers.{full_name}-http.middlewares=https-redirect
                - traefik.http.routers.{full_name}-http.middlewares={full_name}
                - traefik.http.routers.{full_name}-https.middlewares={full_name}
                - traefik.http.routers.{full_name}-https.rule=Host(`{os.environ['MLDEPLOY_DOMAIN']}`) && (PathPrefix(`/{name}/{version}`) || PathPrefix(`/v2/models/{name}/versions/{version}`))
                - traefik.http.routers.{full_name}-https.entrypoints=https
                - traefik.http.routers.{full_name}-https.tls.certresolver=le
                - traefik.http.services.{full_name}.loadbalancer.server.port=5000
    networks:
        traefik-public:
            external: true
    '''
    headers = {"X-API-Key": os.environ['PORTAINER_ACCESS_TOKEN']}
    compose_str={
        "env":[
            {"name":"MLFLOW_TRACKING_URI","value": os.environ['MLFLOW_TRACKING_URI']},
            {"name":"MLFLOW_TRACKING_INSECURE_TLS","value":"true"}
        ],
        "name": f"{full_name}",
        "stackFileContent": compose
    }
    if method=='post':
        params={"type":2,"method":"string","endpointId":os.environ['PORTAINER_ENDPOINTID']}
        res = requests.post(f"{os.environ['PORTAINER_API_URI']}/stacks", headers=headers, params=params, json=compose_str)
        print('Portainer Stack response POST', res.json())
    if method=='put':
        params={"endpointId":os.environ['PORTAINER_ENDPOINTID']}
        res = requests.put(f"{os.environ['PORTAINER_API_URI']}/stacks/{stack_id}", headers=headers, params=params, json=compose_str)
        print('Portainer Stack response PUT', res.json())
    if method=='delete':
        params={"endpointId":os.environ['PORTAINER_ENDPOINTID']}
        res = requests.delete(f"{os.environ['PORTAINER_API_URI']}/stacks/{stack_id}", headers=headers, params=params, json=compose_str)
        print('Portainer Stack response DELETE', res.json())
    return res.json()

def deploy_model(name, version, source=None):
    full_name=f"{name}-v{version}"
    headers = {"X-API-Key": os.environ['PORTAINER_ACCESS_TOKEN']}
    response = requests.get(f"{os.environ['PORTAINER_API_URI']}/stacks", headers=headers)
    if response.status_code==200:
        stacks = response.json()
        for stack in stacks:
            print('Stack Name', stack.get('Name'))
            if stack.get('Name')==full_name:
                res=deploy_stack(name, version, stack.get('Id'), method='put')
                return res
        res=deploy_stack(name, version)
    else: res=response.json()
    print(res)
    return res

def remove_model(name, version, source=None):
    full_name=f"{name}-v{version}"
    headers = {"X-API-Key": os.environ['PORTAINER_ACCESS_TOKEN']}
    response = requests.get(f"{os.environ['PORTAINER_API_URI']}/stacks", headers=headers)
    if response.status_code==200:
        stacks = response.json()
        for stack in stacks:
            if stack.get('Name')==full_name:
                res=deploy_stack(name, version, stack.get('Id'), method='delete')
                return res
        res={"message":"model deployment not found"}
    else: res=response.json()
    return res

async def main():
    models = client.search_registered_models()
    res=[]
    for i, model in enumerate(models):
        print('model', model)
        for v in model.latest_versions:
            if v.current_stage in ["Staging","Production"]:
                res.append(deploy_model(v.name, v.version))
            else: remove_model(v.name, v.version)
    return res

@app.route("/")
def index():
    models = client.search_registered_models()
    print(models)
    return models

@app.route("/redeploy")
def redeploy():
    res = asyncio.run(main())
    return res

@app.route("/stacks")
def stacks():
    headers = {"X-API-Key": os.environ['PORTAINER_ACCESS_TOKEN']}
    params={"Name": 'iris_xgb-v1'}
    stack_1 = requests.get(f"{os.environ['PORTAINER_API_URI']}/stacks", headers=headers, params=params)
    params={"Name": 'iris_xgb-v2'}
    stack_2 = requests.get(f"{os.environ['PORTAINER_API_URI']}/stacks", headers=headers, params=params)
    stacks = stack_1.json()
    return stacks