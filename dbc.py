import sqlite3,json,datetime
import random,string
import json
import subprocess
import hashlib
import mysql.connector

DB_SERVER = '192.168.200.100'
DB_NAME = 'pcc_cas'
DB_PASSWD = 'Minecraft7010'
TABLE_NAME = 'pcc_users'
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
    c.close()
    return res

def discord_message(message:str,uname:str):
    command = ["python","send_discord.py",message,uname]
    subprocess.Popen(command)
    

#################################################################

#ユーザー関連

#################################################################

#新規ユーザを作成する
def create_new_user(conn,uname:str,grade:str,mesc:str,displayname:str,passwd:str,email:str,discord:str,post:str,setting_token:str):
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute(INIT_SQL_COMMAND)
    c.close()
    #テーブルに登録情報を記録
    sql = f'''INSERT IGNORE INTO {TABLE_NAME} VALUES("{uname}","{grade}","{mesc}","{displayname}","{str(hashlib.sha256(passwd.encode('utf-8')).hexdigest())}","{email}","{discord}","{post}","{setting_token}");'''
    c = conn.cursor()
    c.execute(sql)
    c.close()
    return 0

#ユーザーを削除
def delete_user(uname:str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    #ユーザー削除
    c.execute(f'''DELETE FROM "{TABLE_NAME}" WHERE uname == "{uname}" ''')
    conn.commit()
    c.close()

#ユーザー登録情報を検索(ユーザー名から)
def search_userinfo_from_name(uname:str):
    conn = sqlite3.connect(DB_NAME)
    c=conn.cursor()
    c.execute(f'''SELECT * FROM "{TABLE_NAME}" WHERE uname == "{uname}" ''')
    res = c.fetchall()
    conn.close()
    return res #ユーザーのレコードを配列として返す

#全ユーザー登録情報一覧
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c=conn.cursor()
    sql = '''
        SELECT * FROM "{TABLE_NAME}"
    '''
    c.execute(sql)
    res = c.fetchall()
    return res #ユーザー登録情報を配列として返す

#ユーザー登録情報更新
def update_user_info(uname:str,column:str,new_data:str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    prev_userinfo = search_userinfo_from_name(uname)

    sql1 = f'''
        UPDATE "{TABLE_NAME}" SET "{column}" = "{new_data}" WHERE name = "{uname}"
    '''
    c.execute(sql1)
    conn.commit()

#有効なトークンの有効性検証結果とユーザ名の応答
def cktoken(uname:str,token:str):
    conn = sqlite3.connect(DB_NAME)
    c=conn.cursor()
    #ユーザの登録有無
    c.execute(f'''SELECT * FROM "{TABLE_NAME}" WHERE uname == "{uname}" ''')
    suser_res = c.fetchall()
    
    #トークンがすでに存在しているか
    c.execute(f'''SELECT * FROM "{TABLE_NAME}" WHERE setting_token == "{token}" ''')
    token_res = c.fetchall()

    #ログインが正しいか
    c.execute(f'''SELECT * FROM "{TABLE_NAME}" WHERE uname == "{uname}" AND setting_token == "{token}"''')
    usr_token_res = c.fetchall()
    #レコードのフォーマット↓
    #name,email,isAdmin,solt,passwd,activate_flag,uuid,accessToken
    conn.close()

    if len(suser_res) == 0:
        #ユーザ登録なし
        return "Not Submit" ,0
    else:
        if len(token_res) == 0 : #ほかにログインしている可能性あり
            #nameが存在かつ、NoTokenではないTokenが存在
            return name,1
        elif str(token_res[0][8]) == "NoToken": #ログインなし/トークンの期限切れ
            #nameが存在かつ、NoTokenである
            return "NoUname",2
        else:#ユーザのトークンが有効(ログイン状態である)
            name = token_res[0][1]
            #トークンの時間制限をリセットする処理を書きたい
            return str(uname),3

#トークン更新
def update_token(uname:str,new_token:str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql1 = f'''
        UPDATE "{TABLE_NAME}" SET setting_token = "{new_token}" WHERE uname = "{uname}"
    '''
    c.execute(sql1)
    conn.commit()