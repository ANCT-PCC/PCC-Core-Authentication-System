import requests

url = 'http://localhost:8080/keepalv'
headers = {"Content-Type": "application/json"}
res  = requests.get(url=url,headers=headers)

print(res.status_code)