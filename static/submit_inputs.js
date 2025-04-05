const $submit_button = document.getElementById("submit_inputs");

$submit_button.addEventListener('click', (e) => {
    const currentURL = window.location.href; // 現在のURLを取得
    const form_id = currentURL.slice(-64); // URLの最後の64文字を取得

    window.location.href = 'https://test-cas.nemnet-lab.net/' + 'submit/setup/' + form_id;
})