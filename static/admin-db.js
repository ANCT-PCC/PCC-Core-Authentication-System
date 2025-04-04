const SERVER_ADDR = 'https://test-cas.nemnet-lab.net/'
const $SQL_EXECUTE = document.getElementById('sqlexecute_button') 
const $SQL_RESULT = document.getElementById('sqlresult')
const $SQL_CMD = document.getElementById('sqlcmd')

$SQL_EXECUTE.addEventListener('click',(e)=>{
    command = $SQL_CMD.value

    _data = {
        'sqlcmd': String(command)
    }

    $.ajax({
        url:SERVER_ADDR+'admintools/db/sqlexecute',
        type:'POST',
        data:JSON.stringify(_data), //ここで辞書型からJSONに変換
        dataType: 'json',
        contentType: 'application/json'
    }).always(function(jqXHR){
        console.log(jqXHR.status)
        $SQL_RESULT.value = String(jqXHR)
    })
})