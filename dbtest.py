import dbc,hashlib
conn = dbc.startConnection()
pwd=hashlib.sha256('unko'.encode('utf-8')).hexdigest()
dbc.create_new_user(conn,'s203120','1','S','齋藤 直人',pwd,'s203120@edu.asahikawa-nct.ac.jp','networld4816','4')
dbc.closeConnection(conn)