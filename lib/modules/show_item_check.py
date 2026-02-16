from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text, check_text
import re

def check_items_c(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "binding.pry": {"error": True, "message": "binding.pryの記載があります"},
        "Rails.logger.debug" : {"error": True, "message": "Rails.logger.debugが見つかりました\mデバッグ用のRails.logger.debugは本番環境に不要になりますので削除しましょう。"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {}
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {}
    
    # その他の複雑な指摘
    MESSAGES = {
        "authenticate_user_all"             : "authenticate_user!が全てのアクションに適応されています",
        "use_user_signed_in"                : "user_signed_in?がshowクションに適応されていないことを確認してください",
        "no_authenticate_user"              : "authenticate_user!及びuser_signed_in?が見つかりませんでした",
        "incollect_authenticate_user_only"  : "authenticate_user!メソッドのonlyにshowが含まれています",
        "incollect_authenticate_user_except": "authenticate_user!メソッドのexceptにshowが含まれていません",
        "no_show_action"                    : "showアクションが定義されていません",
        "use_find_by"                       : "インスタンス変数の定義にfind_byメソッドが用いられています（任意修正）",
        "incollect_show_action"             : "showアクションにインスタンス変数が見つかりません（あるいは既にbefore_actionでまとめられています）"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/') and contains(@title,'_controller.rb') and (contains(@title,'items') or contains(@title,'products'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) 
    except:
        errors.append("ファイルが見つかりませんでした")
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
                if ":show" in auth_text: errors.append(MESSAGES["incollect_authenticate_user_only"])
            if "except:" in auth_text:
                if not ":show" in auth_text: errors.append(MESSAGES["incollect_authenticate_user_except"])
        file_text = re.sub('\n','',file_text)
        show_text = re.search('defshow.+?end',file_text)
        if show_text == None: 
            errors.append(MESSAGES["no_show_action"])
        else:
            show_text = show_text.group()
            if not re.search('\@.+=.+\.find\(params\[:id]\)',show_text): 
                if re.search('\@.+=.+\.find_by\(params\[:id]\)',show_text):
                    warnings.append(MESSAGES["use_find_by"])
                else:
                    warnings.append(MESSAGES["incollect_show_action"])

    return [errors,warnings]

def check_index_v(driver):
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
        "<%=link_to'#'do%>": {"error": True, "num":1, "method":"over", "message": "詳細ページへのパスが指定されていません(link_to'#'doが二つ以上あります)"}
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
    }
    
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'index.html.erb') and (contains(@title,'items') or contains(@title,'products'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
    return [errors,warnings]

def check_show_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "<%='商品名'%>" : {"error": True, "message": "商品名が設定がされてません"},
        "<%=image_tag'item-sample.png',class:'item-box-img'%>" : {"error": True, "message": "商品画像が設定がされてません"},
        "¥999,999,999" : {"error": True, "message": "商品の値段が設定がされてません"},
        "<spanclass='item-price'></span>" : {"error": True, "message": "商品の値段が設定がされてません"},
        "<%@" : {"error": True, "message": "「<%=」の「=」が抜けている記述があります"},
        "<%='配送料負担'%>" : {"error": True, "message": "配送料負担が設定されてません"},
        "<%='商品説明'%>" : {"error": True, "message": "商品の説明が設定されてません"},
        "<%='出品者名'%>" : {"error": True, "message": "出品者名が設定されてません"},
        "<ahref='#'class='another-item'><%='商品のカテゴリー名'%>をもっと見る</a>" : {"error": True, "message": "ページ下部のカテゴリー名が設定がされてません\m※該当箇所にコメントができないためこちらに失礼いたします。\n\n詳細ページ最下部の以下記述においても保存した商品のカテゴリー名が表示されるようにしましょう。\nまた、実装後は上下のコメントアウトの削除もお忘れなくお願いします。\n\n`<%='商品のカテゴリー名'%>をもっと見る`"}
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "user_signed_in?" : {"error": True, "message": "user_signed_in?が使用されていません"},
        "'商品の編集','#'" : {"error": True, "message": "編集ボタンのリンク先が編集されています"},
        "'削除','#'" : {"error": True, "message": "削除ボタンのリンク先が編集されています"},
        "'購入画面に進む','#'" : {"error": True, "message": "購入ボタンのリンク先が編集されています"}
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "user_signed_in?": {"error": True, "num":1, "method":"over", "message": "user_signed_in?が二回以上使用されています"}
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
        "incollect_btn_method": "編集・削除・購入ボタンを表示させる条件分岐が正しくない可能性があります",
        "stop_name_check_postage": "不要な編集が加えられているため配送料負担に.nameがついているかのチェックを中断しました",
        "stop_name_check_category": "不要な編集が加えられているためページ下部のカテゴリーに.nameがついているかのチェックを中断しました",
        "incollect_postage": "配送料負担表示に対して.nameがついていません",
        "incollect_category": "ページ下部のカテゴリーに対して.nameがついていません",
        "no_yen": "価格表示に¥の表記が見つかりません",
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'show.html.erb') and (contains(@title,'items') or contains(@title,'products'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
        file_text = file_text.replace("\n","")
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)

        patterns = [
            '<%ifuser_signed_in\?%><%if.+?==.+?%>.+?編集.+?削除.+?<%else%>.+?購入.+?<%end%>',
            '<%ifuser_signed_in\?&&.+?==.+?%>.+?編集.+?削除.+?<%end%><%ifuser_signed_in\?&&.+?!=.+?%>.+?購入.+?<%end%>',
            '<%ifuser_signed_in\?&&.+?==.+?%>.+?編集.+?削除.+?<%elsifuser_signed_in\?&&.+?!=.+?%>.+?購入.+?<%end%>',
            '<%ifuser_signed_in\?&&.+?==.+?%>.+?編集.+?削除.+?<%elsifuser_signed_in\?%>.+?購入.+?<%end%>'
        ]
        for pattern in patterns:
            if re.search(pattern, file_text):
                break
        else:
            errors.append(MESSAGES["incollect_btn_method"])
    
        if not "<%='配送料負担'%>" in file_text:
            partial_text = re.search("<spanclass='item-postage'>.+?</span>",file_text)
            if partial_text == None: 
                errors.append(MESSAGES["stop_name_check_postage"])
            else:
                partial_text = partial_text.group()
                if not ".name" in partial_text: errors.append(MESSAGES["incollect_postage"])

        __check_detail('カテゴリー', file_text, errors, warnings)
        __check_detail('商品の状態', file_text, errors, warnings)
        __check_detail('配送料の負担', file_text, errors, warnings)
        __check_detail('発送元の地域', file_text, errors, warnings)
        __check_detail('発送日の目安', file_text, errors, warnings)

        if not "<ahref='#'class='another-item'><%='商品のカテゴリー名'%>をもっと見る</a>" in file_text:
            partial_text = re.search("<ahref='#'class='another-item'>.+?をもっと見る</a>",file_text)
            if partial_text == None: 
                errors.append(MESSAGES["stop_name_check_category"])
            else:
                partial_text = partial_text.group()
                if not ".name" in partial_text: warnings.append(MESSAGES["incollect_category"])

        if "ログインしているユーザーと出品しているユーザーが、同一人物の場合と同一人物ではない場合で、処理を分けましょう" in raw_text or "詳細ページで表示されている商品のカテゴリー名を表示しましょう" in raw_text : 
            errors.append("実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。")

        if not ("¥" in file_text or "円" in file_text): 
            warnings.append(MESSAGES["no_yen"])
    return [errors,warnings]

def check_routes(driver):
    errors = []
    warnings = []
    MESSAGES = {
        "no_changes": "詳細のルーティングの変更点が見つかりません",
        "no_show_route": "出品に対するルーティングが見つかりません"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        warnings.append(MESSAGES["no_changes"])
    else:
        if not ("resources:items" in file_text or "resources:products" in file_text): errors.append(MESSAGES["no_show_route"])
        else:
            if "only:" in file_text and not ":show" in file_text: errors.append(MESSAGES["no_show_route"])
    return [errors,warnings]

def check_others(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/application_controller.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        pass
    else:
        if "authenticate_user!" in file_text: errors.append("authenticate_user!がapplication_controllerに指定されています")
    
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and (contains(@title,'new.html.erb') or contains(@title,'create.html.erb') or contains(@title,'edit.html.erb') or contains(@title,'update.html.erb') or contains(@title,'destroy.html.erb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append("indexとshow以外のビューファイルに編集が加えられています")
    return [errors,warnings]

def __check_detail(item_name, file_text, errors, warnings):
    if f"<tdclass='detail-value'><%='{item_name}'%></td>" in file_text:
        errors.append(f"{item_name}が設定がされてません")
    else:
        partial_text = re.search(f"<thclass='detail-item'>{item_name}</th>.+?</tr>", file_text)
        if partial_text is None:
            errors.append(f"不要な編集が加えられているため{item_name}に.nameがついているかのチェックを中断しました")
        else:
            if not ".name" in partial_text.group():
                warnings.append(f"{item_name}に対して.nameがついていません")