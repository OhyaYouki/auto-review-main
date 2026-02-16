from lib.modules.common import *
from lib.modules.db_check import *

def output(driver):
    first_review = not "reviewed" in driver.find_element(By.CLASS_NAME,'pull-discussion-timeline').text
    error = '*DB設計のチェック結果*\n\n'
    warning = '*⚠️修正任意・要確認項目*\n\n'
    #Conversationチェック(conflict以外)
    if first_review:
        error,warning = append_message(error,warning,'◎What,Why,gyazo(初回のみ),差分なし,マージ済',conversation_check(driver,1))
    else:
        error,warning = append_message(error,warning,'◎差分なし,マージ済',conversation_check(driver,0,False))
    
    driver.get(driver.current_url + '/files')
    error,warning = append_message(error,warning,'◎その他',check_others(driver))

    #DB設計
    if goto_readme(driver):
        error,warning = append_message(error,warning,'◎テーブル数・アソシエーション',check_table_num_and_association(driver))
        error,warning = append_message(error,warning,'◎ユーザーテーブル',check_users_table(driver))
        error,warning = append_message(error,warning,'◎商品テーブル',check_items_table(driver))
        error,warning = append_message(error,warning,'◎購入履歴テーブル',check_orders_table(driver))
        error,warning = append_message(error,warning,'◎住所テーブル',check_addresses_table(driver))
    else:
        error += '`READMEを見つけられませんでした`\n'
    driver.quit()
    return error,warning