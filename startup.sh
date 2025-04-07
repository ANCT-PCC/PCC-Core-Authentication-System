#!/bin/bash
PREV_ADDR='https://test-cas.nemnet-lab.net/'
#SERVER_ADDR='https://pcc-cas.nemnet-lab.net/' #本番環境
SERVER_ADDR='https://test-cas.nemnet-lab.net/' #試験環境

sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/login.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-db.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-user.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admin-top.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/admintools.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/members.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/passwd_change.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/user_settings.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/submit.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/submit_inputs.js
sed -i -e s#$PREV_ADDR#$SERVER_ADDR#g static/leave_pcc.js

python pcc-cas.py