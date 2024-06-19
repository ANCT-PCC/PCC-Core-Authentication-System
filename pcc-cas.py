from flask import Flask, redirect,render_template,request,make_response,send_file
from flask_httpauth import HTTPDigestAuth
import dbc
import random,string
import json
import hashlib
import datetime
import userSubmit

TOKEN_SIZE = 64 #トークンのサイズ
COOKIE_AGE = 0.5 #Cookieの有効期限(単位:h)
VERSION = 'ver 1.0'

#DB接続開始
conn = dbc.startConnection()

#初期化処理
def init(conn):
    #すべてのトークンを無効化
    command='''UPDATE pcc_users SET setting_token = "NoToken" WHERE setting_token != "NoToken"'''
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(dbc.INIT_SQL_COMMAND)
    conn.commit()
    c.close()
    res = dbc.sqlExecute(conn,command)
    print(f"\nアクセストークン初期化を実行\n")
    print(f"Response: {res}\n\n")

#ランダムトークン生成
def randomname(TOKEN_SIZE):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=TOKEN_SIZE))

app = Flask(__name__)
app.config['SECRET_KEY'] = randomname(TOKEN_SIZE)
auth = HTTPDigestAuth()

#adminのBasic認証情報設定ファイルがあるか
try:
    with open('setting_files/admin_info.json','r',encoding='utf-8') as f:
     Admin = json.load(f)

except FileNotFoundError:
    print("[PCC-CAS] ERROR: setting_files/admin_info.json NOT FOUND.")
    exit()

@auth.get_password
def get_pw(id):
    return Admin.get(id)

@app.route('/',methods=['GET'])
def index():
    token = request.cookies.get('token')
    uname = request.cookies.get('uname')
    displayname = request.cookies.get('displayname')
    if token is None or uname is None or displayname is None:
        return redirect('/login')
    else:
        pwchangeFlag = dbc.ckpwdchange(conn,uname=uname)
        if pwchangeFlag == 1:
            return redirect('/pwdchange')
        uname,login_status = dbc.cktoken(conn,uname,token)
        if login_status == 3: #ログイン状態である
            return render_template('index.html',uname = displayname,ver=VERSION)
        elif login_status == 1 or login_status == 2:
            return redirect('/login')
        
@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico')
    

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        res = request.json[0]
        uname = res['uname']
        passwd = hashlib.sha256(res['passwd'].encode("utf-8")).hexdigest()
        
        uinfo = dbc.search_userinfo_from_name(conn,uname)
        if len(uinfo) != 0:
            if(uinfo[0][4] == passwd):
                passwd_flag = True
            else:
                passwd_flag = False

            if passwd_flag == True: #パスワードがあっている
                token = randomname(TOKEN_SIZE=TOKEN_SIZE) #一意のトークン
                displayname = dbc.search_userinfo_from_name(conn,uname)[0][3]
                res = make_response(redirect('/'))
                expires = int(datetime.datetime.now().timestamp()) + 60*60*COOKIE_AGE
                res.set_cookie('token', token,expires=expires)
                res.set_cookie('uname', uname,expires=expires)
                res.set_cookie('displayname',displayname,expires=expires)
                
                #DBに新しいトークンを上書きと同時に
                #サブプロセスでタイマーを作動
                dbc.update_token(conn,uname,token)

            else:
                token="Nodata"
                uname="Nodata"
                return "444",444
        else:
            token="Nodata"
            uname="Nodata"
            if res == "Nodata" or token is None or res is None:

                return "444",444 #ログインエラーのレス
            else:
                uname , login_sta = dbc.cktoken(conn,uname,str(token))
                
                if(login_sta == 3):
                    pass
                elif(uname == "Not Submit"):
                    return "446",446 #ユーザ登録なし
                elif(login_sta == 2):
                    #return "445",445 #トークンが無効
                    pass
                
        return res
    
    elif request.method == 'GET':
        uname = request.cookies.get('uname')
        token = request.cookies.get('token')
        if token is None:
            return render_template('login.html')
        else:
            uname,login_sta = dbc.cktoken(conn,uname,token)
            if login_sta == 1 or login_sta==2 or login_sta==0:
                return render_template('login.html')
            elif login_sta == 3:
                return redirect('/')
            
@app.route('/pwdchange')
def pwdchange():
    uname = request.cookies.get('uname')
    token = request.cookies.get('token')
    displayname = request.cookies.get('displayname')

    uname,login_status = dbc.cktoken(conn,uname,token)
    if login_status != 3:
        return redirect('/login')
    else:
        return render_template('passwd_change.html',uname=displayname,ver=VERSION)

@app.after_request
def set_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Method'] = 'GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS'  # noqa: E501
    response.headers['Access-Control-Allow-Headers'] = 'Content-type,Accept,X-Custom-Header'  # noqa: E501
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@app.route('/logout')
def logout():
    uname=request.cookies.get('uname')
    res=make_response(redirect('/login'))
    res.delete_cookie('token')
    res.delete_cookie('uname')
    res.delete_cookie('displayname')
    dbc.update_token(conn,uname,'NoToken')

    return res

@app.route('/user_settings',methods=['GET','POST'])
def user_settings():

    if request.method == 'POST':
        uname = request.cookies.get('uname')
        token = request.cookies.get('token')

        uname,login_status = dbc.cktoken(conn,uname,token)
        if login_status != 3:
            return redirect('/login')
        else:
            currentPWD = hashlib.sha256(request.json[0]['currentPWD'].encode("utf-8")).hexdigest()
            newPWD = hashlib.sha256(request.json[0]['newPWD'].encode("utf-8")).hexdigest()

            uinfo = dbc.search_userinfo_from_name(conn,uname)
            if uinfo[0][4] != currentPWD:
                return "444",444
            elif uinfo[0][4] == currentPWD:
                #パスワード変更処理
                dbc.update_user_info(conn,uname,'passwd',newPWD)
                return "415",415


    else:

        uname = request.cookies.get('uname')
        token = request.cookies.get('token')
        displayname = request.cookies.get('displayname')

        uname,login_status = dbc.cktoken(conn,uname,token)
        if login_status != 3:
            return redirect('/login')
        else:
            return render_template('user_settings.html',uname=displayname,ver=VERSION)
        
@app.route('/user_settings_discord',methods=['POST'])
def user_settings_discord():
    
    uname = request.cookies.get('uname')
    token = request.cookies.get('token')

    uname,login_status = dbc.cktoken(conn,uname,token)
    if login_status != 3:
        return redirect('/login')
    else:
        newDiscord = request.json[0]['newDiscord']
        #Discordのユーザ名変更処理
        dbc.update_user_info(conn,uname,'discord',newDiscord)
        return "OK",200
    
#部員一覧
@app.route('/members')
def members():
    uname = request.cookies.get('uname')
    token = request.cookies.get('token')
    displayname = request.cookies.get('displayname')

    uname,login_status = dbc.cktoken(conn,uname,token)
    if login_status != 3:
        return redirect('/login')
    else:
        return render_template('members.html',uname=displayname,ver=VERSION)
    
@app.route('/show_members')
def show_members():
    uname = request.cookies.get('uname')
    token = request.cookies.get('token')

    uname,login_status = dbc.cktoken(conn,uname,token)
    if login_status != 3:
        return redirect('/login')
    else:
        res = dbc.get_all_users(conn)
        member_info = []

        for flag in range(len(res)):
            dict = {}
            dict['displayname']=str(res[flag][3])
            dict['uname']=str(res[flag][0])
            dict['grade']=str(res[flag][1])
            dict['class']=str(res[flag][2])
            dict['discord']=str(res[flag][6])
            dict['post'] = str(res[flag][7])
            member_info.append(dict)

        return json.dumps(member_info)
        
@app.route('/admintools')
@auth.login_required
def admintools_top():
    return redirect('/admintools/top')

@app.route('/admintools/<string:page>')
@auth.login_required
def admintools(page):
    return render_template('admintools/'+page+'.html',ver=VERSION)

@app.route('/admintools/submitusers/<string:mode>',methods=['POST'])
@auth.login_required
def submitusers(mode):
    if mode == 'submit':
        submit_contents = str(request.json['content'])
        with open('userList.csv','w',encoding='utf-8') as f:
            f.write(submit_contents)

        userSubmit.userSubmit(conn)
        return "OK"
    elif mode == 'delete':
        delete_contents = str(request.json['content'])
        with open('deluserList.csv','w',encoding='utf-8') as f:
            f.write(delete_contents)
        
        userSubmit.userDelete(conn)
        return "OK"
    
@app.route('/admintools/db/sqlexecute',methods=['POST'])
@auth.login_required
def sqlexecute():
    sqlcmd = str(request.json['sqlcmd'])
    result = dbc.sqlExecute(conn,sqlcmd)
    data = {'content':result}
    print(data['content'])
    return data['content'],200


init(conn)
print("Access: http://localhost:8080/")
app.run(port=8080,host="0.0.0.0",debug=True,threaded=True)