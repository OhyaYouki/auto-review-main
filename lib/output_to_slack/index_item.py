from lib.modules.common import *
from lib.modules.index_item_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*一覧機能のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,2))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #商品一覧
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎itemsコントローラー',check_items_c(driver))
    error,warning = append_message(error,warning,'◎indexファイル',check_index_v(driver))
    error,warning = append_message(error,warning,'◎その他',check_others(driver))
    driver.quit()
    return error,warning
