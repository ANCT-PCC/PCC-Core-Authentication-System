import requests

url = 'http://pcc-cas.nemnet-lab.net/keepalv'
headers = {"Content-Type": "application/json"}
res  = requests.get(url=url,headers=headers)

print(res.status_code)