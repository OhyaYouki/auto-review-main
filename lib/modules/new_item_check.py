from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text, check_text, check_comment, auth_check
import re

def check_items_c(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "binding.pry": {"error": True, "message": "binding.pryの記載があります"},
        ".find": {"error": True, "message": "findメソッドが見つかりました（商品詳細機能が実装されている可能性があります）"},
        "Rails.logger.debug" : {"error": True, "message": "Rails.logger.debugが見つかりました\mデバッグ用のRails.logger.debugは本番環境に不要になりますので削除しましょう。"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {}
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {}
    
    # その他の複雑な指摘
    MESSAGES = {
        "incollect_index_action"            : "indexアクションにインスタンス変数の定義があります",
        "no_new_action"                     : "newアクションが定義されていません",
        "incollect_new_action"              : "newアクションにインスタンス変数が正しく定義されていません",
        "no_create_action"                  : "createアクションが定義されていません",
        "incollect_create_action"           : "createアクションにインスタンス変数が正しく定義されていません",
        "no_error_handling"                 : "saveメソッドに対してif文によるエラーハンドリングが実装されていません",
        "no_redirect_root_path"             : "createアクションに保存成功時root_pathにリダイレクトする記述が見つかりません",
        "no_render_new"                     : "createアクションに保存失敗時newのテンプレートを呼び出す記述が見つかりません",
        "no_private_method"                 : "privateメソッドが定義されていません",
        "no_strong_parameter"               : "ストロングパラメーターメソッドが定義されていません",
        "incollect_strong_parameter"        : "ストロングパラメータがparams.require(:○).permit(○).merge(○)の形になっていません",
        "incollect_permit"                  : "ストロングパラメータのpermitの引数の数が違います",
        "incollect_merge"                   : "ストロングパラメータ内でcurrent_user.idがmergeされていません"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/') and contains(@title,'_controller.rb') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        auth_check(file_text,"new",errors,warnings)

        file_text = re.sub('\n','',file_text)
        index_text = re.search('defindex.*?end',file_text)
        if index_text:
            index_text = index_text.group()
            if "@" in index_text: errors.append(MESSAGES["incollect_index_action"])
        
        new_text = re.search('defnew.+?end',file_text)
        if new_text == None: 
            errors.append(MESSAGES["no_new_action"])
        else:
            new_text = new_text.group()
            def_text = re.search('\@.+=.+\.new',new_text)
            if def_text == None: 
                errors.append(MESSAGES["incollect_new_action"])
            else:
                def_text = def_text.group()
        
        create_text = re.search('defcreate.+?endend',file_text)
        if create_text == None: 
            errors.append(MESSAGES["no_create_action"])
        else:
            create_text = create_text.group()
            if not re.search('\@.+=.+\.new(.+_params)',create_text): errors.append(MESSAGES["incollect_create_action"])
            if not re.search('if.+save.+else.+?end',create_text): 
                errors.append(MESSAGES["no_error_handling"])
            else:
                if_text = re.search('if.+?else',create_text).group()
                if not ('redirect_toroot_path' in if_text or 'redirect_toaction::index' in if_text or "redirect_toaction:'index'" in if_text): errors.append(MESSAGES["no_redirect_root_path"])
                else_text = re.search('else.+?endend',create_text).group()
                if not ('render:new' in else_text or "render'new'" in else_text): errors.append(MESSAGES["no_render_new"])
        
        private_text = re.search('private.+?endend',file_text)
        if private_text == None:
            errors.append(MESSAGES["no_private_method"])
        else:
            private_text = private_text.group()
            item_params_text = re.search('def.+_params.+?endend',private_text)
            if item_params_text == None:
                errors.append(MESSAGES["no_strong_parameter"])
            else:
                item_params_text = item_params_text.group()
                if not re.search('params\.require\(\:.+\)\.permit\(.+\)\.merge\(.+\)',item_params_text):
                    errors.append(MESSAGES["incollect_strong_parameter"])
                else:
                    permit_text = re.search('.permit\(.+?\)',item_params_text).group()
                    merge_text = re.search('.merge\(.+?\)',item_params_text).group()
                    if not permit_text.count(':') == 9: errors.append(MESSAGES["incollect_permit"])
                    if not 'user_id:current_user.id' in merge_text: errors.append(MESSAGES["incollect_merge"])
    return [errors,warnings]

def check_price_j(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        ".find": {"error": True, "message": "findメソッドが見つかりました（商品詳細機能が実装されている可能性があります）"},
        "addEventListener('change'" : {"error": True, "message": "changeイベントが見つかりました（inputイベントに変更が必要です）"},
        "Math.round" : {"error": True, "message": "Math.roundが見つかりました（販売利益であればMath.floorで小数点以下を切り下げる必要があります）\mMath.roundだと小数点以下四捨五入になります。要件に沿って小数点以下切り捨ての処理にしましょう。"},
        "0.9" : {"error": True, "message": "0.9をかけている表記が見つかりました（販売手数料と利益の合計値が価格になっているかを確認してください）\m現在の記述ですと例えば価格に555を入力した際に販売手数料と利益の合計値が555に一致しない可能性があります。\n該当する場合は一致するように修正しましょう"},
        "console.log" : {"error": True, "message": "console.log()が残っています"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "addEventListener('input'" : {"error": True, "message": "inputイベントが見つかりませんでした"},
        "Math.floor" : {"error": True, "message": "Math.floorが見つかりませんでした\m要件に沿って販売手数料と販売利益は小数点以下切り捨てで表示されるようにしましょう"},
        "turbo:render" : {"error": True, "message": "turbo:renderのイベントの記述がありません（指摘必須）\m商品の出品に失敗して出品ページに戻った際もjavascriptが動作するよう、renderメソッドに対応したイベントを追加しましょう。\n以下カリキュラムのSTEP2、手順6をご参考ください。\n\n実装に悩んだときのヒント\n商品出品機能\nhttps://master.tech-camp.in/v2/curriculums/8138"},
        "turbo:load" : {"error": True, "message": "turbo:loadのイベントの記述がありません"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/javascript/') and contains(@title,'.js') and not (contains(@title,'application'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        if "Math.floor" in file_text:
            tax_text = re.search(r'.*0\.1.*', file_text)    
            if tax_text and "Math.floor" not in tax_text.group():
                errors.append("0.1をかけている行にMath.floorが使用されていません（販売手数料と利益の合計値が価格になっているかを確認してください）\m現在の記述ですと例えば価格に555を入力した際に販売手数料と利益の合計値が555に一致しない可能性があります。\n該当する場合は一致するように修正しましょう")
    return [errors,warnings]

def check_item_m(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "has_one:" : {"error": True, "message": "has_oneの記述があります"},
        "has_many:" : {"error": True, "message": "has_manyの記述があります"},
        "optional:true" : {"error": True, "message": "optional:trueの記述があります"},
        "includeActiveHash::Associations" : {"error": True, "message": "includeActiveHash::Associationsの記述があります"},
        "validates:user" : {"error": True, "message": "userに対してバリデーションが設定されています"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "belongs_to:user" : {"error": True, "message": "ユーザーとのアソシエーションが見つかりません"},
        "has_one_attached:image" : {"error": True, "message": "has_one_attached:imageが見つかりません"},
        "other_than:" : {"error": True, "message": "activehashカラムに対するother_thanのバリデーションが見つかりません"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "belongs_to": {"error": True, "num":6, "method":"under", "message": "ユーザーまたはactivehashとのアソシエーションが足りていません（belongs_toが6個必要です）"}
    }
    
    # その他の複雑な指摘
    MESSAGES = {
        "no_numericality"               : "priceにnumericalityバリデーションが見つかりません",
        "no_only_integer"               : "priceのnumericalityにonly_integer:trueが見つかりません",
        "no_over_300_validation"        : "priceのnumericalityバリデーションに300以上の制限が見つかりません",
        "no_under_9999999_validation"   : "priceのnumericalityバリデーションに9_999_999以下の制限が見つかりません",
        "use_with"                      : "価格に対して正規表現が適応されています（integer型に正規表現は無効です）",
        "not_found_validation"          : "価格に対するバリデーションが見つかりません"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/models') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        price_texts = re.findall('validates:.*?price.+?\n',file_text)
        price_text = ''
        for text in price_texts:
            if text[-2] == ",":
                if re.search(text + ".+?\n", file_text).group()[-2] == ",":
                    text = re.search(text + ".+?\n.+?\n", file_text).group()
                else:
                    text = re.search(text + ".+?\n", file_text).group()
            price_text += text
        if price_text:
            if not "numericality:" in price_text: 
                errors.append(MESSAGES["no_numericality"])
            else:
                if not "only_integer:true" in price_text: errors.append(MESSAGES["no_only_integer"])
                if not (r"inclusion:{in:300..9_999_999}" in price_text or r"inclusion:{in:300..9999999}" in price_text):
                    if not "greater_than_or_equal_to:300" in price_text: errors.append(MESSAGES["no_over_300_validation"])
                    if not ("less_than_or_equal_to:9_999_999" in price_text or "less_than_or_equal_to:9999999" in price_text or "less_than:10_000_000" in price_text or "less_than:10000000" in price_text): errors.append(MESSAGES["no_under_9999999_validation"])
                if "with:" in price_text: errors.append(MESSAGES["use_with"])
        else:
            errors.append(MESSAGES["not_found_validation"])

    return [errors,warnings]

def check_activehash_m(driver):
    errors = []
    warnings = []
    MESSAGES = {
        "less_activehash_model": "activehashモデルが不足しています",
        "incollect_prefecture_model": "発送元の地域モデルのself.dataの中身が編集されている可能性があります",
        "incollect_category_model": "カテゴリーモデルのself.dataの中身が編集されている可能性があります",
        "incollect_fee_status_model": "配送料の負担モデルのself.dataの中身が編集されている可能性があります",
        "incollect_sales_status_model": "配送料の負担モデルのself.dataの中身が編集されている可能性があります",
        "incollect_schedule_model":  "発送までの日数モデルのself.dataの中身が編集されている可能性があります"
    }

    models = driver.find_elements(By.XPATH, "//a[contains(@title,'app/models') and not (contains(@title, 'app/models/item.rb') or contains(@title, 'app/models/product.rb') or contains(@title, 'app/models/user.rb')) ]/../../following-sibling::div/div/details/details-menu/a")[::2]
    if len(models) < 5: errors.append(MESSAGES["less_activehash_model"])
    for model in models:
        url = model.get_attribute("href")
        file_text = get_file_text(url,driver,False)
        file_text = re.sub('\n','',file_text)
        if "北海道" in file_text:
            if not "self.data=[{id:1,name:'---'},{id:2,name:'北海道'},{id:3,name:'青森県'},{id:4,name:'岩手県'},{id:5,name:'宮城県'},{id:6,name:'秋田県'},{id:7,name:'山形県'},{id:8,name:'福島県'},{id:9,name:'茨城県'},{id:10,name:'栃木県'},{id:11,name:'群馬県'},{id:12,name:'埼玉県'},{id:13,name:'千葉県'},{id:14,name:'東京都'},{id:15,name:'神奈川県'},{id:16,name:'新潟県'},{id:17,name:'富山県'},{id:18,name:'石川県'},{id:19,name:'福井県'},{id:20,name:'山梨県'},{id:21,name:'長野県'},{id:22,name:'岐阜県'},{id:23,name:'静岡県'},{id:24,name:'愛知県'},{id:25,name:'三重県'},{id:26,name:'滋賀県'},{id:27,name:'京都府'},{id:28,name:'大阪府'},{id:29,name:'兵庫県'},{id:30,name:'奈良県'},{id:31,name:'和歌山県'},{id:32,name:'鳥取県'},{id:33,name:'島根県'},{id:34,name:'岡山県'},{id:35,name:'広島県'},{id:36,name:'山口県'},{id:37,name:'徳島県'},{id:38,name:'香川県'},{id:39,name:'愛媛県'},{id:40,name:'高知県'},{id:41,name:'福岡県'},{id:42,name:'佐賀県'},{id:43,name:'長崎県'},{id:44,name:'熊本県'},{id:45,name:'大分県'},{id:46,name:'宮崎県'},{id:47,name:'鹿児島県'},{id:48,name:'沖縄県'}]" in file_text: 
                if not "self.data=[{id:0,name:'---'},{id:1,name:'北海道'},{id:2,name:'青森県'},{id:3,name:'岩手県'},{id:4,name:'宮城県'},{id:5,name:'秋田県'},{id:6,name:'山形県'},{id:7,name:'福島県'},{id:8,name:'茨城県'},{id:9,name:'栃木県'},{id:10,name:'群馬県'},{id:11,name:'埼玉県'},{id:12,name:'千葉県'},{id:13,name:'東京都'},{id:14,name:'神奈川県'},{id:15,name:'新潟県'},{id:16,name:'富山県'},{id:17,name:'石川県'},{id:18,name:'福井県'},{id:19,name:'山梨県'},{id:20,name:'長野県'},{id:21,name:'岐阜県'},{id:22,name:'静岡県'},{id:23,name:'愛知県'},{id:24,name:'三重県'},{id:25,name:'滋賀県'},{id:26,name:'京都府'},{id:27,name:'大阪府'},{id:28,name:'兵庫県'},{id:29,name:'奈良県'},{id:30,name:'和歌山県'},{id:31,name:'鳥取県'},{id:32,name:'島根県'},{id:33,name:'岡山県'},{id:34,name:'広島県'},{id:35,name:'山口県'},{id:36,name:'徳島県'},{id:37,name:'香川県'},{id:38,name:'愛媛県'},{id:39,name:'高知県'},{id:40,name:'福岡県'},{id:41,name:'佐賀県'},{id:42,name:'長崎県'},{id:43,name:'熊本県'},{id:44,name:'大分県'},{id:45,name:'宮崎県'},{id:46,name:'鹿児島県'},{id:47,name:'沖縄県'}]" in file_text: 
                    warnings.append(MESSAGES["incollect_prefecture_model"])
        elif "メンズ" in file_text:
            if not "self.data=[{id:1,name:'---'},{id:2,name:'レディース'},{id:3,name:'メンズ'},{id:4,name:'ベビー・キッズ'},{id:5,name:'インテリア・住まい・小物'},{id:6,name:'本・音楽・ゲーム'},{id:7,name:'おもちゃ・ホビー・グッズ'},{id:8,name:'家電・スマホ・カメラ'},{id:9,name:'スポーツ・レジャー'},{id:10,name:'ハンドメイド'},{id:11,name:'その他'}]" in file_text:
                if not "self.data=[{id:0,name:'---'},{id:1,name:'レディース'},{id:2,name:'メンズ'},{id:3,name:'ベビー・キッズ'},{id:4,name:'インテリア・住まい・小物'},{id:5,name:'本・音楽・ゲーム'},{id:6,name:'おもちゃ・ホビー・グッズ'},{id:7,name:'家電・スマホ・カメラ'},{id:8,name:'スポーツ・レジャー'},{id:9,name:'ハンドメイド'},{id:10,name:'その他'}]" in file_text:
                    warnings.append(MESSAGES["incollect_category_model"])
        elif "着払い" in file_text:
            if not "self.data=[{id:1,name:'---'},{id:2,name:'着払い(購入者負担)'},{id:3,name:'送料込み(出品者負担)'}]" in file_text:
                if not "self.data=[{id:0,name:'---'},{id:1,name:'着払い（購入者負担）'},{id:2,name:'送料払み（出品者負担）'}]" in file_text:
                    warnings.append(MESSAGES["incollect_fee_status_model"])
        elif "新品" in file_text:
            if not "self.data=[{id:1,name:'---'},{id:2,name:'新品・未使用'},{id:3,name:'未使用に近い'},{id:4,name:'目立った傷や汚れなし'},{id:5,name:'やや傷や汚れあり'},{id:6,name:'傷や汚れあり'},{id:7,name:'全体的に状態が悪い'}]" in file_text:
                if not "self.data=[{id:0,name:'---'},{id:1,name:'新品・未使用'},{id:2,name:'未使用品に近い'},{id:3,name:'目立った傷や汚れなし'},{id:4,name:'やや傷や汚れあり'},{id:5,name:'傷や汚れあり'},{id:6,name:'全体的に状態が悪い'}]" in file_text:
                    warnings.append(MESSAGES["incollect_sales_status_model"])
        elif "で発送" in file_text:
            if not "self.data=[{id:1,name:'---'},{id:2,name:'1~2日で発送'},{id:3,name:'2~3日で発送'},{id:4,name:'4~7日で発送'}]" in file_text:
                if not "self.data=[{id:0,name:'---'},{id:1,name:'1~2日で発送'},{id:2,name:'2~3日で発送'},{id:3,name:'4~7日で発送'}]" in file_text:
                    warnings.append(MESSAGES["incollect_schedule_model"])
    return [errors,warnings]

def check_index_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "user_signed_in?" : {"error": True, "message": "ログイン有無を確認する条件分岐があります"},
        "each" : {"error": True, "message": "一覧機能が実装されています(コントローラにも実装されている可能性があります)"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
    }
    
    # その他の複雑な指摘
    MESSAGES = { 
        "no_new_link": "「出品する」のリンクが見つかりません" 
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'index.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした（トップページの「出品する」ボタンのリンクが実装されていない可能性があります）")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        if not ("'items/new',class:'purchase-btn'" in file_text or "'/items/new',class:'purchase-btn'" in file_text or "new_item_path,class:'purchase-btn'" in file_text or "'/products/new',class:'purchase-btn'" in file_text or "new_product_path,class:'purchase-btn'" in file_text): 
            errors.append(MESSAGES["no_new_link"])
    return [errors,warnings]

def check_new_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "hoge" : {"error": True, "message": "フォーム内にhogeが残っています。\m◎フォーム内に未実装項目がないか確認しましょう。\n\n■理由\nフォーム内に未実装のhogeが残っている為です。"},
        "prompt:" : {"error": False, "message": "collection_selectにおいてprompt:が使用されています（バリデーションやテストに矛盾がないか確認してください）"},
        "include_blank" : {"error": False, "message": "include_blankが使用されています（モデル、テスト両方においてnumericalityではなくpresence:trueを用いていることを確認してください）"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "form_with": {"error": True, "num":1, "method":"over", "message": "form_withが二つ以上存在しています\m◎form_withが二つ以上存在しているので一つにしましょう。"}
    }
    
    # その他の複雑な指摘
    MESSAGES = { 
        "no_model_in_form": "form_withにmodel指定がされていません",
        "no_render_error_messages": "_error_messagesをrenderする記述が見つかりません",
        "no_back_link": "戻るボタンにトップページのパスが設定されていません"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'new.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        errors = check_comment(raw_text,errors)
        if not ("<%=form_withmodel:@" in file_text or "<%=form_with(model:@" in file_text): errors.append(MESSAGES["no_model_in_form"])
        if not ("<%=render'shared/error_messages'" in file_text or "<%=renderpartial:'shared/error_messages'" in file_text): errors.append(MESSAGES["no_render_error_messages"])
        if not ("<%=link_to'もどる',root_path,class:'back-btn'%>" in file_text or "<%=link_to'もどる','/',class:'back-btn'%>" in file_text): errors.append(MESSAGES["no_back_link"])
    return [errors,warnings]

def check_routes(driver):
    errors = []
    warnings = []
    
    MESSAGES = {
        "no_changes": "出品のルーティングの変更点が見つかりません",
        "no_create_route": "出品に対するルーティングが見つかりません"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        warnings.append("出品のルーティングの変更点が見つかりません")
    else:
        if not ("resources:items" in file_text or "resources:products" in file_text): errors.append(MESSAGES["no_changes"])
        else:
            if "only:" in file_text and not ":new,:create" in file_text: errors.append(MESSAGES["no_create_route"])
    return [errors,warnings]

def check_item_mig(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "t.integer": {"error": True, "num":6, "method":"not_equal", "message": "integer型のカラムの数が6個ではありません"},
        "t.text": {"error": True, "num":1, "method":"not_equal", "message": "text型のカラムの数が1個ではありません"},
        "t.string": {"error": True, "num":1, "method":"not_equal", "message": "string型のカラムの数が1個ではありません"},
        "t.references": {"error": True, "num":1, "method":"not_equal", "message": "references型のカラムの数が1個ではありません"},
        "null:false": {"error": True, "num":9, "method":"not_equal", "message": "null:falseの数が正しくありません\mNOTNULL制約を追加しましょう。\n\n■理由\nNOTNULL制約のオプションが付いていないと、空文字を登録できてしまうためになります。"},
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
        "no_reference_text": "外部キーカラムの記述が見つかりませんでした",
        "no_foreign_key_true": "外部キーカラムにforeign_key:trueが付与されていません"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'db/migrate') and (contains(@title,'create_items.rb') or contains(@title,'create_products.rb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,False,False,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        reference_text = re.search("t.references.+?\n",raw_text)
        if reference_text == None:
            errors.append(MESSAGES["no_reference_text"])
        else:
            reference_text = reference_text.group()
            if not "foreign_key:true" in reference_text: errors.append(MESSAGES["no_foreign_key_true"])

    return [errors,warnings]

def check_item_f(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "{": {"error": True, "num":8, "method":"under", "message": "カラムの数が少ないです"}
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
        "incollect_image": "image{---}の記述があります",
        "no_image": "画像がattachされていません",
        "no_association_user": "association:userが見つかりません",
        "use_user_id": "ユーザーがassociationではなくuser_idで設定されています",
        "use_0_or_1_to_activehash": "activehashのidに0か1が設定されています"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'spec/factories') and (contains(@title,'items.rb') or contains(@title,'products.rb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        if not "image{Rack::test::UploadedFile.new(Rails.root.join('app','assets',":
            if re.search("image\{.+?\}",file_text): errors.append(MESSAGES["incollect_image"])
            if not ".image.attach" in file_text: errors.append(MESSAGES["no_image"])
        if not ("user\n" in file_text or "association:user\n"): errors.append(MESSAGES["no_association_user"])
        for activehash in re.findall(".+_id{.+?}",file_text):
            if "user_id" in activehash:
                errors.append(MESSAGES["use_user_id"])
                continue
            if re.search("{.+}",activehash).group()[1:-1].replace("\'","") in [0,1]:
                errors.append(MESSAGES["use_0_or_1_to_activehash"])
    return [errors,warnings]

def check_item_t(driver):
    errors = []
    warnings = []

    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {}

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {}
    
    # 重複した記述がある場合の指摘
    CHECK_NUM_TEXT = {
        "FactoryBot.build": {"error": True, "num":1, "method":"over", "message": "FactoryBot.buildが2つ以上記載されています\mbeforeブロックの中でインスタンスの生成が行えているため、上記は削除しましょう。\n他のit内の同記述も削除しましょう。"}
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'spec/models/') and (contains(@title,'item') or contains(@title,'product')) ]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        file_text = re.sub('\n','',file_text)
        before_text = re.search('beforedo.+?end',file_text)
        if before_text == None: 
            errors.append('beforeの記述が見つかりません')
        else:
            before_text = before_text.group()
            if not ('@item=FactoryBot.build(:item)' in before_text or '@product=FactoryBot.build(:product)' in before_text): 
                if 'FactoryBot.create' in before_text:
                    errors.append("before内でbuildではなくcreateメソッドが使用されています")
                else:
                    errors.append('before内にfactorybotを用いたインスタンス変数の定義が見つかりません')
            file_text = file_text.replace(before_text,'')

        valid_text = re.search('context.+?できる.+?endend',file_text)
        if valid_text == None:
            valid_text = re.search('context.+?正常.+?endend',file_text)

        if valid_text: 
            valid_text = valid_text.group()
            if not ('expect(@item).tobe_valid' in valid_text or 'expect(@product).tobe_valid' in valid_text): errors.append('be_validのテストが見つかりません')
            file_text = file_text.replace(valid_text,'')
        else:
            errors.append('正常系テストのcontextが見つかりませんでした\m過去アプリと同様に正常系テストをcontextでグループ分けできているかを確認しましょう。')
            if not ('expect(@item).tobe_valid' in file_text or 'expect(@product).tobe_valid' in file_text): errors.append('be_validのテストが見つかりません')

        invalid_text = re.search('context.+?できない.+?endend',file_text)
        if invalid_text == None:
            invalid_text = re.search('context.+?異常.+?endend',file_text)

        if invalid_text: 
            invalid_text = invalid_text.group()
            error_flg = False
            if invalid_text.count("can'tbeblank") < 9: 
                errors.append("異常系テスト-空では登録できないが"+ str(invalid_text.count("can'tbeblank"))+"個しか見つかりません（activehashを含めるとcan'tbeblankが9個必要です）")
                error_flg = True
                if invalid_text.count("mustbeotherthan") < 5: 
                    errors.append('異常系テスト-activehashの未選択が不足している可能性があります')
            if "='---'" in invalid_text or "='--'" in invalid_text:
                errors.append('異常系テスト-activehashの未選択テストにおいて値に"---"が格納されている可能性があります')
            if not ("_id=0" in invalid_text or "_id='0'" in invalid_text or "_id=1" in invalid_text or "_id='1'" in invalid_text):
                errors.append('異常系テスト-activehashの未選択テストにおいて値に0または1が格納されていない可能性があります')
            if not 'mustbegreater' in invalid_text: 
                errors.append('異常系テスト-価格が300未満が見つかりません（mustbegreaterのエラーメッセージが見つかりません）')
                error_flg = True
            if not 'mustbeless' in invalid_text: 
                errors.append('異常系テスト-価格が9_999_999超えが見つかりません（mustbelessのエラーメッセージが見つかりません）')
                error_flg = True
            if not 'isnotanumber' in invalid_text: 
                errors.append('異常系テスト-価格が半角数値ではないが見つかりません（notanumberのエラーメッセージが見つかりません）')
                error_flg = True
            if not 'Usermustexist' in invalid_text: 
                errors.append('異常系テスト-userが紐づいていないが見つかりません（Usermustexisのエラーメッセージが見つかりません）')
                error_flg = True
            if invalid_text.count("expect") < 13: 
                errors.append('異常系テストが'+str(invalid_text.count('expect'))+'個しか見つかりません(13個必要です)')
            elif error_flg:
                errors.append('↑↑異常系テストの数は足りているので、問題ない可能性が高いです↑↑')
        else:
            errors.append('異常系テストのcontextが見つかりませんでした\m過去アプリと同様に異常系テストをcontextでグループ分けできているかを確認しましょう。')
            if file_text.count("can'tbeblank") < 9: 
                errors.append("異常系テスト-空では登録できないが"+ str(file_text.count("can'tbeblank"))+"個しか見つかりません（activehashを含めるとcan'tbeblankが9個必要です）")
                if file_text.count("mustbeotherthan") < 5: 
                    errors.append('異常系テスト-activehashの未選択が不足している可能性があります')
            if "='---'" in file_text or "='--'" in file_text:
                errors.append('異常系テスト-activehashの未選択テストにおいて値に"---"が格納されている可能性があります')
            if not ("_id=0" in file_text or "_id='0'" in file_text or "_id=1" in file_text or "_id='1'" in file_text):
                errors.append('異常系テスト-activehashの未選択テストにおいて値に0または1が格納されていない可能性があります')
            if not 'mustbegreater' in file_text: 
                errors.append('異常系テスト-価格が300未満が見つかりません（mustbegreaterのエラーメッセージが見つかりません）')
            if not 'mustbeless' in file_text: 
                errors.append('異常系テスト-価格が9_999_999超えが見つかりません（mustbelessのエラーメッセージが見つかりません）')
            if not 'isnotanumber' in file_text: 
                errors.append('異常系テスト-価格が半角数値ではないが見つかりません（notanumberのエラーメッセージが見つかりません）')
            if not 'Usermustexist' in file_text: 
                errors.append('異常系テスト-userが紐づいていないが見つかりません（Usermustexisのエラーメッセージが見つかりません）')

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
    
    MESSAGES = {
        "change_application_controller": "application_controller.rbに編集が加えられています",
        "change_another_view": "indexとnew以外のビューファイルに編集が加えられています",
        "change_error_messages": "_error_mssages.html.erbに編集が加えられています"
    }
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/application_controller.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        warnings.append(MESSAGES["change_application_controller"])
    
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and (contains(@title,'show.html.erb') or contains(@title,'create.html.erb') or contains(@title,'edit.html.erb') or contains(@title,'update.html.erb') or contains(@title,'destroy.html.erb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        warnings.append(MESSAGES["change_another_view"])
        
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/shared/_error_messages.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        warnings.append(MESSAGES["change_error_messages"])
    return [errors,warnings]