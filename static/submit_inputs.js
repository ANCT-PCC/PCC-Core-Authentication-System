const $submit_button = document.getElementById("submit_inputs");
const $entry_keyword = document.getElementById("entry_keyword");

const currentURL = window.location.href; // 現在のURLを取得
const form_id = currentURL.slice(-64); // URLの最後の64文字を取得

$submit_button.addEventListener('click', (e) => {
    if ($entry_keyword.value === "") {
        alert("「入部のあいことば」を入力してください");
    } else {
        $.ajax({
            type: "POST",
            url: "https://test-cas.nemnet-lab.net/submit/entry_keyword",
            data: JSON.stringify([{
                entry_keyword: $entry_keyword.value,
            }]),
            dataType: 'json',
            contentType: 'application/json'
        }).always(function (jqXHR, json) {
            console.log("statuscode::")
            console.log(jqXHR.status);
            if (String(jqXHR.status) === "200") {
                //入部のあいことばの確認成功
                window.location.href = 'https://test-cas.nemnet-lab.net/' + 'submit/setup/' + form_id;
            } else {
                //入部のあいことばの確認失敗
                console.log("入部のあいことばの確認失敗")
                alert("「入部のあいことば」が正しくありません");
            }
        });
    }
})