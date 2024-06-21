import dbc

service_name= input("サービス名 > ")
conn = dbc.startConnection()

token = dbc.generateAccessToken(conn,service_name)

print(token)