from lib.modules.common import *
from lib.modules.destroy_item_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*削除機能のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,1))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #商品削除
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎商品コントローラー',check_items_c(driver))
    error,warning = append_message(error,warning,'◎詳細ページ',check_show_v(driver))
    # error,warning = append_message(error,warning,'◎ルーティング',check_routes(driver))
    driver.quit()
    return error,warning
