import subprocess
import hashlib
import mysql.connector
import string,random

DB_SERVER = 'pcc-cas-db'
#DB_SERVER='127.0.0.1'
DB_NAME = 'pcc_cas'
DB_PASSWD = 'Kusopass'
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
    setting_token TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''
INIT_SQL_COMMAND_2 = f'''CREATE TABLE IF NOT EXISTS {DB_NAME}.pcc_systems_token (
    system_name VARCHAR(255) NOT NULL PRIMARY KEY,
    system_token TEXT
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'''

#MySQL接続
def startConnection():
    conn = mysql.connector.connect(
        host=DB_SERVER,
        user='root',
        password=DB_PASSWD,
        database=DB_NAME,
        port='3306'
    )
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
    else:
        post = 'その他の役職'
        
    #テーブルに登録情報を記録
    sql = f'''INSERT IGNORE INTO {DB_NAME}.{TABLE_NAME} VALUES("{uname}","{grade}","{mesc}","{displayname}","{str(hashlib.sha256(passwd.encode('utf-8')).hexdigest())}","{email}","{discord}","{post}","NoToken");'''
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()
    return 0

#ユーザーを削除
def delete_user(conn,uname:str):
    c = conn.cursor()
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
    sql = f'''
        UPDATE {TABLE_NAME} SET {column} = "{new_data}" WHERE uname = "{uname}"
    '''
    c.execute(sql)
    conn.commit()
    c.close()

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
    if len(res) == 0:
        return 1
    uname_hash = hashlib.sha256(uname.encode('utf-8')).hexdigest()
    applied_passwd = res[0][4] #現在設定されているパスワード
    old_temp_passwd_hash = uname_hash #初期パスワード(改定前)
    new_temp_passwd = 'Kusopass@'+uname[1:]
    new_temp_passwd_hash = hashlib.sha256(new_temp_passwd.encode('utf-8')).hexdigest() #初期パスワード(改定後)

    if applied_passwd == old_temp_passwd_hash or applied_passwd == new_temp_passwd_hash:
        return 1 #パスワードが未変更
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