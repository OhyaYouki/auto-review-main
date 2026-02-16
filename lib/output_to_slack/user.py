from lib.modules.common import *
from lib.modules.user_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*ユーザー機能のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,6))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #ユーザー管理
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎applicationコントローラー',check_app_c(driver))
    error,warning = append_message(error,warning,'◎ユーザーモデル',check_user_m(driver))
    error,warning = append_message(error,warning,'◎ログインページ',check_session_v(driver))
    error,warning = append_message(error,warning,'◎登録ページ',check_registration_v(driver))
    error,warning = append_message(error,warning,'◎ヘッダー',check_header_v(driver))
    # error,warning = append_message(error,warning,'◎ルーティング',check_routes(driver))
    error,warning = append_message(error,warning,'◎マイグレーション',check_user_mig(driver))
    error,warning = append_message(error,warning,'◎factorybot',check_user_f(driver))
    error,warning = append_message(error,warning,'◎単体テスト',check_user_t(driver))
    error,warning = append_message(error,warning,'◎その他',check_others(driver))
    driver.quit()
    return error,warning
