from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text
import re

def check_items_c(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers') and contains(@title,'_controller.rb') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("itemsコントローラに「売却済み商品を編集しようとするとトップページに遷移する」が実装されていません")
    else:
        if "logger" in file_text: errors.append("Rails.logger.debugが見つかりました\mデバッグ用のRails.logger.debugは削除しましょう。")
        if "binding.pry" in file_text: errors.append("binding.pryが見つかりました\mデバッグ用のbinding.pryは削除しましょう。")
        if not (re.search('unless.+?\..+?==nil',file_text)\
            or re.search('unless.+?\..+?\.nil\?',file_text)\
            or re.search('unless.+?\..+?\.blank\?',file_text)\
            or re.search('if.+?\..+?==nil\nrender',file_text)\
            or re.search('if.+?\..+?\.nil\?\nrender',file_text)\
            or re.search('if.+?\..+?\.blank\?\nrender',file_text)\
            or re.search('if.+?\..+?\.present\?',file_text)\
            or re.search('if.+?\..+?\.exists\?\(.+?\)',file_text)\
            or re.search('if.+?\..+?!=nil',file_text)\
            or re.search('if.+?\..+?==nil\nelse',file_text)\
            or re.search('if.+?\..+?\.nil\?\nelse',file_text)\
            or re.search('if.+?\..+?\.blank\?\nelse',file_text)\
            or re.search('unless.+?\..+?\.present\?\nelse',file_text)\
            or re.search('unless.+?\..+?\.exists\?\(.+?\)\nelse',file_text)\
            or re.search('unless.+?\..+?!=nilelse',file_text)\
            or re.search('returnunless.+?\..+?\.present\?\n',file_text)\
            or re.search('returnunless.+?\..+?\.exists\?\(.+?\)\n',file_text)\
                ): errors.append('売り切れ時に編集ページを表示させない処理が見つかりません')
    return [errors,warnings]

def check_orders_c(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers') and contains(@title,'_controller.rb') and not (contains(@title,'item') or contains(@title,'product') or contains(@title,'application'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        if "logger" in file_text: errors.append("Rails.logger.debugの記述が見つかりました\mデバッグ用のRails.logger.debugは削除しましょう。")
        if "binding.pry" in file_text: errors.append("binding.pryが見つかりました\mデバッグ用のbinding.pryは削除しましょう。")
        if not "before_action:authenticate_user!" in file_text: errors.append("authenticate_user!がbefore_actionに見つかりません")
        if not "gon.public_key" in file_text: errors.append("gon.public_keyの記述が見つかりません")
        if not (re.search('if.+?==.+?\n',file_text)\
            or re.search('unless.+?!=.+?\n',file_text)\
            or re.search('returnif.+?!=.+?\n',file_text)\
            or re.search('returnunless.+?==.+?\n',file_text)\
                ): errors.append("出品者が自身の商品の購入ページに遷移させないための実装が見つかりません")
        if not (re.search('unless.+?\..+?==nil',file_text)\
            or re.search('unless.+?\..+?\.nil\?',file_text)\
            or re.search('unless.+?\..+?\.blank\?',file_text)\
            or re.search('if.+?\..+?==nil\nrender',file_text)\
            or re.search('if.+?\..+?\.nil\?\nrender',file_text)\
            or re.search('if.+?\..+?\.blank\?\nrender',file_text)\
            or re.search('if.+?\..+?\.present\?',file_text)\
            or re.search('if.+?\..+?\.exists\?\(.+?\)',file_text)\
            or re.search('if.+?\..+?!=nil',file_text)\
            or re.search('if.+?\..+?==nil\nelse',file_text)\
            or re.search('if.+?\..+?\.nil\?\nelse',file_text)\
            or re.search('if.+?\..+?\.blank\?\nelse',file_text)\
            or re.search('unless.+?\..+?\.present\?\nelse',file_text)\
            or re.search('unless.+?\..+?\.exists\?\(.+?\)\nelse',file_text)\
            or re.search('unless.+?\..+?!=nilelse',file_text)\
            or re.search('returnunless.+?\..+?\.present\?\n',file_text)\
            or re.search('returnunless.+?\..+?\.exists\?\(.+?\)\n',file_text)\
                ): errors.append('売り切れ時に購入ページを表示させない処理が見つかりません')
        if "***" in file_text or "sk_" in file_text: errors.append("payjpの秘密鍵に環境変数が使用されていません")
        if len(re.findall('\@.+=.+\.find\(',file_text)) >= 2 : errors.append("商品インスタンスの定義が二回以上記載されています")
        if not ("params[:item_id]" in file_text or "params[:product_id]" in file_text): errors.append("商品インスタンスの定義においてparams[:モデル名_id]が使われていません")
        file_text = re.sub('\n','',file_text)
        if not re.search("\@.+=.+?\.new", file_text): errors.append("インスタンス変数の定義式が見つかりません") 
        
        new_text = re.search("defnew.+?end",file_text)
        if new_text:
            if not new_text.group()[6:-3] == "": warnings.append("newアクションが定義されており、中に記載があります")
        
        create_text = re.search("defcreate.+?endend",file_text)
        if create_text == None:
            errors.append("createアクションが見つかりません")
        else:
            create_text = create_text.group()
            
            if not re.search("\@.+=.+\.new(.+)",create_text) : errors.append("createアクションにformオブジェクトインスタンスが見つかりません")
            if_end_text = re.search("if.+\.valid\?.+else.+endend",create_text)
            if if_end_text == None:
                errors.append("valid?メソッドに対してif文によるエラーハンドリングが見つかりません")
            else:
                if_end_text = if_end_text.group()
                if_else_text = re.search("if.+?else", if_end_text).group()
                # if not "pay_item" in if_else_text: errors.append("購入成功時にpayjpに購入処理をするpay_itemメソッドが見つかりません")
                if not ".save" in if_else_text: errors.append("購入成功時にformオブジェクトのsaveメソッドを動かす処理が見つかりません")
                if not "redirect_toroot_path" in if_else_text: errors.append("購入成功時にトップページに遷移する処理が見つかりません")
                else_end_text = re.search("else.+?endend", if_end_text).group()
                if not ("render:index" in else_end_text or "render'index'" in else_end_text): errors.append("購入失敗時に購入ページを表示させる処理が見つかりません")
        
        private_text = re.search('private.+',file_text)
        if private_text == None:
            errors.append('privateメソッドが定義されていません')
        else:
            private_text = private_text.group()
            order_params_text = re.search('_params.+',private_text)
            if order_params_text == None:
                errors.append('ストロングパラメーターメソッドが定義されていません')
            else:
                order_params_text = order_params_text.group()
                if not re.search('params\.require\(\:.+\)\.permit\(.+\)\.merge\(.+\)',order_params_text):
                    errors.append('ストロングパラメータがparams.require(:○).permit(○).merge(○)の形になっていません')
                else:
                    permit_text = re.search('.permit\(.+?\)',order_params_text).group()
                    merge_text = re.search('.merge\(.+?\)',order_params_text).group()
                    if not permit_text.count(':') == 6: errors.append('ストロングパラメータのpermitの引数の数が'+str(permit_text.count(':'))+'個です(6個必要です)')
                    if not 'user_id:current_user.id' in merge_text: errors.append('ストロングパラメータ内でcurrent_user.idがmergeされていません')
                    if not ('_id:params[:' in merge_text or '_id:@' in merge_text): errors.append('ストロングパラメータ内で商品のid番号がmergeされていません')
                    if not 'token:params[:token]' in merge_text: errors.append('ストロングパラメータ内でtokenがmergeされていません')
    return [errors,warnings]

def check_card_j(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/javascript/') and contains(@title,'.js') and not (contains(@title,'application'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        if "***" in file_text or "pk_" in file_text: errors.append("payjpの公開鍵に環境変数が使用されていません")
        if "console.log" in file_text: errors.append("console.logが残っています")
        if not "turbo:render" in file_text: errors.append("turbo:renderのイベントの記述がありません")
        if not "turbo:load" in file_text: errors.append("turbo:loadのイベントの記述がありません")
    return [errors,warnings]

def check_form_m(driver):
    f_errors = []
    f_warnings = [] #モデルの存在確認は一度に行いたいが、エラーは分けたいので新たにf_errorsを定義
    errors = []
    warnings = []
    models = driver.find_elements(By.XPATH, "//a[contains(@title,'app/models') and not (contains(@title, 'app/models/item.rb') or contains(@title, 'app/models/product.rb') or contains(@title, 'app/models/user.rb') or contains(@title, 'app/models/prefecture.rb')) ]/../../following-sibling::div/div/details/details-menu/a")[::2]
    form_flg = False
    address_flg = False
    order_flg = False
    for model in models:
        url = model.get_attribute("href")
        file_text = get_file_text(url,driver,False)
        if "ActiveHash::Base" in file_text:
            continue
        elif "includeActiveModel::Model" in file_text:
            if form_flg:
                continue
            form_flg = True
            attr_text = re.search("attr_accessor.+\n", file_text)
            if attr_text == None:
                f_errors.append("attr_accessorが見つかりません")
            else:
                attr_text = attr_text.group()
                if attr_text.count(":") < 9: f_errors.append("attr_accessorの属性の指定が"+ str(attr_text.count(":")) +"個しか見つかりません（9個必要です）")
                if attr_text.count(":") > 9: f_warnings.append("attr_accessorの属性の指定が"+ str(attr_text.count(":")) +"個見つかりました（9個より多いです）")
            if not (r"/\A[0-9]{3}-[0-9]{4}\z/" in file_text or r"/\A\d{3}-\d{4}\z/" in file_text): f_errors.append(r"バリデーションに郵便番号の正規表現/\A[0-9]{3}-[0-9]{4}\z/または/\A\d{3}-\d{4}\z/が見つかりません")
            if not (r"/\A[0-9]{10,11}\z/" in file_text or r"/\A\d{10,11}\z/" in file_text or r"^\d{10}$|^\d{11}$" in file_text or r"\A\d{10}$|^\d{11}\z" in file_text): 
                if not (r"/\A[0-9]+\z/" in file_text and "in:10..11" in file_text):
                    f_errors.append("バリデーションに電話番号の正規表現/\A[0-9]{10,11}\z/または/\A\d{10,11}\z/が見つかりません")
            if not re.search("validates.*:user_id",file_text): f_errors.append("user_idに対するバリデーションが見つかりません")
            if not re.search("validates.*:item_id",file_text): f_errors.append("item_idに対するバリデーションが見つかりません")
            if not re.search("validates.*:token",file_text): f_errors.append("tokenに対するバリデーションが見つかりません")
            if not "numericality" in file_text: f_errors.append("都道府県に対するnumericalityのバリデーションが見つかりません（購入のビューでinclude_blankが正しく使用されていれば問題ありません）")
            if ("validates:building" in file_text or "validates:apart" in file_text): f_errors.append("建物名に対するバリデーションが設定されています")
            if file_text.count("presence:true") > 1: f_errors.append("リファクタリングの余地がある可能性があります（presence:trueが" + str(file_text.count("presence:true")) + "回使われています）")
            file_text = re.sub('\n','',file_text)
            save_text = re.search("defsave.+endend",file_text)
            if save_text == None:
                f_errors.append("formオブジェクトにsaveメソッドが見つかりません")
            else:
                save_text = save_text.group()[7:]
                if "token" in save_text: f_errors.append("saveメソッド内にtokenが使われています")
                if not save_text.count("create") == 2:
                    f_errors.append("saveメソッド内にcreateメソッドが2回使われていません")
                else:
                    order_create_text = re.search(".+=.+?create\(.+?_id\)",save_text)
                    if order_create_text == None:
                        f_errors.append("saveメソッド内に購入履歴の変数定義が見つかりません(saveメソッド内の残りのチェックを飛ばします）")
                    else:
                        order_create_text = order_create_text.group()
                        if not ("item_id:item_id" in order_create_text or "product_id:product_id" in order_create_text):f_errors.append("saveメソッド内の購入履歴の保存処理に商品_id: 商品_idが見つかりません")
                        if not "user_id:user_id" in order_create_text:f_errors.append("saveメソッド内の購入履歴の保存処理にuser_id: user_idが見つかりません")
                        if order_create_text.count(",") != 1:f_errors.append("saveメソッド内の購入履歴の保存処理の引数の数が2個ではありません")
                        save_text = save_text[len(order_create_text):]
                        address_create_text = re.search(".+?create\(.+?\)",save_text)
                        valiant_name = re.search(".+=",order_create_text).group()[:-1]
                        if address_create_text == None:
                            f_errors.append("saveメソッド内に住所情報を保存する記述が見つかりません")
                        else:
                            address_create_text = address_create_text.group()
                            if not address_create_text.count(",") == 6: f_errors.append("saveメソッド内の住所の保存処理の引数の数が7個ではありません")
                            if not valiant_name + ".id" in address_create_text: f_errors.append("saveメソッド内の住所の保存処理に購入履歴の変数が使われていません")
        elif ("Address" in file_text.split('\n')[0] or "Ship" in file_text.split('\n')[0] or "Desti" in file_text.split('\n')[0] or "Payment" in file_text.split('\n')[0] or "Deli" in file_text.split('\n')[0] or "Info" in file_text.split('\n')[0]):
            if address_flg:
                continue
            address_flg = True
            if not "belongs_to" in file_text: errors.append("住所モデルにbelongs_toの記述が見つかりません")
            if "has_one" in file_text: errors.append("住所モデルにhas_oneの記述があります")
            if "has_many" in file_text: errors.append("住所モデルにhas_manyの記述があります")
            if "optional:true" in file_text: errors.append("住所モデルにoptional:trueの記述があります")
        elif ("Order" in file_text.split('\n')[0] or "Buy" in file_text.split('\n')[0] or "Purchase" in file_text.split('\n')[0] or "Tran" in file_text.split('\n')[0]):
            if order_flg:
                continue
            order_flg = True
            if not file_text.count("belongs_to") == 2: errors.append("購入履歴モデルのbelongs_toの数が2個ではありません")
            if not file_text.count("has_one") == 1: errors.append("購入履歴モデルのhas_oneの数が1個ではありません")
            if "has_many" in file_text: errors.append("購入履歴モデルにhas_manyの記述があります")
            if "optional:true" in file_text: errors.append("購入履歴モデルにoptional:trueの記述があります")
    if form_flg == False:
        f_errors.append("formオブジェクトファイルが見つかりませんでした")
    if address_flg == False:
        errors.append("配送先住所モデルが見つかりませんでした")
    if order_flg == False:
            errors.append("購入履歴モデルが見つかりませんでした")
    return [f_errors,f_warnings],[errors,warnings]

def check_user_m(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/models/user.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("変更点が見つかりませんでした（購入モデルとのアソシエーションが設定されていない可能性があります）")
    else:
        if not file_text.count("has_many") == 2: errors.append("has_manyが"+str(file_text.count("has_many"))+"個見つかりました（2個必要です）")
        if "belongs_to" in file_text: errors.append("不要なbelongs_toが見つかりました")
        if "has_one" in file_text: errors.append("不要なhas_oneが見つかりました")
    return [errors,warnings]

def check_item_m(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/models/') and (contains(@title,'item.rb') or contains(@title,'product.rb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("変更点が見つかりませんでした（購入モデルとのアソシエーションが設定されていない可能性があります）")
    else:
        if "has_many" in file_text: errors.append("has_manyがあります")
        if not file_text.count("belongs_to") == 6: errors.append("belongs_toが"+str(file_text.count("belongs_to"))+"個見つかりました（activehashを含めると6個必要です）")
        if not file_text.count("has_one:") == 1: errors.append("has_oneが"+str(file_text.count("has_one"))+"個見つかりました（1個必要です）")
    return [errors,warnings]

def check_top_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'index.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした（トップページの売り切れ表示が実装されていない可能性があります）")
    else:
        if "しょう" in raw_text: errors.append("実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。")
        file_text = re.sub('\n','',file_text)
        img_text = re.search("<divclass='item-img-content'>.+?</div><divclass='item-info'>",file_text)
        if img_text == None:
            errors.append("商品画像の記述が見つからなかったのでチェックを中止します（ビューファイルが編集されています）")
        else:
            img_text = img_text.group()
            if not (re.search('unless.+?\..+?==nil',img_text)\
                or re.search('unless.+?\..+?\.nil\?',img_text)\
                or re.search('unless.+?\..+?\.blank\?',img_text)\
                or re.search('if.+?\..+?%>',img_text)\
                or re.search('if.+?\..+?\.present\?',img_text)\
                    ): errors.append('売り切れ時にSoldOutを表示する条件分岐が見つかりません')
    return [errors,warnings]

def check_show_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'show.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした（詳細ページの売り切れ時の表示切り替えが実装されていない可能性があります）")
    else:
        if not r"data:{turbo:false}" in file_text: errors.append(r"data:{turbo:false}の記述が見つかりませんでした（Turbo機能がオフになっていない可能性があります）")
        if "outを表示しましょう" in raw_text: errors.append("実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。")
        file_text = re.sub('\n','',file_text)
        img_text = re.search("<divclass='item-img-content'>.+?</div><divclass='item-price-box'>",file_text)
        if img_text == None:
            errors.append("商品画像の記述が見つからなかったのでSoldOut表示のチェックを中止します")
        else:
            img_text = img_text.group()
            if not (re.search('unless.+?\..+?==nil',img_text)\
                or re.search('unless.+?\..+?\.nil\?',img_text)\
                or re.search('unless.+?\..+?\.blank\?',img_text)\
                or re.search('if.+?\..+?%>',img_text)\
                or re.search('if.+?\..+?\.present\?',img_text)\
                    ): errors.append('売り切れ時にSoldOutを表示する条件分岐が見つかりません')
        button_text = re.search("<spanclass='item-postage'>.+?<divclass='item-explain-box'>",file_text)
        if button_text == None:
            errors.append("htmlが改変されているため編集削除購入ボタンのチェックをスキップします")
        else:
            button_text = button_text.group()
            if not (re.search('if.+?\..+?==nil',button_text)\
                or re.search('if.+?\..+?\.nil\?',button_text)\
                or re.search('if.+?\..+?\.blank\?',button_text)\
                or re.search('unless.+?\..+?%>',button_text)\
                or re.search('unless.+?\..+?\.present\?',button_text)\
                    ): errors.append('売り切れ時に編集削除購入ボタンを表示させない処理が見つかりません')
    return [errors,warnings]

def check_order_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'index.html.erb') and not (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        if "しょう" in raw_text: errors.append("実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。")
        if "item-sample.png" in file_text: errors.append("商品画像が編集されていません")
        if "商品名" in file_text: errors.append("商品名が編集されていません")
        if "999,999,999" in file_text: errors.append("商品価格が編集されていません（'999,999,999'が残っています）")
        if "配送料負担" in file_text: errors.append("配送料負担が編集されていません")
        if "販売価格" in file_text: errors.append("販売価格が編集されていません")
        if not ("<%=form_withmodel:" in file_text or "<%=form_with(model:" in file_text): errors.append("form_withにmodel指定がされていません")
        if not "url:" in file_text: errors.append("form_withにurl指定がされていません")
        if file_text.count("form_with") > 1: errors.append("form_withが二つ以上存在しています")
        if not ("<%=render'shared/error_messages'" in file_text or "<%=renderpartial:'shared/error_messages'" in file_text): errors.append("_error_messagesをrenderする記述が見つかりません")
        if "f.text_field:number" in file_text: errors.append("Payjpv2への移行が完了していません（f.text_field:numberが存在します）")
        if "hoge" in file_text: errors.append("フォーム内にhogeが残っています")
        if "include_blank" in file_text: warnings.append("include_blankが使用されています（モデル、テスト両方においてnumericalityではなくpresence:trueを用いていることを確認してください）")
    return [errors,warnings]

def check_routes(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        warnings.append("購入のルーティングの変更点が見つかりません")
    else:
        if file_text.count("do") < 2: errors.append("ルーティングのネストが見つかりません")
    return [errors,warnings]

def check_order_mig(driver):
    errors = []
    warnings = []
    migs = driver.find_elements(By.XPATH, "//a[contains(@title,'db/migrate') and not (contains(@title,'create_items.rb') or contains(@title,'create_users.rb') or contains(@title,'activestorage')) ]/../../following-sibling::div/div/details/details-menu/a")[::2]
    i = 1
    for mig in migs:
        try:
            url = mig.get_attribute("href")
            file_text = get_file_text(url,driver,False)
            reference_texts = re.findall("t.references.+?\n",file_text)
            if reference_texts == []:
                errors.append("外部キーカラムの記述が見つかりませんでした")
            else:
                for reference_text in reference_texts:
                    if not "foreign_key:true" in reference_text: errors.append(reference_text.replace('\n', '') + "の外部キーカラムにforeign_key:trueが付与されていません")
            building_text = re.search("build.+?\n",file_text)
            if building_text:
                building_text = building_text.group()
                if "null:false" in building_text: errors.append("建物名カラムにNOTNULL制約が適応されています")
        except:
            warnings.append(str(i)+"番目のマイグレーションファイルのチェックに失敗しました")
        i += 1
    return [errors,warnings]

def check_order_f(driver):
    errors = []
    warnings = []
    factories = driver.find_elements(By.XPATH, "//a[contains(@title,'spec/factories/')]/../../following-sibling::div/div/details/details-menu/a")[::2]
    for factory in factories:
        url = factory.get_attribute("href")
        file_text = get_file_text(url,driver,False)
        if not ("{" in file_text and "}" in file_text) or file_text.count("{") < 3: continue
        if file_text.count("{") < 7: 
            if file_text.count("{") != 0: errors.append("値の数が7個必要なのに対し" + str(file_text.count("{")) + "個しかありません")
            if file_text.count("{") == 0: errors.append("factorybotファイルが複数あり特定ができないため、factorybotのチェックをスキップします")
        if "association" in file_text: errors.append("associationが記述されています")
        if "user_id" in file_text: errors.append("user_idが記述されています")
        if "item_id" in file_text: errors.append("item_idが記述されています")
    return [errors,warnings]

def check_order_t(driver):
    errors = []
    warnings = []
    dupli = False
    tests = driver.find_elements(By.XPATH, "//a[contains(@title,'spec/models/') and not (contains(@title,'item_spec.rb') or contains(@title,'user_spec.rb') or contains(@title,'product_spec.rb')) ]/../../following-sibling::div/div/details/details-menu/a")[::2]
    for test in tests:
        url = test.get_attribute("href")
        file_text = get_file_text(url,driver,False)
        if file_text.count("\n") < 10: continue
        if dupli == True:
            errors.append("＊単体テストファイルが重複しています。files changedで上にある単体テストファイルのみをチェックしています")
            continue
        dupli = True
        file_text = re.sub('\n','',file_text)
        before_text = re.search('beforedo.+?end',file_text)
        if before_text == None: 
            errors.append('beforeの記述が見つかりません')
        else:
            before_text = before_text.group()
            if not "FactoryBot.create(:user)" in before_text: errors.append("before内でユーザーがcreateされていません")
            if not ("FactoryBot.create(:item)" in before_text or "FactoryBot.create(:product)" in before_text): errors.append("before内で商品がcreateされていません")
            if not ("FactoryBot.build" in before_text and "user_id" in before_text and ("item_id" in before_text or "product_id" in before_text)): errors.append("before内でformオブジェクトのインスタンスが正しく生成されていない可能性があります")
            file_text = file_text.replace(before_text,'')
        
        valid_text = re.search('context.+?できる.+?endend',file_text)
        if valid_text == None:
            valid_text = re.search('context.+?正常.+?endend',file_text)

        if valid_text: 
            valid_text = valid_text.group()
            if not "tobe_valid" in valid_text: errors.append('be_validのテストが見つかりません')
            if not ("=''" in valid_text or "=nil" in valid_text): errors.append('正常系テスト内に建物名が空でも登録できるテストが無いか、テスト内で建物名に空文字をいれていません')
            if valid_text.count("expect") < 2: errors.append('正常系テストが少ないです')
            file_text = file_text.replace(valid_text,'')
        else:
            errors.append('正常系テストのcontextが見つかりませんでした\m過去アプリと同様に正常系テストをcontextでグループ分けできているかを確認しましょう。')
            if file_text.count("tobe_valid") < 2: errors.append('be_validのテストが足りていません')
            if not (re.search("\.building.*=''",file_text) or re.search("\.building.*=nil",file_text)): errors.append('正常系テスト内に建物名が空でも登録できるテストが無いか、テスト内で建物名に空文字をいれていません')
            
        invalid_text = re.search('context.+?できない.+?endend',file_text)
        if invalid_text == None:
            invalid_text = re.search('context.+?異常.+?endend',file_text)

        if invalid_text: 
            invalid_text = invalid_text.group()
            error_flg = False
            if invalid_text.count("isinvalid") < 4: 
                errors.append('異常系テスト-郵便番号のハイフンなし、電話番号の9桁,12桁,数字以外の中で見つからないものがあります（isinvalidが4個見つかりません）')
                error_flg = True
            if invalid_text.count("can'tbeblank") < 8: 
                errors.append('異常系テスト-空では登録できないが'+ str(invalid_text.count("can'tbeblank")) +"個しか見つかりません（都道府県を含めるとcan'tbeblankが8個必要です）")
                error_flg = True
            if invalid_text.count("expect") < 12: 
                errors.append('異常系テストが'+str(invalid_text.count('expect'))+'個しか見つかりません(12個必要です)')
            elif error_flg:
                errors.append('↑↑異常系テストの数は足りているので、問題ない可能性が高いです↑↑')
        else:
            errors.append('異常系テストのcontextが見つかりませんでした\m過去アプリと同様に異常系テストをcontextでグループ分けできているかを確認しましょう。')
            if file_text.count("isinvalid") < 4: 
                errors.append('異常系テスト-郵便番号のハイフンなし、電話番号の9桁,12桁,数字以外の中で見つからないものがあります（isinvalidが4個見つかりません）')
            if file_text.count("can'tbeblank") < 8: 
                errors.append('異常系テスト-空では登録できないが'+ str(file_text.count("can'tbeblank")) +"個しか見つかりません（都道府県を含めるとcan'tbeblankが8個必要です）")
        
        include_texts = re.findall('include.+?\n',file_text)
        cant_texts = []
        for include_text in include_texts:
            if include_text.count(",") > 0 and include_text.count("'") >=4: 
                errors.append(include_text.replace("\n","")+'においてエラーメッセージが2つ以上適応されています')
            if "can'tbeblank" in include_text:
                cant_texts.append(include_text)
        dup = [x for x in set(cant_texts) if cant_texts.count(x) > 1]
        if len(dup) > 0:
            for text in dup:
                warnings.append(text.replace('\n','')+"のエラーメッセージが別々のinclude内で2回以上使用されています")
    return [errors,warnings]

def check_others(driver):
    errors = []
    warnings = []
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/shared/_error_messages.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append("_error_emssages.html.erbに編集が加えられています")

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/layouts/application.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        pass
    else:
        if 'https://js.pay.jp/v1/' in file_text : errors.append('application.html.erbにPayjpのv1の記述が残っています')
    return errors,warnings

    return [errors,warnings]
