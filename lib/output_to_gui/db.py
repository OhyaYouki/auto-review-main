from lib.modules.common import *
from lib.modules.db_check import *

def output(pull_url,output):
    output.insert('end','---チェック開始---','info')
    driver = driver_init(pull_url)
    output.insert('end','\n◎What,Why,gyazo,差分なし,マージ済','info')
    #Conversationチェック(conflict以外)
    output_error(output, conversation_check(driver))
    
    driver.get(pull_url + '/files')
    output.insert('end','\n◎DB以外','info')
    output_error(output, check_others(driver))
    
    #DB設計
    if goto_readme(driver):
        output.insert('end','\n◎テーブル数・アソシエーション','info')
        output_error(output, check_table_num_and_association(driver))
        output.insert('end','\n◎ユーザーテーブル','info')
        output_error(output, check_users_table(driver))
        output.insert('end','\n◎商品テーブル','info')
        output_error(output, check_items_table(driver))
        output.insert('end','\n◎購入履歴テーブル','info')
        output_error(output, check_orders_table(driver))
        output.insert('end','\n◎住所テーブル','info')
        output_error(output, check_addresses_table(driver))
    else:
        output_error(output, [['READMEを見つけられませんでした'],[]])

    output.insert('end','\n---チェック終了---','info')
    driver.quit()