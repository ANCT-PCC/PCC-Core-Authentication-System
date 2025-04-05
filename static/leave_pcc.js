const $leave_pcc = document.getElementById("leave_pcc");
const $passwd_for_leave_pcc = document.getElementById("passwd_for_leave_pcc");

$leave_pcc.addEventListener("click", function (e) {
    if ($passwd_for_leave_pcc.value == "") {
        alert("退部するにはパスワードが必要です。");
    } else {
        if (confirm("退部します。元には戻せませんが、本当によろしいですか？")){
            var data = [{
                password: $passwd_for_leave_pcc.value 
            }]
            $.ajax({
                url:'https://test-cas.nemnet-lab.net/'+'leave_pcc',
                type:'POST',
                data:JSON.stringify(data), //ここで辞書型からJSONに変換
                dataType: 'json',
                contentType: 'application/json',
                success: function (response) {
                    console.log("退部成功");
                    alert("退部しました。");
                    window.location.href = 'https://test-cas.nemnet-lab.net/';
                },
                error: function (jqXHR) {
                    console.log("statuscode::")
                    console.log(jqXHR.status);
                    if (String(jqXHR.status) === "200") {
                        //ログイン続行
                        alert("退部しました。");
                        window.location.href = 'https://test-cas.nemnet-lab.net/';
                    } else {
                        console.log(jqXHR.status);
                        alert("正常に完了しませんでした。退部手続きが完了していない可能性があります。内容をもう一度確かめてください。");
                    }
                }
            })
        }
    }
});