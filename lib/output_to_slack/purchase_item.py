from lib.modules.common import *
from lib.modules.purchase_item_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*購入機能のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,10))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    #商品購入
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎商品コントローラー',check_items_c(driver))
    error,warning = append_message(error,warning,'◎購入コントローラー',check_orders_c(driver))
    error,warning = append_message(error,warning,'◎payjpのjs',check_card_j(driver))
    f_messages,messages = check_form_m(driver)
    error,warning = append_message(error,warning,'◎formオブジェクト',f_messages)
    error,warning = append_message(error,warning,'◎購入履歴・住所モデル',messages)
    error,warning = append_message(error,warning,'◎ユーザーモデル',check_user_m(driver))
    error,warning = append_message(error,warning,'◎商品モデル',check_item_m(driver))
    error,warning = append_message(error,warning,'◎トップページ',check_top_v(driver))
    error,warning = append_message(error,warning,'◎詳細ページ',check_show_v(driver))
    error,warning = append_message(error,warning,'◎購入ページ',check_order_v(driver))
    # error,warning = append_message(error,warning,'◎ルーティング',check_routes(driver))
    error,warning = append_message(error,warning,'◎マイグレーション',check_order_mig(driver))
    error,warning = append_message(error,warning,'◎factorybot',check_order_f(driver))
    error,warning = append_message(error,warning,'◎単体テスト',check_order_t(driver))
    error,warning = append_message(error,warning,'◎その他',check_others(driver))
    driver.quit()
    return error,warning