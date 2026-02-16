from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text, check_text, auth_check, check_comment
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
    NECESSARY_TEXT = {
    }
        
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "find(params[:id])": {"error": True, "num":1, "method":"over", "message": "findメソッドがまとめられていません\m◎findメソッドが複数箇所で使用されている為、beforeアクションでまとめましょう。\n\n■理由\n可読性向上の為です。\nまた保守（修正作業など）が発生した際も手を加えやすくなります。"}
    }
        
    # その他の複雑な指摘
    MESSAGES = { 
        "incollect_private_method": "商品インスタンスを定義するprivateメソッドに他の処理も記載されています（showアクションに影響を及ぼしている可能性があります）",
        "no_move_toppage_method": "出品者以外がトップページに遷移する条件式がeditアクション内に見つかりません（editアクション外で定義されていれば問題ありません　）\m◎editアクションに「出品者のみが編集できる」条件分岐を実装しましょう。\n\n■理由\n「ログイン状態のユーザーであっても、URLを直接入力して出品していない商品の商品情報編集ページへ遷移しようとすると、トップページに遷移すること」という実装条件を満たす為です。",
        "unnecessary_move_toppage_method": "出品者以外がトップページに遷移する条件式がコントローラ内に二つ以上見つかりました",
        "no_edit_action": "editアクションが定義されていません\m◎editアクションが見当たらない為追加しましょう。\n\n■理由\n商品編集機能に必要なアクションの為です。",
        "no_update_action": "updateアクションが定義されていません\m◎updateアクションが見当たらない為追加しましょう。\n\n■理由\n商品編集機能に必要なアクションの為です。",
        "no_update_method": "updateアクション内にupdateメソッドの処理が見つかりません\m◎updateアクションを見直し、updateアクション内にupdateメソッドが使われているか確認しましょう。\n\n■理由\n「エラーハンドリングができること（入力に問題がある状態で「変更する」ボタンが押された場合、情報は保存されず、編集ページに戻りエラーメッセージが表示されること）。」という実装条件を満たす為です。",
        "no_error_handle": "updateメソッドに対してif文によるエラーハンドリングが実装されていません\m◎updateアクション内に更新可否の条件式が実装できているか確認しましょう。\n\n■理由\n「エラーハンドリングができること（入力に問題がある状態で「変更する」ボタンが押された場合、情報は保存されず、編集ページに戻りエラーメッセージが表示されること）。」という実装条件を満たす為です。",
        "no_redirect": "updateアクションに保存成功時詳細ページにリダイレクトする記述が見つかりません\m◎更新が完了した際の遷移先を確認しましょう。updateアクションを見直しましょう。\n\n■理由\n「編集が完了したら、商品詳細表示ページに遷移し、変更された商品情報が表示されること。」という実装条件を満たす為です。",
        "no_render": "updateアクションに保存失敗にeditのテンプレートを呼び出す記述が見つかりません\m◎更新が失敗した際の遷移先について確認しましょう。\n\n■理由\n「エラーハンドリングができること（入力に問題がある状態で「変更する」ボタンが押された場合、情報は保存されず、編集ページに戻りエラーメッセージが表示されること）。」という実装条件を満たす為です。"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/') and contains(@title,'_controller.rb') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,False,False,True) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        auth_check(file_text,"edit",errors,warnings)

        file_text = re.sub('\n','',file_text)
        if file_text.count('find(params[:id])') == 1 and not re.search('find\(params\[:id\]\)end',file_text): 
            errors.append(MESSAGES["incollect_private_method"])
        
        patterns = [
            'if.+?==.+?\nrender:edit',
            'if.+?==.+?\nelse',
            'if.+?!=.+?\nredirect_toroot_path',
            'if.+?!=.+?\nredirect_toaction::index',
            'returnif.+?==.+?\n',
            'redirect_toroot_pathif.+?!=.+?\n',
            'redirect_toaction::indexif.+?!=.+?\n',
            'unless.+?==.+?\nredirect_toroot_path',
            'unless.+?==.+?\nredirect_toaction::index',
            'unless.+?==.+?\nredirect_toredirect_toaction::index',
            'unless.+?!=.+?\nrender:edit',
            'unless.+?!=.+?\nelse',
            'returnunless.+?!=.+?\n',
            'redirect_toroot_pathunless.+?==.+?\n',
            'redirect_toaction::indexunless.+?==.+?\n',
            'redirect_toredirect_toaction::indexunless.+?==.+?\n'
        ]
        match_found = any(re.search(pattern, raw_text) for pattern in patterns)
        if not match_found:
            errors.append(MESSAGES["no_move_toppage_method"])

        if (file_text.count('!=') + file_text.count('==')) >= 2:  
            errors.append(MESSAGES["unnecessary_move_toppage_method"])
        edit_text = re.search('defedit.+?end',file_text)
        if edit_text == None: 
            errors.append(MESSAGES["no_edit_action"])
        
        update_text = re.search('defupdate.+?endend',file_text)
        if update_text == None: 
            errors.append(MESSAGES["no_update_action"])
        else:
            update_text = update_text.group()
            update_instance_text = re.search('\@.+\.update',update_text)
            if update_instance_text == None: 
                errors.append(MESSAGES["no_update_method"])
            if not re.search('if.+update.+else.+?endend',update_text):
                if not re.search('if.+valid.+else.+?endend',update_text):
                    errors.append(MESSAGES["no_error_handle"])
            else:
                if_text = re.search('if.+?else',update_text).group()
                if not ("redirect_toaction::show" in if_text or "redirect_toitem_path" in if_text or "redirect_toproduct_path" in if_text): errors.append(MESSAGES["no_redirect"])
                else_text = re.search('else.+?endend',update_text).group()
                if not ("render:edit" in else_text or "render'edit'"in else_text): errors.append(MESSAGES["no_render"])
    return [errors,warnings]

def check_edit_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "hoge" : {"error": True, "message": "フォーム内にhogeが残っています。\m◎フォーム内に未実装項目がないか確認しましょう。\n\n■理由\nフォーム内に未実装のhogeが残っている為です。"},
        "<%=link_to'もどる',root_path,class:'back-btn'%>" : {"error": True, "message": "「もどる」ボタンのリンク先がトップページになっています\m◎「もどる」ボタンのリンク先をトップページから商品詳細ページに変更しましょう。\n\n■理由\n「ページ下部の「もどる」ボタンを押すと、編集途中の情報は破棄され、商品詳細表示ページに遷移すること。」という実装条件を満たす為です。"},
        "<%=link_to'もどる',:back,class:'back-btn'%>" : {"error": True, "message": "「もどる」ボタンのリンク先が:backになっています(指摘必須）\m「もどる」ボタンのリンク先を:backから商品詳細ページに変更しましょう。\n\n■理由\n:backですと例えばトップページからURL指定で編集画面に遷移した場合、もどるボタンで詳細ページではなくトップページに遷移してしまい以下要件を満たさなくなってしまう為です。\n\n「ページ下部の「もどる」ボタンを押すと、編集途中の情報は破棄され、商品詳細表示ページに遷移すること。」"}
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
        "incollect_form_with_model": "form_withにmodel指定がされていません\m◎form_withのモデルオプションに、コントローラーで定義したインスタンス変数を定義しましょう。\n\n■理由\n「商品名やカテゴリーの情報など、すでに登録されている商品情報は、商品情報編集画面を開いた時点で表示されること（商品画像・販売手数料・販売利益に関しては、表示されない状態で良い）。」という実装条件を満たす為です。",
        "no_render_error_message": "_error_messagesをrenderする記述が見つかりません\m◎エラーメッセージを表示できるようにしましょう。\n\n■理由\n「エラーハンドリングができること（入力に問題がある状態で「変更する」ボタンが押された場合、情報は保存されず、編集ページに戻りエラーメッセージが表示されること）。」という実装条件を満たす為です。",
        "incollect_back_btn": "「もどる」ボタンが破損している可能性があります\m◎「もどる」ボタンを確認しましょう。\n\n■理由\n「ページ下部の「もどる」ボタンを押すと、編集途中の情報は破棄され、商品詳細表示ページに遷移すること。」という実装条件を満たす為です。"
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'edit.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        errors = check_comment(raw_text,errors)
        
        if not ("<%=form_withmodel:@" in file_text or "<%=form_with(model:@" in file_text) :
            errors.append(MESSAGES["incollect_form_with_model"])
        if not ("<%=render'shared/error_messages'" in file_text or "<%=renderpartial:'shared/error_messages'" in file_text): 
            errors.append(MESSAGES["no_render_error_message"])

        if not (("<%=link_to'もどる',root_path,class:'back-btn'%>" in file_text or "<%=link_to'もどる',:back,class:'back-btn'%>" in file_text) or \
        ("<%=link_to'もどる',item_path" in file_text or "<%=link_to'もどる',product_path" in file_text)):
            errors.append(MESSAGES["incollect_back_btn"])
    return [errors,warnings]

def check_show_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'show.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした(編集ボタンのリンクが実装されていない可能性があります)詳細ページの編集ボタンのリンクが実装されていません\m◎詳細ページの「商品の編集」ボタンのリンク先を実装できているか確認しましょう。\n\n■理由\n「ログイン状態の場合は、自身が出品した販売中商品の商品情報編集ページに遷移できること。」という実装条件を満たす為です。")
    else:
        if "<%= link_to'商品の編集','#',method::get,class:'item-red-btn'%>" in file_text: errors.append("詳細ページの編集ボタンのリンクが実装されていません\m◎詳細ページの「商品の編集」ボタンのリンク先を実装しましょう。\n\n■理由\n「ログイン状態の場合は、自身が出品した販売中商品の商品情報編集ページに遷移できること。」という実装条件を満たす為です。")
        if not "'削除','#'" in file_text: errors.append("削除ボタンのリンク先が編集されています")
        if not "'購入画面に進む','#'" in file_text: errors.append("購入ボタンのリンク先が編集されています")
    return [errors,warnings]

def check_routes(driver):
    errors = []
    warnings = []
    MESSAGES = {
        "no_changes": "編集のルーティングの変更点が見つかりません\m◎editやupdateのルーティングがあるか確認しましょう。\n\n■理由\nコントローラやビューを使用できるようにするためです。",
        "no_edit_route": "編集のルーティングが見つかりません\m◎editやupdateのルーティングがあるか確認しましょう。\n\n■理由\nコントローラやビューを使用できるようにするためです。"
    }
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        warnings.append(MESSAGES["no_changes"])
    else:
        if not ("resources:items" in file_text or "resources:products" in file_text): errors.append(MESSAGES["no_edit_route"])
        else:
            if "only:" in file_text and not ":edit,:update" in file_text: errors.append(MESSAGES["no_edit_route"])

    return [errors,warnings]

def check_others(driver):
    errors = []
    warnings = []
    MESSAGES = {
        "incollect_error_messages": "_error_mssages.html.erbに編集が加えられています\m◎エラーメッセージを表示できるようにしている「_error_emssages.html.erb」に誤って編集がされている可能性があります。もう一度確認しましょう。\n\n■理由\n「エラーハンドリングができること（入力に問題がある状態で「変更する」ボタンが押された場合、情報は保存されず、編集ページに戻りエラーメッセージが表示されること）。」という実装条件を満たす為です。"
    }
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'app/views/shared/_error_messages.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append(MESSAGES["incollect_error_messages"])
    return [errors,warnings]