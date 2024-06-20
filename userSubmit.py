import dbc,csv

def userSubmit(conn):
    csvfile = open("userList.csv","r",encoding="utf-8")

    file = csv.reader(csvfile, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

    for row in file:
        dbc.create_new_user(conn,row[0],row[1],row[2],row[3],"Kusopass@"+row[0][1:],row[0][:7]+"@edu.asahikawa-nct.ac.jp","未設定",row[4])
    csvfile.close()

def userDelete(conn):
    csvfile = open("deluserList.csv","r",encoding="utf-8")

    file = csv.reader(csvfile, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

    for row in file:
        dbc.delete_user(conn,row[0])
        
    csvfile.close()

if __name__ == '__main__':
    userSubmit()