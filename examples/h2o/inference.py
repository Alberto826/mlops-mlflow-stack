import requests

#Pandas split orient format
json={
  "columns": ["fixed acidity", "volatile acidity", "citric acid", "residual sugar", "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density", "pH", "sulphates", "alcohol"],
  "data": [
    [7, 0.27, 0.36, 20.7, 0.045, 45, 170, 1.001, 3, 0.45, 8.8 ],
    [6.3, 0.3, 0.34, 1.6, 0.049, 14, 132, 0.994, 3.3, 0.49, 9.5],
  ]
}
headers={'Content-type':'application/json'}
res = requests.post('http://models.localhost/wine_quality_h2o/1/invocations', headers=headers, json=json, verify=False)
print(res.content)

#Pandas records orient format
json=[
  {"fixed acidity":7, "volatile acidity":0.27, "citric acid":0.36, "residual sugar":20.7, "chlorides":0.045, "free sulfur dioxide":45, "total sulfur dioxide":170, "density":1.001, "pH":3, "sulphates":0.45, "alcohol":8.8},
  {"fixed acidity":6.3, "volatile acidity":0.3, "citric acid":0.34, "residual sugar":1.6, "chlorides":0.049, "free sulfur dioxide":14, "total sulfur dioxide":132, "density":0.994, "pH":3.3, "sulphates":0.49, "alcohol":9.5},
]
headers={'Content-type':'application/json'}
res = requests.post('http://models.localhost/wine_quality_h2o/1/invocations', headers=headers, json=json, verify=False)
print(res.content)