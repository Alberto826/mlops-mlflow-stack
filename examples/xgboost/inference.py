import requests

#Tensor input format
json={
  "inputs": [
    [4.6, 3.6, 1, 0.2] for x in range(1000)
  ]
}

headers={'Content-type':'application/json'}
res = requests.post('http://models.localhost/iris_xgb/2/invocations', headers=headers, json=json, verify=False)
print(res.content)