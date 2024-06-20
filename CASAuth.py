import json,requests,hashlib

#接続先情報
CAS_ADDR = 'http://localhost:8080/auth'

def Authenticate(username:str,password:str):
    passwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    headers = {"Content-Type": "application/json"}
    data = {
        "username":username,
        "password":passwd_hash
    }
    jsondata = json.dumps(data)
    res = requests.post(url=CAS_ADDR,data=jsondata,headers=headers)
    print(res.status_code)
    print(res.json())