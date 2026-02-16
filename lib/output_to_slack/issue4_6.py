from lib.modules.common import *
from lib.modules.issue4_6_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*Issue4-6のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,1,False))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #ユーザー管理
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎コントローラー',check_c(driver))
    error,warning = append_message(error,warning,'◎ビュー',check_v(driver))
    driver.quit()
    return error,warning
