from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text, check_text
import re

def check_items_c(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        ".find" : {"error": True, "message": "findメソッドが見つかりました\mもし商品詳細機能を実装されている場合は、次のブランチの実装内容になりますので本ブランチ上では全てコメントアウトか削除しましょう。"},
        "Rails.logger.debug" : {"error": True, "message": "Rails.logger.debugが見つかりました\mデバッグ用のRails.logger.debugは本番環境に不要になりますので削除しましょう。"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
        "authenticate_user_all"             : "authenticate_user!が全てのアクションに適応されている可能性があります\m要件に沿って未ログイン時にトップページに遷移できるかを確認し、もし期待通りでない場合は修正しましょう。",
        "use_user_signed_in"                : "user_signed_in?がnewアクションに適応されているか確認してください\m要件に沿って未ログイン時に出品ページに遷移できないことを確認し、もし期待通りでない場合は修正しましょう。",
        "no_authenticate_user"              : "authenticate_user!及びuser_signed_in?が見つかりませんでした\m要件に沿ってログイン時に出品ページに遷移できること及び未ログイン時でもトップページに遷移できることを確認し、もし期待通りでない場合は修正しましょう。",
        "incollect_authenticate_user_only"  : "authenticate_user!メソッドのonlyにindexが見つかりませんでした\m要件に沿って未ログイン時にトップページに遷移できることを確認し、もし期待通りでない場合は修正しましょう。",
        "incollect_authenticate_user_except": "authenticate_user!メソッドのexceptにindexが含まれています\m要件に沿って未ログイン時にトップページに遷移できることを確認し、もし期待通りでない場合は修正しましょう。",
        "no_index_action"                   : "indexアクションが見つかりませんでした\mindexアクションが正しく定義されているかを確認しましょう。",
        "dup_valiable"                      : "indexアクションにインスタンス変数が二つ以上見つかりました\mトップページでは全ての商品を格納するインスタンス変数が一つだけあれば一覧表示ができるため、定義式も1行にまとめましょう。",
        "no_valiable"                       : "indexアクションにインスタンス変数が見つかりませんでした\m商品の一覧を表示するためのインスタンス変数をindexアクションに定義できているか確認してください。",
        "incorrect_order"                   : "出品された順の並び替えが正しくない可能性があります\m要件に沿ってトップページで商品が出品された順に並んでいるかを確認し、期待通りでない場合は修正しましょう。"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/') and contains(@title,'_controller.rb') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした\m商品コントローラーの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        auth_text = re.search('before_action:authenticate_user!.+?\n',file_text)
        if auth_text == None:
            if re.search('before_action:authenticate_user!\n',file_text):
                errors.append(MESSAGES["authenticate_user_all"])
            elif "user_signed_in?" in file_text:
                warnings.append(MESSAGES["use_user_signed_in"])
            else:
                errors.append(MESSAGES["no_authenticate_user"])
        else:
            auth_text = auth_text.group()
            if "only:" in auth_text:
                if ":index" in auth_text: errors.append(MESSAGES["incollect_authenticate_user_only"])
            if "except:" in auth_text:
                if not ":index" in auth_text: errors.append(MESSAGES["incollect_authenticate_user_except"])

        file_text = re.sub('\n', '', file_text)
        index_text = re.search('defindex.+?end', file_text)
        if index_text is None: 
            errors.append(MESSAGES["no_index_action"])
            return [errors,warnings]
        index_text = index_text.group()
        if index_text.count("@") > 1:
            errors.append(MESSAGES["dup_valiable"])

        def_text = re.search('\@.+=.+\..+',index_text)
        if def_text is None: 
            errors.append(MESSAGES["no_valiable"])
            return [errors,warnings]
        def_text = def_text.group().lower()
        order_patterns = [
            "order('created_atdesc')",
            "order(created_atdesc)",
            "order('created_at::desc')",
            "order(created_at::desc)",
            "order(created_at: 'desc')",
        ]
        if not any(pattern in def_text for pattern in order_patterns):
            errors.append(MESSAGES["incorrect_order"])

    return [errors,warnings]

def check_index_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "<%=image_tag'item-sample.png',class:'item-img'%>" : {"error": True, "message": "商品画像が正しく表示されていない可能性があります\mトップページで出品した商品の画像が見本通りに表示されているかを確認し、もし期待通りでない場合は修正しましょう。"},
        "<%='商品名'%>" : {"error": True, "message": "商品名が正しく表示されていない可能性があります\mトップページで出品した商品の名前が見本通りに表示されているかを確認し、もし期待通りでない場合は修正しましょう。"},
        "<%='販売価格'%>" : {"error": True, "message": "販売価格が正しく表示されていない可能性があります\mトップページで出品した商品の販売価格が見本通りに表示されているかを確認し、もし期待通りでない場合は修正しましょう。"},
        "<%='配送料負担'%>" : {"error": True, "message": "配送料負担が正しく表示されていない可能性があります\mトップページで出品した商品の配送料負担が見本通りに表示されているかを確認し、もし期待通りでない場合は修正しましょう。"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "each" : {"error": True, "message": "eachメソッドが見つかりませんでした\mトップページで出品した商品が全て表示されているかを確認し、もし期待通りでない場合は修正しましょう。"}
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "link_to'#'do": {"error": True, "num":2, "method":"under", "message": "link_toに変更が加えられている可能性があります\mもしlink_toのパスを詳細ページへのパスに変更されている場合は、次の商品詳細機能ブランチでの実装内容になるため本ブランチでは元の'#'のままにしましょう。"}
    }

    # その他の複雑な指摘
    MESSAGES = { 
        "no_dammy_item": "ダミー画像表示のための条件分岐が見つかりませんでした\m要件に沿ってトップページで商品が一つもない時のみダミー商品が表示されるかを確認し、もし期待通りでない場合は修正しましょう。",
        "stop_check_fee": "配送料負担の表示が正しくない可能性があります\m要件に沿ってトップページで商品の配送料負担が見本通りに表示されるかを確認し、もし期待通りでない場合は修正しましょう。",
        "no_name_to_fee": "配送料負担の表示が正しくない可能性があります\m要件に沿ってトップページで商品の配送料負担が見本通りに表示されるかを確認し、もし期待通りでない場合は修正しましょう。",
        "guidance_message": "実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。",
        "sold_out": "売り切れ表示の条件式が実装されている可能性があります\mもし購入機能をまだ実装していない場合は売り切れ表示の実装は動作確認ができないため、売り切れ表示の実装を元に戻しましょう。"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'index.html.erb') and (contains(@title,'items') or contains(@title,'products'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした\mビューファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)

        file_text = re.sub('\n','',file_text)
        if not (re.search('<%if.+(count>0|length!=0|\[0\]!=nil|present\?|length==0|\[0\]==nil|blank\?|empty\?|exists\?)',file_text) or re.search('<%unless\@.+?\.exists\?%>',file_text)): errors.append(MESSAGES["no_dammy_item"])
        if not "<%='配送料負担'%>" in file_text:
            partial_text = re.search("円<br><%=.+?%></span>",file_text)
            if partial_text == None: 
                errors.append(MESSAGES["stop_check_fee"])
            else:
                partial_text = partial_text.group()

                if not ".name" in partial_text: errors.append(MESSAGES["no_name_to_fee"])
        guidance_messages = ["展開できるようにしましょう", "ダミー商品が表示されるようにしましょう", "表示されないようにしましょう"]
        if any(msg in raw_text for msg in guidance_messages):
            errors.append(MESSAGES["guidance_message"])
        if not "outを表示しましょう" in raw_text:
            errors.append(MESSAGES["sold_out"])
    return [errors,warnings]

def check_others(driver):
    errors = []
    warnings = []
    MESSAGES = {
        "authenticate_in_application": "authenticate_user!がapplication_controllereに指定されています\mauthenticate_user!は他のコントローラーに記述しましょう。\n\n■理由\n こちらをapplication_controllerに記述してしまうと全てのコントローラーに影響を与えてしまい、意図しない挙動を引き起こす怖れがある為です。",
        "change_another_view": "indexとnew以外のビューファイルに編集が加えられています"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/application_controller.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        pass
    else:
        if "authenticate_user!" in file_text: errors.append(MESSAGES["authenticate_in_application"])
    
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and (contains(@title,'new.html.erb') or contains(@title,'show.html.erb') or contains(@title,'create.html.erb') or contains(@title,'edit.html.erb') or contains(@title,'update.html.erb') or contains(@title,'destroy.html.erb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append(MESSAGES["change_another_view"])
    return [errors,warnings]