import requests,json

data = {
    "uname": "s203120",
    "passwd":"Minecraft7010"
}

jsondata = json.dumps(data)
res = requests.post("https://pcc-rent.nemnet-lab.net/login",data=jsondata,headers={"Content-Type": "application/json"})

print(f"SPEED:{res.elapsed.total_seconds()}")