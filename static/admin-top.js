const SERVER_ADDR = 'https://test-cas.nemnet-lab.net/'
const $MOVE_DB = document.getElementById('move_db')
const $MOVE_USER = document.getElementById('move_user')
const $MOVE_PWRESET = document.getElementById('move_pwreset')

window.onload = function(){

    $MOVE_DB.addEventListener('click',(e)=>{
        window.location = SERVER_ADDR+'admintools/db'
    })

    $MOVE_USER.addEventListener('click',(e)=>{
        window.location = SERVER_ADDR+'admintools/user'
    })

    $MOVE_PWRESET.addEventListener('click',(e)=>{
        window.location = SERVER_ADDR+'admintools/pw_reset'
    })
}