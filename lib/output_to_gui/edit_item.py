from lib.modules.common import *
from lib.modules.edit_item_check import *

def output(pull_url,output):
    output.insert('end','---チェック開始---','info')
    driver = driver_init(pull_url)
    output.insert('end','\n◎What,Why,gyazo,差分なし,マージ済','info')
    #Conversationチェック(conflict以外)
    output_error(output, conversation_check(driver))
    #商品編集
    driver.get(pull_url + '/files')
    #下流ファイルに一つメソッドを作成するごとに以下二行を本ファイルに追加してください
    #output.insert('end','\n◎<チェックする項目>','info')
    #output_error(output, <下流ファイルに作成したメソッド名>(driver))
    output.insert('end','\n◎コントローラー','info')
    output_error(output, check_items_c(driver))
    output.insert('end','\n◎編集ページ','info')
    output_error(output, check_edit_v(driver))
    output.insert('end','\n◎詳細ページ','info')
    output_error(output, check_show_v(driver))
    output.insert('end','\n◎ルーティング','info')
    output_error(output, check_routes(driver))
    output.insert('end','\n◎その他','info')
    output_error(output, check_others(driver))

    output.insert('end','\n---チェック終了---','info')
    driver.quit()