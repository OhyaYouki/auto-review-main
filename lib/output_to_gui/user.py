from lib.modules.common import *
from lib.modules.user_check import *

def output(pull_url,output):
    output.insert('end','---チェック開始---','info')
    driver = driver_init(pull_url)
    #Conversationチェック(conflict以外)
    output.insert('end','\n◎What,Why,gyazo,差分なし,マージ済','info')
    errors = conversation_check(driver)
    output_error(output, errors)
    if "プルリクエストURLが無効です" in errors: return 
    #ユーザー管理
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'new-discussion-timeline').text
    driver.get(pull_url + '/files')
    #下流ファイルに一つメソッドを作成するごとに以下二行を本ファイルに追加してください
    #output.insert('end','\n◎<チェックする項目>','info')
    #output_error(output, <下流ファイルに作成したメソッド名>(driver))

    output.insert('end','\n◎applicationコントローラー','info')
    output_error(output, check_app_c(driver))
    output.insert('end','\n◎ユーザーモデル','info')
    output_error(output, check_user_m(driver))
    output.insert('end','\n◎ログインページ','info')
    output_error(output, check_session_v(driver))
    output.insert('end','\n◎登録ページ','info')
    output_error(output, check_registration_v(driver))
    output.insert('end','\n◎ヘッダー','info')
    output_error(output, check_header_v(driver))
    if first_review:
        output.insert('end','\n◎ルーティング','info')
    output_error(output, check_routes(driver))
    output.insert('end','\n◎マイグレーション','info')
    output_error(output, check_user_mig(driver))
    output.insert('end','\n◎factorybot','info')
    output_error(output, check_user_f(driver))
    output.insert('end','\n◎単体テスト','info')
    output_error(output, check_user_t(driver))
    output.insert('end','\n◎その他','info')
    output_error(output, check_others(driver))
    output.insert('end','\n---チェック終了---','info')
    driver.quit()
