const $form_grade = document.getElementById("grade");
const $form_class = document.getElementById("class");
const $form_firstname = document.getElementById("firstname");
const $form_lastname = document.getElementById("lastname");
const $form_pwd = document.getElementById("password");
const $form_pwd_retype = document.getElementById("password_retype");
const $form_discord = document.getElementById("discord_id");
const $button_next = document.getElementById("next_button");

const $error_message = document.getElementById("error_message");
$error_message.style.visibility = 'hidden';

const SERVER_ADDR='http://localhost:8080/'

$button_next.addEventListener('click',(e) => {
    if ($form_grade.value == '' || $form_class.value == '' || $form_firstname.value == '' || $form_lastname.value == '' || $form_pwd.value == '' || $form_pwd_retype.value == '' || $form_discord.value == ''){
        $error_message.textContent = 'すべての項目を入力してください';
        $error_message.style.visibility = 'visible';
    }else if($form_pwd.value !== $form_pwd_retype.value){
        $error_message.textContent = 'パスワードが一致しません';
    }else{
    var form_data = [
        {
        grade: String($form_grade.value),
        class: String($form_class.value),
        firstname: String($form_firstname.value),
        lastname: String($form_lastname.value),
        password: String($form_pwd.value),
        discord_id: String($form_discord.value)
        }
    ];    

    console.log(form_data)
    
    $.ajax(
        {
          url:'http://localhost:8080/'+'/submit/veryfi_inputs',
          type:'POST',
          data:JSON.stringify(form_data), //ここで辞書型からJSONに変換
          dataType: 'json',
          contentType: 'application/json'
    }).always(function (jqXHR,data) {
        console.log("statuscode::")
        console.log(jqXHR.status);
        if(String(jqXHR.status) === "200"){
            //サーバへの入力データの一時キャッシュ成功
            //内容確認画面へ遷移
            login_status_error.style.visibility = "hidden";
            window.location.href = 'http://localhost:8080/';
        }else{
            //サーバサイドエラー
            console.log("サーバサイドエラー")
            console.log(jqXHR.status);
          $error_message.textContent = "不明なエラー。システム管理者へ問い合わせてください";
          $error_message.style.visibility = "visible";
        }
    })};

});