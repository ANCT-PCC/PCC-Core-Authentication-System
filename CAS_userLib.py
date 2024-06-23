import json,requests

#PCC-CAS管理者から発行されたシステムトークンを用いて
#PCC-CASに登録されているユーザ情報を取得するために使うプログラムです

#接続先情報
CAS_ADDR = 'https://pcc-cas.nemnet-lab.net/' #リモートサーバ

#PCC-CASからユーザ登録情報をjson形式で取得します
#トークンが違う/鯖落ちの場合は、ステータスコードが200ではありません
#上記の場合と、ユーザ名がヒットしなかった場合は、result変数には空の配列が代入されます。
#result変数内に格納されたユーザ情報は、配列形式です。以下を参考にしてください。
# [ユーザ名,学年,学科,名前,パスワードのハッシュ,メールアドレス,DiscordのID,役職,(ここの値は使わない)]
def getUserInfo(username:str,system_token:str):
    headers = {"Content-Type": "application/json"}
    data = {
        "username":username,
        "system_token":system_token
    }
    jsondata = json.dumps(data)
    res = requests.get(url=CAS_ADDR+'getuserinfo',data=jsondata,headers=headers)

    if res.status_code != 200:
        return res.status_code,[]
    else:
        result = res.json()
        status_code = res.status_code

    return status_code,result

#PCC-CASからすべてのユーザ登録情報をjson形式で取得します
#トークンが違う/鯖落ちの場合は、ステータスコードが200ではありません
#検索にヒットしなかった場合は、result変数に空の配列が代入されます。
#ユーザがPCC-CASに複数登録されている場合は、resultの要素数はその登録数になります。
# -> 要素数は変化するので、毎回len(result) などで要素数を確認してください。
def getAllUserInfo(system_token:str):
    headers = {"Content-Type": "application/json"}
    data = {
        "system_token":system_token
    }
    jsondata = json.dumps(data)
    res = requests.get(url=CAS_ADDR+'getalluserinfo',data=jsondata,headers=headers)

    if res.status_code != 200:
        return res.status_code,[]
    else:
        result = res.json()
        status_code = res.status_code

    return status_code,result