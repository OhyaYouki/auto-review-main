from lib.modules.common import *
from lib.modules.issue1_3_check import *

def output(pull_url,output):
    output.insert('end','---チェック開始---','info')
    driver = driver_init(pull_url)
    output.insert('end','\n◎What,Why,gyazo,差分なし,マージ済','info')
    #Conversationチェック(conflict以外)
    output_error(output, conversation_check(driver,0))
    #issue1-3
    driver.get(pull_url + '/files')
    
    output.insert('end','\n◎コントローラー','info')
    output_error(output, check_c(driver))
    output.insert('end','\n◎ビュー','info')
    output_error(output, check_v(driver))
    output.insert('end','\n---チェック終了---','info')
    driver.quit()