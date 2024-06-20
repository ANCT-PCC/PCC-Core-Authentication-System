import CASAuth

#実行前に、PCC-CASの管理者用ページで、適当なアカウントを登録しましょう


#PCC-CASに登録しているアカウントで認証をしてみましょう
uname = input('ユーザ名 > ')
passwd = input('パスワード > ')

#ここで認証を行う
status,res = CASAuth.Authenticate(uname,password=passwd)

print(f'status_code: {status}')
print(f'json: {res}')

#CASAuth.Authenticate()は、ステータスコード と 認証結果のjson を返します。
#jsonの中身はこの場合だと res['username'] の形式で取り出せます。

#認証に失敗している場合は、以下のjsonが返ってきます。
#{'login_status': 1, 'username': 'NoUname', 'displayname': 'NoDisplayname', 'post': 'NoPost', 'grade': 'NoGrade', 'mesc': 'NoMESC', 'discord_id': 'NoDiscord'}

#以下、例
print(res['login_status']) #0:成功 1:失敗
print(res['username'])
print(res['grade'])
print(res['mesc'])
print(res['displayname'])
print(res['discord_id'])
print(res['post'])

#これらの情報を、他の基幹システムで使用する形になります。
#たとえば、ユーザ名ごとにアクセストークンを発行して、各自のDBでセッション管理をするなど。
#入退出記録なんかは、認証で得られた情報をもとに「誰が入ってきたのか」をタイムスタンプと一緒にDBで管理すればOK
#認証スピードは、1秒あればおわる。