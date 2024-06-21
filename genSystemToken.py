import dbc

conn = dbc.startConnection()

token = dbc.generateAccessToken(conn,'試験用スクリプト')

print(token)