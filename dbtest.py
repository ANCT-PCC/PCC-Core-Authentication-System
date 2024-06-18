import dbc
conn = dbc.startConnection()
dbc.create_new_user(conn,'s203120','1','S','齋藤 直人','UNKO','s203120@edu.asahikawa-nct.ac.jp','networld4816','no','NoToken')
dbc.closeConnection(conn)