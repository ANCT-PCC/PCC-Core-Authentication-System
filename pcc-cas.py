from flask import Flask, redirect,render_template,request,make_response,send_file,Response
from flask_httpauth import HTTPDigestAuth
import dbc
import random,string
import json
import hashlib
import datetime
import userSubmit

TOKEN_SIZE = 64 #トークンのサイズ
COOKIE_AGE = 0.5 #Cookieの有効期限(単位:h)
VERSION = 'ver 1.3.2' #バージョン情報

class Worker:
    def __init__(self):
        self.name = None
        self.class_name = None
        self.disc = None

class Member:
    def __init__(self):
        self.grade5 = None
        self.grade4 = None
        self.grade3 = None
        self.grade2 = None
        self.grade1 = None
        self.all = None

#DB接続開始
conn = dbc.startConnection()
if conn is None:
    print("[PCC-CAS] ERROR: DB Connection Failed.")
    exit()
#connauth = dbc.startAuthConnection()

#初期化処理
def init(conn):
    #すべてのトークンを無効化
    command='''UPDATE pcc_users SET setting_token = "NoToken" WHERE setting_token != "NoToken"'''
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(dbc.INIT_SQL_COMMAND)
    conn.commit()
    c.execute(dbc.INIT_SQL_COMMAND_2)
    conn.commit()
    c.execute(dbc.INIT_SQL_COMMAND_3)
    conn.commit()
    c.execute(dbc.INIT_SQL_COMMAND_4)
    conn.commit()
    c.execute(dbc.INIT_SQL_COMMAND_5)
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

@app.route('/submit')
def submit():
    return render_template('submit.html')

@app.route('/submit/veryfi_inputs',methods=['POST'])
def record_inputs():
    #フォーム入力内容の取得
    json_data = request.json[0]
    user_grade = json_data['grade']
    user_class = json_data['class'] 
    user_number = json_data['number']
    firstname = json_data['firstname']
    lastname = json_data['lastname']
    passwd = json_data['password']
    discord = json_data['discord_id']
    #フォーム入力情報のIDを生成。
    #これをもとにフォーム入力内容の確認と部員登録を行う。
    form_id = randomname(TOKEN_SIZE=TOKEN_SIZE)
    #DBに入力内容を一時的に登録
    dbc.save_form_inputs(conn,form_id=form_id,user_grade=user_grade,user_class=user_class,user_number=user_number,firstname=firstname,lastname=lastname,passwd=passwd,discord=discord)
    #フォーム入力情報のIDを返す。
    data = [{'form_id':form_id}]
    return Response(response=json.dumps(data), status=200, mimetype='application/json')

@app.route('/submit/veryfi_inputs/<string:form_id>',methods=['GET'])
def veryfi_inputs(form_id:str):
    #form_idから、DBに登録されたフォーム入力情報を取得
    res = dbc.get_form_inputs(conn,form_id=form_id)
    #form_idがDBに存在しない場合は、エラー画面を返す。
    if len(res) == 0:
        return render_template('error.html')
    #取得した情報を、html内の各変数に設定してhtmlを返す。
    user_grade = res[0][1]
    user_class = res[0][2]
    user_number = res[0][3]
    firstname = res[0][4]
    lastname = res[0][5]
    discord = res[0][7]
    #パスワードは表示しない
    return render_template('submit_veryfi.html',user_grade=user_grade,user_class=user_class,user_number=user_number,firstname=firstname,lastname=lastname,passwd='非表示',discord=discord)

@app.route('/submit/setup/<string:form_id>',methods=['GET'])
def submit_startup(form_id:str):
    res = dbc.get_form_inputs(conn,form_id=form_id)
    #form_idがDBに存在しない場合は、エラー画面を返す。
    if len(res) == 0:
        return render_template('error.html')
    
    #取得したフォーム内容を、pcc_usersテーブルに登録
    user_grade = res[0][1]
    user_class = res[0][2]
    user_number = res[0][3]
    firstname = res[0][4]
    lastname = res[0][5]
    passwd = res[0][6]
    discord = res[0][7]
    #ユーザ名を生成
    current_year = datetime.datetime.now().year % 100

    #学科名をアルファベットに変換
    if user_class == 'M' or user_class == 'm' or user_class == '機械システム工学科':
        user_class = 'M'
    elif user_class == 'E' or user_class == 'e' or user_class == '電気情報工学科':
        user_class = 'E'
    elif user_class == 'S' or user_class == 's' or user_class == 'システム制御情報工学科':
        user_class = 'S'
    elif user_class == 'C' or user_class == 'c' or user_class == '物質化学工学科':
        user_class = 'C'
    elif user_class == 'A' or user_class == 'a' or user_class == '生産システム工学専攻':
        user_class = 'A' #専攻
    elif user_class == 'P' or user_class == 'p' or user_class == '応用化学専攻':
        user_class = 'P' #専攻

    class_number = None #学科番号
    if user_class == 'M':
        class_number = '11'
    elif user_class == 'E':
        class_number = '21'
    elif user_class == 'S':
        class_number = '31'
    elif user_class == 'C':
        class_number = '41'
    
    uname = str(user_class.lower()) + str(current_year) + str(class_number) + str(user_number)
    email = uname + '@edu.asahikawa-nct.ac.jp'

    #pcc_usersテーブルにユーザを登録
    dbc.create_new_user_from_form(conn,uname=uname,grade=user_grade,mesc=user_class,displayname=firstname+' '+lastname,passwd=passwd,email=email,discord=discord,post='0')
    return render_template('submit_complete.html',uname=uname)

@app.route('/submit/entry_keyword',methods=['POST'])
def check_entry_keyword():
    #入部のあいことば
    entry_keyword = 'ふぉれすとりばあ'
    if (entry_keyword == request.json[0]['entry_keyword']):
        return "OK",200
    else:
        return "NG",444
    
@app.route('/leave_pcc',methods=['GET','POST'])
def leave_pcc():
    if request.method == 'GET':
        uname = request.cookies.get('uname')
        token = request.cookies.get('token')
        displayname = request.cookies.get('displayname')

        uname,login_status = dbc.cktoken(conn,uname,token)
        if login_status != 3:
            return redirect('/login')
        else:
            return render_template('leave_pcc.html',uname=displayname,ver=VERSION)
    elif request.method == 'POST':
        uname = request.cookies.get('uname')
        token = request.cookies.get('token')
        displayname = request.cookies.get('displayname')

        uname,login_status = dbc.cktoken(conn,uname,token)
        if login_status != 3:
            return redirect('/login')
        else:
            #パスワードの確認
            currentPWD = hashlib.sha256(request.json[0]['password'].encode("utf-8")).hexdigest()
            uinfo = dbc.search_userinfo_from_name(conn,uname)
            if uinfo[0][4] != currentPWD:
                return "incorrect password",401
            #退部処理

            dbc.delete_user(conn,uname)
            res=make_response(redirect('/login'))
            res.delete_cookie('token')
            res.delete_cookie('uname')
            res.delete_cookie('displayname')
            return res,200


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
        member_info = [] #json生成用
        users = [[[] for _ in range(4)] for _ in range(5)]
        mecanical = {}
        electnical = {}
        system = {}
        chemical = {}
        
        for flag in range(len(res)): #部員の数だけループ
            mecanical = {}
            electnical = {}
            system = {}
            chemical = {}
            
            if res[flag][1] == '1' :
                if res[flag][10] == '11':
                    mecanical['displayname']=str(res[flag][3])
                    mecanical['uname']=str(res[flag][0])
                    mecanical['grade']=str(res[flag][1])
                    mecanical['class']=str(res[flag][2])
                    mecanical['discord']=str(res[flag][6])
                    mecanical['post'] = str(res[flag][7])

                    users[0][0].append(mecanical)
                

                elif res[flag][10] == '21':
                    electnical['displayname']=str(res[flag][3])
                    electnical['uname']=str(res[flag][0])
                    electnical['grade']=str(res[flag][1])
                    electnical['class']=str(res[flag][2])
                    electnical['discord']=str(res[flag][6])
                    electnical['post'] = str(res[flag][7])

                    users[0][1].append(electnical)

                elif res[flag][10] == '31':
                    system['displayname']=str(res[flag][3])
                    system['uname']=str(res[flag][0])
                    system['grade']=str(res[flag][1])
                    system['class']=str(res[flag][2])
                    system['discord']=str(res[flag][6])
                    system['post'] = str(res[flag][7])
                    
                    users[0][2].append(system)

                elif res[flag][10] == '41':
                    chemical['displayname']=str(res[flag][3])
                    chemical['uname']=str(res[flag][0])
                    chemical['grade']=str(res[flag][1])
                    chemical['class']=str(res[flag][2])
                    chemical['discord']=str(res[flag][6])
                    chemical['post'] = str(res[flag][7])
                
                    users[0][3].append(chemical)

            elif res[flag][1] == '2' :
                if res[flag][10] == '11':
                    mecanical['displayname']=str(res[flag][3])
                    mecanical['uname']=str(res[flag][0])
                    mecanical['grade']=str(res[flag][1])
                    mecanical['class']=str(res[flag][2])
                    mecanical['discord']=str(res[flag][6])
                    mecanical['post'] = str(res[flag][7])

                    users[1][0].append(mecanical)
                

                elif res[flag][10] == '21':
                    electnical['displayname']=str(res[flag][3])
                    electnical['uname']=str(res[flag][0])
                    electnical['grade']=str(res[flag][1])
                    electnical['class']=str(res[flag][2])
                    electnical['discord']=str(res[flag][6])
                    electnical['post'] = str(res[flag][7])

                    users[1][1].append(electnical)

                elif res[flag][10] == '31':
                    system['displayname']=str(res[flag][3])
                    system['uname']=str(res[flag][0])
                    system['grade']=str(res[flag][1])
                    system['class']=str(res[flag][2])
                    system['discord']=str(res[flag][6])
                    system['post'] = str(res[flag][7])
                    
                    users[1][2].append(system)

                elif res[flag][10] == '41':
                    chemical['displayname']=str(res[flag][3])
                    chemical['uname']=str(res[flag][0])
                    chemical['grade']=str(res[flag][1])
                    chemical['class']=str(res[flag][2])
                    chemical['discord']=str(res[flag][6])
                    chemical['post'] = str(res[flag][7])
                
                    users[1][3].append(chemical)

            elif res[flag][1] == '3' :
                if res[flag][10] == '11':
                    mecanical['displayname']=str(res[flag][3])
                    mecanical['uname']=str(res[flag][0])
                    mecanical['grade']=str(res[flag][1])
                    mecanical['class']=str(res[flag][2])
                    mecanical['discord']=str(res[flag][6])
                    mecanical['post'] = str(res[flag][7])

                    users[2][0].append(mecanical)
                

                elif res[flag][10] == '21':
                    electnical['displayname']=str(res[flag][3])
                    electnical['uname']=str(res[flag][0])
                    electnical['grade']=str(res[flag][1])
                    electnical['class']=str(res[flag][2])
                    electnical['discord']=str(res[flag][6])
                    electnical['post'] = str(res[flag][7])

                    users[2][1].append(electnical)

                elif res[flag][10] == '31':
                    system['displayname']=str(res[flag][3])
                    system['uname']=str(res[flag][0])
                    system['grade']=str(res[flag][1])
                    system['class']=str(res[flag][2])
                    system['discord']=str(res[flag][6])
                    system['post'] = str(res[flag][7])
                    
                    users[2][2].append(system)

                elif res[flag][10] == '41':
                    chemical['displayname']=str(res[flag][3])
                    chemical['uname']=str(res[flag][0])
                    chemical['grade']=str(res[flag][1])
                    chemical['class']=str(res[flag][2])
                    chemical['discord']=str(res[flag][6])
                    chemical['post'] = str(res[flag][7])
                
                    users[2][3].append(chemical)

            if res[flag][1] == '4' :
                if res[flag][10] == '11':
                    mecanical['displayname']=str(res[flag][3])
                    mecanical['uname']=str(res[flag][0])
                    mecanical['grade']=str(res[flag][1])
                    mecanical['class']=str(res[flag][2])
                    mecanical['discord']=str(res[flag][6])
                    mecanical['post'] = str(res[flag][7])

                    users[3][0].append(mecanical)
                

                elif res[flag][10] == '21':
                    electnical['displayname']=str(res[flag][3])
                    electnical['uname']=str(res[flag][0])
                    electnical['grade']=str(res[flag][1])
                    electnical['class']=str(res[flag][2])
                    electnical['discord']=str(res[flag][6])
                    electnical['post'] = str(res[flag][7])

                    users[3][1].append(electnical)

                elif res[flag][10] == '31':
                    system['displayname']=str(res[flag][3])
                    system['uname']=str(res[flag][0])
                    system['grade']=str(res[flag][1])
                    system['class']=str(res[flag][2])
                    system['discord']=str(res[flag][6])
                    system['post'] = str(res[flag][7])
                    
                    users[3][2].append(system)

                elif res[flag][10] == '41':
                    chemical['displayname']=str(res[flag][3])
                    chemical['uname']=str(res[flag][0])
                    chemical['grade']=str(res[flag][1])
                    chemical['class']=str(res[flag][2])
                    chemical['discord']=str(res[flag][6])
                    chemical['post'] = str(res[flag][7])
                
                    users[3][3].append(chemical)
            
            if res[flag][1] == '5' :
                if res[flag][10] == '11':
                    mecanical['displayname']=str(res[flag][3])
                    mecanical['uname']=str(res[flag][0])
                    mecanical['grade']=str(res[flag][1])
                    mecanical['class']=str(res[flag][2])
                    mecanical['discord']=str(res[flag][6])
                    mecanical['post'] = str(res[flag][7])

                    users[4][0].append(mecanical)
                

                elif res[flag][10] == '21':
                    electnical['displayname']=str(res[flag][3])
                    electnical['uname']=str(res[flag][0])
                    electnical['grade']=str(res[flag][1])
                    electnical['class']=str(res[flag][2])
                    electnical['discord']=str(res[flag][6])
                    electnical['post'] = str(res[flag][7])

                    users[4][1].append(electnical)

                elif res[flag][10] == '31':
                    system['displayname']=str(res[flag][3])
                    system['uname']=str(res[flag][0])
                    system['grade']=str(res[flag][1])
                    system['class']=str(res[flag][2])
                    system['discord']=str(res[flag][6])
                    system['post'] = str(res[flag][7])
                    
                    users[4][2].append(system)

                elif res[flag][10] == '41':
                    chemical['displayname']=str(res[flag][3])
                    chemical['uname']=str(res[flag][0])
                    chemical['grade']=str(res[flag][1])
                    chemical['class']=str(res[flag][2])
                    chemical['discord']=str(res[flag][6])
                    chemical['post'] = str(res[flag][7])
                
                    users[4][3].append(chemical)

        #5年生から順に、MESCの順番で部員を整理してmember_infoに追加する
        grade = 5
        mesc = 0
        while grade > 0:
            grade -= 1
            mesc = 0
            while mesc < 4:
                for item in users[grade][mesc]:
                    if users[grade][mesc] != None:
                        member_info.append(item)
                mesc += 1

        return json.dumps(member_info)
    
@app.route('/info')
def show_info():
    uname = request.cookies.get('uname')
    token = request.cookies.get('token')

    uname,login_status = dbc.cktoken(conn,uname,token)
    if login_status != 3:
        return redirect('/login')
    else:
        workers , members = dbc.get_club_information(conn)

        club_leader = Worker()
        club_leader.name = workers[0][0][0]
        club_leader.class_name = workers[0][0][1]+workers[0][0][2]
        club_leader.disc = ''

        club_subleader = Worker()

        for flag in range(len(workers[1])):
            if flag == 0:
                club_subleader.name = workers[1][flag][0]
            else:
                club_subleader.name = club_subleader.name + ','+workers[1][flag][0]

        for flag in range(len(workers[1])):
            if flag == 0:
                club_subleader.class_name = workers[1][flag][1]+workers[1][flag][2]
            else:
                club_subleader.class_name = club_subleader.class_name + ','+workers[1][flag][1]+workers[1][flag][2]
        club_subleader.disc = ''

        casher = Worker()
        for flag in range(len(workers[2])):
            if flag == 0:
                casher.name = workers[2][flag][0]
            else:
                casher.name = casher.name + ','+workers[2][flag][0]

        for flag in range(len(workers[2])):
            if flag == 0:
                casher.class_name = workers[2][flag][1]+workers[2][flag][2]
            else:
                casher.class_name = casher.name + ','+workers[2][flag][1]+workers[2][flag][2]
        casher.disc = ''
        
        admin = Worker()
        for flag in range(len(workers[3])):
            if flag == 0:
                admin.name = workers[3][flag][0]
            else:
                admin.name = admin.name + ','+workers[3][flag][0]

        for flag in range(len(workers[3])):
            if flag == 0:
                admin.class_name = workers[3][flag][1]+workers[3][flag][2]
            else:
                admin.class_name = admin.name + ','+workers[3][flag][1]+workers[3][flag][2]
        admin.disc = ''

        members_count = Member()
        members_count.grade1 = members[0]
        members_count.grade2 = members[1]
        members_count.grade3 = members[2]
        members_count.grade4 = members[3]
        members_count.grade5 = members[4]
        members_count.all = int(members_count.grade5)+int(members_count.grade4)+int(members_count.grade3)+int(members_count.grade2)+int(members_count.grade1)
        return render_template('info.html',ver=VERSION,members=members_count,club_leader=club_leader,club_subleader=club_subleader,casher=casher,admin=admin)
        
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
    return data['content'],200

@app.route('/admintools/db/check_user_exist',methods=['POST'])
@auth.login_required
def check_user_exist():
    uname = request.json['uname']
    print(uname)
    result = dbc.search_userinfo_from_name(conn,uname)
    print(len(result))
    display = result[0][3]
    print(display)
    
    if len(result) == 0:
        return 400
    else:
        return json.dumps({'displayname':display}),200

@app.route('/admintools/db/pw_reset',methods=['POST'])
@auth.login_required
def passwd_reset():
    uname = request.json['uname']
    new_passwd = 'Kusopass@'+uname[-6:]
    print(new_passwd)
    passwd_hash = hashlib.sha256(new_passwd.encode("utf-8")).hexdigest()
    sqlcmd = f'''UPDATE pcc_cas.pcc_users SET passwd = '{passwd_hash}',changedpwd = 'False' WHERE uname = '{uname}' '''
    dbc.sqlExecute(conn,sqlcmd)
    return json.dumps({'new_passwd': new_passwd}),200

@app.route('/auth',methods=['POST'])
def auth():
    
    res = request.json[0]
    system_token = res['system_token']
    uname = res['username']
    passwd_hash = res['password']
    sysTokenFlag = dbc.ckSystemToken(conn,system_token=system_token)

    if sysTokenFlag == True:
        uinfo = dbc.search_userinfo_from_name(conn,uname)
        if len(uinfo) != 0:
            if(uinfo[0][4] == passwd_hash):
                passwd_flag = True
            else:
                passwd_flag = False

            if passwd_flag == True: #パスワードがあっている
                grade = uinfo[0][1]
                mesc = uinfo[0][2]
                displayname = uinfo[0][3]
                discord_id = uinfo[0][6]
                post = uinfo[0][7]
                
                pwdchange = dbc.ckpwdchange(conn,uname)

                if pwdchange == 1:
                    result= {"login_status":2,
                        "username":uname,
                        "displayname":displayname,
                        "post":post,
                        "grade":grade,
                        "mesc":mesc,
                        "discord_id":discord_id
                        }
                    
                else:
                    result = {"login_status":0,
                        "username":uname,
                        "displayname":displayname,
                        "post":post,
                        "grade":grade,
                        "mesc":mesc,
                        "discord_id":discord_id
                        }
            else:
                result = {"login_status":1,
                            "username":'NoUname',
                            "displayname":'NoDisplayname',
                            "post":'NoPost',
                            "grade":'NoGrade',
                            "mesc":'NoMESC',
                            "discord_id":'NoDiscord'
                            }
        else:
            result = {"login_status":1,
                        "username":'NoUname',
                        "displayname":'NoDisplayname',
                        "post":'NoPost',
                        "grade":'NoGrade',
                        "mesc":'NoMESC',
                        "discord_id":'NoDiscord'
                        }
    else:
        result = {"login_status":1,
                  "username":'NoUname',
                  "displayname":'NoDisplayname',
                  "post":'NoPost',
                  "grade":'NoGrade',
                  "mesc":'NoMESC',
                  "discord_id":'NoDiscord'
                  }
        
    json_data = json.dumps(result)
    return json_data,200

#キープアライブ
@app.route('/keepalv')
def keepalv():
    sql = f'''
        INSERT IGNORE INTO {dbc.DB_NAME}.keepalive VALUES('{datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}')
        '''
    res = dbc.sqlExecute(conn,sql)

    return json.dumps({'contents':res}),200

#EULA
@app.route('/eula')
def eula():
    return render_template('eula.html')

#########################################

# 他のシステムからのユーザ関係の情報照会

#########################################

@app.route('/getuserinfo',methods=['GET'])
def getuserinfo():
    uname = request.json['username']
    system_token = request.json['system_token']
    tokenFlag = dbc.ckSystemToken(conn,system_token=system_token)
    if tokenFlag == True:
        res = dbc.search_userinfo_from_name(conn=conn,uname=uname)
        if len(res) == 0:
            return []
        
        uinfo = []
        for i in range(10):
            if i == 4 or i == 8:
                continue
            uinfo.append(res[0][i])

        return json.dumps(uinfo)
    else:
        return None
    
@app.route('/getalluserinfo',methods=['GET'])
def getalluserinfo():
    system_token = request.json['system_token']

    tokenFlag = dbc.ckSystemToken(conn,system_token=system_token)
    if tokenFlag == True:
        res = dbc.get_all_users(conn=conn)
        if len(res) == 0:
            return []
        
        uinfo = [[] for _ in range(len(res))]
        for i in range(len(res)):
            for j in range(10):
                if j == 4 or j == 8:
                    continue
                else:
                    uinfo[i].append(res[i][j])

        return json.dumps(uinfo)
    else:
        return None
    


init(conn)
print("Access: http://localhost:8080/")
app.run(port=8080,host="0.0.0.0",debug=True,threaded=True)