from lib.modules.common import *
from lib.modules.show_item_check import *

def output(pull_url,output):
    output.insert('end','---チェック開始---','info')
    driver = driver_init(pull_url)
    output.insert('end','\n◎What,Why,gyazo,差分なし,マージ済','info')
    #Conversationチェック(conflict以外)
    output_error(output, conversation_check(driver))
    #商品詳細
    driver.get(pull_url + '/files')

    output.insert('end','\n◎itemsコントローラー','info')
    output_error(output, check_items_c(driver))
    output.insert('end','\n◎indexファイル','info')
    output_error(output, check_index_v(driver))
    output.insert('end','\n◎showファイル','info')
    output_error(output, check_show_v(driver))
    output.insert('end','\n◎ルーティングファイル','info')
    output_error(output, check_routes(driver))
    output.insert('end','\n◎その他','info')
    output_error(output, check_others(driver))
    
    output.insert('end','\n---チェック終了---','info')
    driver.quit()