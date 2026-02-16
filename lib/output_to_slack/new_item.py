from lib.modules.common import *
from lib.modules.new_item_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*出品機能のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,6))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #商品出品
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎商品コントローラ',check_items_c(driver))
    error,warning = append_message(error,warning,'◎価格js',check_price_j(driver))
    error,warning = append_message(error,warning,'◎商品モデル',check_item_m(driver))
    error,warning = append_message(error,warning,'◎activehashモデル',check_activehash_m(driver))
    error,warning = append_message(error,warning,'◎トップページ',check_index_v(driver))
    error,warning = append_message(error,warning,'◎出品ページ',check_new_v(driver))
    # error,warning = append_message(error,warning,'◎ルーティング',check_routes(driver))
    error,warning = append_message(error,warning,'◎マイグレーション',check_item_mig(driver))
    error,warning = append_message(error,warning,'◎factorybot',check_item_f(driver))
    error,warning = append_message(error,warning,'◎単体テスト',check_item_t(driver))
    error,warning = append_message(error,warning,'◎その他',check_others(driver))
    driver.quit()
    return error,warning