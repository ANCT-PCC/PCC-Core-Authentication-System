#!/bin/bash
PREV_ADDR='http://localhost:8080/'
SERVER_ADDR='http://192.168.200.100:8080/'

sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/login.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-db.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-user.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-top.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admintools.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/members.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/passwd_change.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/user_settings.js

python pcc-cas.py