import hashlib
import mysql.connector
import string,random
import datetime

DB_SERVER = 'pcc-cas-db'
#DB_SERVER='127.0.0.1'
DB_NAME = 'pcc_cas'
###############################################
DB_PASSWD = 'Kusopass' #本番環境ではここを変更する
###############################################
TABLE_NAME = 'pcc_users'
TABLE_NAME_TOKEN = 'pcc_systems_token'
TOKEN_SIZE = 64
INIT_SQL_COMMAND = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_NAME} (
    uname VARCHAR(255) NOT NULL PRIMARY KEY,
    grade TEXT,
    mesc TEXT,
    displayname TEXT,
    passwd TEXT,
    email TEXT,
    discord TEXT,
    post TEXT,
    setting_token TEXT,
    changedpwd TEXT,
    class_number TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''
INIT_SQL_COMMAND_2 = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.pcc_systems_token (
    system_name VARCHAR(255) NOT NULL PRIMARY KEY,
    system_token TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''

INIT_SQL_COMMAND_3 = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.keepalive (
    keepalive TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''
INIT_SQL_COMMAND_4 = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.form_inputs (
    form_id VARCHAR(255) NOT NULL PRIMARY KEY,
    grade TEXT,
    class TEXT,
    number TEXT,
    firstname TEXT,
    lastname TEXT,
    password TEXT,
    discord TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''
INIT_SQL_COMMAND_5 = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.deleted_users (
    uname VARCHAR(255) NOT NULL PRIMARY KEY,
    grade TEXT,
    mesc TEXT,
    displayname TEXT,
    deleted_at TEXT,
    email TEXT,
    discord TEXT,
    post TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''

#MySQL接続
def startConnection():
    try:
        conn = mysql.connector.connect(
            host=DB_SERVER,
            user='root',
            password=DB_PASSWD,
            database=DB_NAME,
            port='3306'
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    return conn

#MySQL切断
def closeConnection(conn):
    conn.close()
    

#汎用SQL実行
def sqlExecute(conn,sql:str):
    c = conn.cursor()
    c.execute(sql)
    res = c.fetchall()
    conn.commit()
    c.close()
    return res

#################################################################

#ユーザー関連

#################################################################

#新規登録フォームの内容を一時保存
def save_form_inputs(conn,form_id:str,user_grade:str,user_class:str,user_number:str,firstname:str,lastname:str,passwd:str,discord:str):
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(INIT_SQL_COMMAND_4)
    c.close()
    #テーブルに登録情報を記録
    sql = f'''INSERT IGNORE INTO {DB_NAME}.form_inputs VALUES("{form_id}","{user_grade}","{user_class}","{user_number}","{firstname}","{lastname}","{str(hashlib.sha256(passwd.encode('utf-8')).hexdigest())}","{discord}");'''
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()
    return 0

#新規登録フォームの内容を取得
def get_form_inputs(conn,form_id:str):
    c = conn.cursor()
    c.execute(f'''SELECT * FROM {DB_NAME}.form_inputs WHERE form_id = "{form_id}" ''')
    res = c.fetchall()
    c.close()
    return res #入力内容のレコードを配列として返す

#一時保存した新規登録フォームの内容を削除
def delete_form_inputs(conn,form_id:str):
    c = conn.cursor()
    #ユーザー削除
    c.execute(f'''DELETE FROM {DB_NAME}.form_inputs WHERE form_id = "{form_id}";''')
    conn.commit()
    c.close()
    return

#新規ユーザを作成する
def create_new_user(conn,uname:str,grade:str,mesc:str,displayname:str,passwd:str,email:str,discord:str,post:str):
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(INIT_SQL_COMMAND)
    c.close()
    #役職名を設定
    if post == '0':
        post = 'なし'
    elif post == '1':
        post = '部長'
    elif post == '2':
        post = '副部長'
    elif post == '3':
        post = '会計'
    elif post == '4':
        post = '基幹システム班'
    elif post == '5':
        post = 'システム管理者'
    else:
        post = 'その他の役職'

    #ユーザのクラス番号を判別
    class_number = ''
    if mesc == 'M' or mesc == 'm':
        class_number = '11'
    elif mesc == 'E' or mesc == 'e':
        class_number = '21'
    elif mesc == 'S' or mesc == 's':
        class_number = '31'
    elif mesc == 'C' or mesc == 'c':
        class_number = '41'

    #テーブルに登録情報を記録
    sql = f'''INSERT IGNORE INTO {DB_NAME}.{TABLE_NAME} VALUES("{uname}","{grade}","{mesc}","{displayname}","{str(hashlib.sha256(passwd.encode('utf-8')).hexdigest())}","{email}","{discord}","{post}","NoToken","False","{class_number}");'''
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()
    return 0

#新規ユーザを作成する(登録フォームから。パスワードは元からハッシュ化されているという違いがある)
def create_new_user_from_form(conn,uname:str,grade:str,mesc:str,displayname:str,passwd:str,email:str,discord:str,post:str):
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(INIT_SQL_COMMAND)
    c.close()
    #役職名を設定
    if post == '0':
        post = 'なし'
    elif post == '1':
        post = '部長'
    elif post == '2':
        post = '副部長'
    elif post == '3':
        post = '会計'
    elif post == '4':
        post = '基幹システム班'
    elif post == '5':
        post = 'システム管理者'
    else:
        post = 'その他の役職'

    #ユーザのクラス番号を判別
    class_number = ''
    if mesc == 'M' or mesc == 'm':
        class_number = '11'
    elif mesc == 'E' or mesc == 'e':
        class_number = '21'
    elif mesc == 'S' or mesc == 's':
        class_number = '31'
    elif mesc == 'C' or mesc == 'c':
        class_number = '41'
        
    #テーブルに登録情報を記録
    sql = f'''INSERT IGNORE INTO {DB_NAME}.{TABLE_NAME} VALUES("{uname}","{grade}","{mesc}","{displayname}","{passwd}","{email}","{discord}","{post}","NoToken","True","{class_number}");'''
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()
    return 0

#ユーザーを削除
def delete_user(conn,uname:str):
    c = conn.cursor()
    #削除履歴に追加
    res = search_userinfo_from_name(conn,uname)
    now_time = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
    sql = f'''INSERT IGNORE INTO {DB_NAME}.deleted_users VALUES("{uname}","{res[0][1]}","{res[0][2]}","{res[0][3]}","{now_time}","{res[0][5]}","{res[0][6]}","{res[0][7]}");'''
    c.execute(sql)
    conn.commit()
    #ユーザー削除
    c.execute(f'''DELETE FROM {TABLE_NAME} WHERE uname = "{uname}";''')
    conn.commit()
    c.close()

#ユーザー登録情報を検索(ユーザー名から)
def search_userinfo_from_name(conn,uname:str):
    c=conn.cursor()
    c.execute(f'''SELECT * FROM {TABLE_NAME} WHERE uname = "{uname}" ''')
    res = c.fetchall()
    c.close()
    return res #ユーザーのレコードを配列として返す

#全ユーザー登録情報一覧
def get_all_users(conn):
    c=conn.cursor()
    sql = f'''
        SELECT * FROM {TABLE_NAME}
    '''
    c.execute(sql)
    res = c.fetchall()
    c.close()
    return res #ユーザー登録情報を配列として返す

#ユーザー登録情報更新
def update_user_info(conn,uname:str,column:str,new_data:str):
    c = conn.cursor()

    if column == 'passwd':
        sql = f'''
            UPDATE {TABLE_NAME} SET changedpwd = "True" WHERE uname = "{uname}"
        '''
        c.execute(sql)
        conn.commit()

    sql = f'''
        UPDATE {TABLE_NAME} SET {column} = "{new_data}" WHERE uname = "{uname}"
    '''
    c.execute(sql)
    conn.commit()
    c.close()

#役員と部員の人数を取得
def get_club_information(conn):
    #役員などの情報を取得
    c = conn.cursor()
    c.execute(f'''SELECT displayname,grade,mesc FROM pcc_cas.{TABLE_NAME} WHERE post = "部長" ''')
    leader = c.fetchall()
    c.execute(f'''SELECT displayname,grade,mesc FROM pcc_cas.{TABLE_NAME} WHERE post = "副部長" ''')
    subleaders = c.fetchall()
    c.execute(f'''SELECT displayname,grade,mesc FROM pcc_cas.{TABLE_NAME} WHERE post = "会計" ''')
    casher = c.fetchall()
    c.execute(f'''SELECT displayname,grade,mesc FROM pcc_cas.{TABLE_NAME} WHERE post = "システム管理者" ''')
    administrator = c.fetchall()

    #各学年の人数を取得
    c.execute(f'''SELECT COUNT(*) FROM pcc_cas.{TABLE_NAME} WHERE grade = "1" ''')
    grade1 = c.fetchall()
    c.execute(f'''SELECT COUNT(*) FROM pcc_cas.{TABLE_NAME} WHERE grade = "2" ''')
    grade2 = c.fetchall()
    c.execute(f'''SELECT COUNT(*) FROM pcc_cas.{TABLE_NAME} WHERE grade = "3" ''')
    grade3 = c.fetchall()
    c.execute(f'''SELECT COUNT(*) FROM pcc_cas.{TABLE_NAME} WHERE grade = "4" ''')
    grade4 = c.fetchall()
    c.execute(f'''SELECT COUNT(*) FROM pcc_cas.{TABLE_NAME} WHERE grade = "5" ''')
    grade5 = c.fetchall()
    c.close()

    workers = [leader,subleaders,casher,administrator]
    members = [grade1[0][0],grade2[0][0],grade3[0][0],grade4[0][0],grade5[0][0]]

    return workers,members

#有効なトークンの有効性検証結果とユーザ名の応答
def cktoken(conn,uname:str,token:str):
    c=conn.cursor()
    #ユーザの登録有無
    c.execute(f'''SELECT * FROM {TABLE_NAME} WHERE uname = "{uname}" ''')
    suser_res = c.fetchall()
    
    #トークンがすでに存在しているか
    c.execute(f'''SELECT * FROM {TABLE_NAME} WHERE setting_token = "{token}" ''')
    token_res = c.fetchall()

    #ログインが正しいか
    c.execute(f'''SELECT * FROM {TABLE_NAME} WHERE uname = "{uname}" AND setting_token = "{token}"''')
    usr_token_res = c.fetchall()
    c.close()

    if len(suser_res) == 0:
        #ユーザ登録なし
        return "Not Submit" ,0
    else:
        if len(token_res) == 0 : #ほかにログインしている可能性あり
            #nameが存在かつ、NoTokenではないTokenが存在
            return "NoUname",1
        elif str(token_res[0][8]) == "NoToken": #ログインなし/トークンの期限切れ
            #nameが存在かつ、NoTokenである
            return "NoUname",2
        else:#ユーザのトークンが有効(ログイン状態である)
            name = token_res[0][0]
            return str(uname),3

#トークン更新
def update_token(conn,uname:str,new_token:str):
    c = conn.cursor()

    sql1 = f'''
        UPDATE {TABLE_NAME} SET setting_token = "{new_token}" WHERE uname = "{uname}"
    '''
    c.execute(sql1)
    conn.commit()
    c.close()

#ユーザのパスワード未変更を検出
def ckpwdchange(conn,uname:str):
    res = search_userinfo_from_name(conn,uname)
    if res[0][9] == "False":
        return 1
    else:
        return 0

#################################################################

#基幹システム連携関連

#################################################################

#ランダムトークン生成
def randomname(TOKEN_SIZE):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=TOKEN_SIZE))

#基幹システム連携用のトークン発行
def generateAccessToken(conn,system_name:str):
    system_token = randomname(TOKEN_SIZE)

    #テーブルをなければ作る
    c = conn.cursor()
    c.execute(INIT_SQL_COMMAND_2)
    conn.commit()

    save_token = f'''INSERT IGNORE INTO {DB_NAME}.pcc_systems_token VALUES(
        "{system_name}","{system_token}"
    );'''
    c.execute(save_token)
    conn.commit()
    c.close()

    return system_token

#基幹システム連携用トークンの有効性検証
def ckSystemToken(conn,system_token):
    c=conn.cursor()
    c.execute(f'''SELECT * from pcc_systems_token WHERE system_token = "{system_token}"''')
    res = c.fetchall()
    conn.commit()
    c.close()

    if len(res) == 0:
        return False
    else:
        return True
