import CASAuth

uname = input('ユーザ名 > ')
passwd = input('パスワード > ')

status,res = CASAuth.Authenticate(uname,password=passwd)

print(f'status_code: {status}')
print(f'json: {res}')

#CASAuth.Authenticate()は、ステータスコード と 認証結果のjson を返します。
#jsonの中身はこの場合だと res['username'] の形式で取り出せます。

#例
print(res['username'])
print(res['grade'])
print(res['mesc'])
print(res['displayname'])
print(res['discord_id'])
print(res['post'])