# PCC-CAS パソコン部 基幹認証システム
## 概要
PCC-CASとは、Personal Computer Club-Core Authentication System(パソコン部 基幹認証システム)の略称です。  
  
  この認証システムを使用する基幹システム:  
  「備品管理システム PCC-RENT」  
  「入退出管理システム」  

## どんなシステム
弊部の基幹システムで使用するアカウントをすべて、一括で管理してしまおうってやつ。　　
他のシステムは、専用のPythonモジュールなどを用いて  
認証結果を受け取り、PCC-CASからの認証情報を使って各自データ処理する。

## 認証モジュールの使い方
細かい説明は、CASAuth.pyとauthtest.pyにコメントアウトしている  
pip install requests を実行  
CASAuth.pyをインポートする。  
CASAuth.Authentication()で認証する。  
引数は「username:str,password:str」で  
passwordには、生の値をぶち込む。(ハッシュ化は自動でやってくれます)  
system_tokenには、PCC-CAS管理者から発行された値を入れる。

認証結果として、以下の形式でjsonが返ってくる  
{  
  "login_status":0, //認証可否(0:成功 1:不可)   
  "username":uname, //ユーザ名  
  "displayame":displayname, //部員名  
  "post":post, //役職  
  "grade":grade,　//学年  
  "mesc":mesc,　//学科  
  "discord_id":discord_id //Discordのユーザ名  
}  
この認証結果を使って、各システムでデータを処理する。  
LDAPサーバとか、構築できたら最高なんだろうけど、取り合えず、独自開発の基幹システムに関してはこれで運用しよう