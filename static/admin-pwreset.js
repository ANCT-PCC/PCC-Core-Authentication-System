const SERVER_ADDR = "https://test-cas.nemnet-lab.net/"; // サーバのアドレスを指定

const $CHECK_BUTTON = document.getElementById("check_button");
const $RESET_BUTTON = document.getElementById("reset_button");
const $INPUT_UNAME = document.getElementById("uname");
const $OUTPUT_DISPLAYNAME = document.getElementById("displayname");

is_checked = false;

//入力されたユーザ名が存在するか確認し、存在すれば
//ユーザ名に対応する部員の名前を表示する
$CHECK_BUTTON.addEventListener("click", async () => {
    const uname = $INPUT_UNAME.value;
    if (uname === "") {
        alert("リセット対象のユーザ名を入力してください");
        return;
    }
    $.ajax({
        url:SERVER_ADDR+'admintools/db/check_user_exist',
        type:'POST',
        data:JSON.stringify({"uname": uname}), //ここで辞書型からJSONに変換
        dataType: 'json',
        contentType: 'application/json'
    }).done(function(data){
        console.log(data);
        $OUTPUT_DISPLAYNAME.placeholder = data['displayname'];
        is_checked = true;
    }).fail(function(jqXHR){
        console.log(jqXHR);
        console.log(jqXHR.status);
        alert("ユーザの確認に失敗しました"+'\n'+jqXHR.status);
    });
});

//入力されたユーザ名に対応する部員のパスワードをリセットする
$RESET_BUTTON.addEventListener("click", async () => {
    const uname = $INPUT_UNAME.value;
    if (uname === "") {
        alert("リセット対象のユーザ名を入力してください");
        return;
    }
    else if(!is_checked) {
        alert("「ユーザの確認」を押して、対象のユーザを確認してください");
        return;
    }
    $.ajax({
        url:SERVER_ADDR+'admintools/db/pw_reset',
        type:'POST',
        data:JSON.stringify({"uname": uname}), //ここで辞書型からJSONに変換
        dataType: 'json',
        contentType: 'application/json'
    }).done(function(data){
        console.log(data);
        alert("パスワードをリセットしました"+'\n'+
              "新しいパスワードは「"+data['new_passwd']+"」です"+'\n'+
              "※この表示を消すと、パスワードは再表示されません！");
        is_checked = false;
        $OUTPUT_DISPLAYNAME.placeholder = "";
        $INPUT_UNAME.value = "";
    }).fail(function(jqXHR){
        console.log(jqXHR);
        console.log(jqXHR.status);
        alert("パスワードのリセットに失敗しました"+'\n'+jqXHR.status);
    });
    
});